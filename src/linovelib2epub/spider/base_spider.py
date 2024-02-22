import asyncio
import os
import pickle
import re
import time
from abc import ABC, abstractmethod
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable, Optional, Callable, Awaitable, Union, Dict, Any, List

import aiofiles
import aiohttp as aiohttp
import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError

from ..exceptions import LinovelibException
from ..logger import Logger
from ..models import LightNovel, LightNovelImage, LightNovelVolume, LightNovelChapter, CatalogMasiroVolume, \
    CatalogBaseVolume
from ..utils import (check_image_integrity, create_folder_if_not_exists,
                     is_async, is_valid_image_url)

# IMAGE_DOWNLOAD_STRATEGY
MULTIPROCESSING = 'MULTIPROCESSING'
MULTITHREADING = 'MULTITHREADING'
ASYNCIO = 'ASYNCIO'


class BaseNovelWebsiteSpider(ABC):

    def __init__(self, spider_settings: Dict[str, Any]) -> None:
        self.spider_settings = spider_settings
        self.logger = Logger(logger_name=type(self).__name__,
                             logger_level=self.spider_settings["log_level"],
                             log_filename=self.spider_settings["log_filename"]).get_logger()

        # in base class, http session is bare
        self.session = requests.session()

        self.FETCH_CHAPTER_CONCURRENCY_LEVEL = 2

    @abstractmethod
    def fetch(self) -> LightNovel:
        raise NotImplementedError("Note: subclass must implement this method to do real fetch logic.")

    def request_headers(self) -> Dict[str, Any]:
        """
        Act as a common headers, 这个方法目前在base class中的用例为：下载图片时的默认请求头。
        :return:
        """
        return {}

    def download_images_by_multiprocessing(self, light_novel_images: List[LightNovelImage]) -> None:

        self.logger.info(f'len of light_novel_images = {len(light_novel_images)}')

        download_url_to_image: Dict[str, LightNovelImage] = {
            image.download_url: image for image in light_novel_images
        }
        params = [(image.download_url, image.local_relative_path) for image in light_novel_images]

        with Pool(processes=os.cpu_count() or 4) as process_pool:
            error_links = process_pool.starmap(self._download_image_legacy, params)

            while sorted_error_links := list(filter(None, error_links)):
                self.logger.info('Some errors occurred when download images. Retry those links that failed to request.')
                self.logger.info(f'Retry image links: {sorted_error_links}')
                params = [(url, download_url_to_image[url].local_relative_path) for url in sorted_error_links]
                error_links = process_pool.starmap(self._download_image_legacy, params)

    def _download_image_legacy(self, download_url: str, local_relative_path: str) -> Optional[str]:
        """
        If a image url download failed, return its url(for retry). else return None.

        :param download_url: single url string
        :return: original url if failed, or None if succeeded.
        """
        if not is_valid_image_url(download_url):
            return None

        save_path = f"{self.spider_settings['image_download_folder']}/{local_relative_path}"
        create_folder_if_not_exists(os.path.dirname(save_path))

        filename_path = Path(save_path)
        if filename_path.exists():
            return None

        # url is valid and never downloaded
        try:
            resp = self.session.get(download_url, headers=self.request_headers(),
                                    timeout=self.spider_settings['http_timeout'])

            expected_length = resp.headers and resp.headers.get('Content-Length')
            actual_length = resp.raw.tell()
            check_image_integrity(expected_length, actual_length)
        except (Exception, ProxyError,) as e:
            # SAD PATH
            return download_url
        else:
            try:
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                # HAPPY PATH
                return None
            except (Exception,):
                # SAD PATH
                return download_url

    async def download_images_by_asyncio(self, light_novel_images: List[LightNovelImage]) -> None:
        self.logger.info(f'len of light_novel_images= {len(light_novel_images)}')

        download_url_to_image: Dict[str, LightNovelImage] = {
            image.download_url: image for image in light_novel_images
        }

        async with aiohttp.ClientSession() as session:
            tasks = {asyncio.create_task(self._download_image(session,
                                                              image.download_url,
                                                              image.local_relative_path),
                                         name=image.download_url)
                     for image in light_novel_images}
            pending: set = tasks
            succeed_count = 0

            while pending:
                done, pending = await asyncio.wait(pending, return_when=asyncio.ALL_COMPLETED)
                # Note: This does not raise TimeoutError! Futures that aren't done when the timeout occurs
                # are returned in the second set

                # 1. succeed => normal result in done(# HAPPY CASE)
                # 2. Timeout => No TimeoutError, put timeout tasks in pending(SAD CASE(need retry))
                # 3  Other Exception before timeout => (SAD CASE(need retry)

                for done_task in done:
                    exception = done_task.exception()
                    task_url = done_task.get_name()

                    if exception is None:
                        # result = done_task.result()
                        succeed_count += 1
                    else:
                        # [TEST]make connect=.1 to reach this branch, should retry all the urls that entered this case
                        self.logger.error(
                            f'Exception: {exception.__class__.__name__} | FAIL: {task_url}; should retry.')
                        pending.add(asyncio.create_task(
                            self._download_image(session, task_url,
                                                 download_url_to_image[task_url].local_relative_path),
                            name=task_url))

                self.logger.info(f'SUCCEED_COUNT: {succeed_count}')
                self.logger.info(f'[NEXT TURN]Pending task count: {len(pending)}')

    async def _download_image(self, session: ClientSession, download_url: str, local_relative_path: str) -> None:
        if not is_valid_image_url(download_url):
            return

        save_path = f"{self.spider_settings['image_download_folder']}/{local_relative_path}"
        create_folder_if_not_exists(os.path.dirname(save_path))

        filename_path = Path(save_path)
        if filename_path.exists():
            self.logger.info(f"The image to download is already downloaded at {filename_path}.skip.")
            return

        timeout = aiohttp.ClientTimeout(total=30, connect=15)  # per request timeout
        async with session.get(download_url, headers=self.request_headers(), timeout=timeout) as resp:
            if resp.status < 400:
                image = await resp.read()

                # check image integrity here, if get partial, MUST raise error
                expected_get = resp.headers.get('Content-Length')
                actual_get = len(image)
                self.logger.debug(f'check_image_integrity: expected_get:{expected_get} vs actual_get: {actual_get}')
                check_image_integrity(expected_get, actual_get)

                # write file, maybe raise IO error
                async with aiofiles.open(save_path, mode='wb') as afp:
                    await afp.write(image)
                    self.logger.info(f'image url {download_url} => local relative path {save_path} ok.')
            else:
                # maybe 404 etc. Now ignore it, don't raise error to avoid retry dead loop
                pass

    def post_fetch(self, novel: LightNovel) -> None:
        self._save_novel_pickle(novel)

        start = time.perf_counter()
        self._process_image_download(novel)
        self.logger.info('(Perf metrics) Download Images took: {} seconds'.format(time.perf_counter() - start))

    def _process_image_download(self, novel: LightNovel) -> None:
        create_folder_if_not_exists(self.spider_settings["image_download_folder"])

        strategy_to_method = {
            MULTIPROCESSING: self.download_images_by_multiprocessing,
            ASYNCIO: self.download_images_by_asyncio,
            # add more
        }
        _download_image: Callable[[Iterable], Union[None, Awaitable[None]]] = strategy_to_method.get(
            self.spider_settings['image_download_strategy'],
            self.download_images_by_asyncio)

        self.logger.info(f"Image download strategy: {self.spider_settings['image_download_strategy']}")

        if self.spider_settings['has_illustration']:
            image_list: List[LightNovelImage] = novel.get_illustrations()
            image_list.append(novel.book_cover)
        else:
            image_list: List[LightNovelImage] = [novel.book_cover]

        self.logger.info(f"len of image list: {len(image_list)}")

        if is_async(_download_image):
            asyncio.run(_download_image(image_list))
        else:
            _download_image(image_list)

    def _save_novel_pickle(self, novel):
        create_folder_if_not_exists(self.spider_settings["pickle_temp_folder"])
        pickle_save_path = self.spider_settings['novel_pickle_path']
        with open(pickle_save_path, 'wb') as fp:
            pickle.dump(novel, fp)

    async def download_pages(self, session: Any, page_url_set: set) -> Dict[str, str]:

        self.logger.info(f'page url set = {len(page_url_set)}')

        url_to_page = {url: 'NOT_DOWNLOAD_READY' for url in page_url_set}

        # use semaphore to control concurrency
        max_concurrency = self.FETCH_CHAPTER_CONCURRENCY_LEVEL
        semaphore = asyncio.Semaphore(max_concurrency)

        self.logger.info(f'DOWNLOAD_PAGES concurrency level: {max_concurrency}.')

        async with session:
            tasks = {asyncio.create_task(self._download_page(session, semaphore, url), name=url) for url in
                     page_url_set}
            pending: set = tasks
            succeed_count = 0

            while pending:
                done, pending = await asyncio.wait(pending, return_when=asyncio.ALL_COMPLETED)
                # Note: This does not raise TimeoutError! Futures that aren't done when the timeout occurs
                # are returned in the second set

                # 1. succeed => normal result in done(# HAPPY CASE)
                # 2. Timeout => No TimeoutError, put timeout tasks in pending(SAD CASE(need retry))
                # 3  Other Exception before timeout => (SAD CASE(need retry)

                for done_task in done:
                    exception = done_task.exception()
                    task_url = done_task.get_name()

                    if exception is None:
                        url_to_page[task_url] = done_task.result()
                        succeed_count += 1
                    else:
                        # [TEST]make connect=.1 to reach this branch, should retry all the urls that entered this case
                        self.logger.error(
                            f'Exception: {exception.__class__.__name__} | FAIL: {task_url}; should retry.')
                        pending.add(
                            asyncio.create_task(self._download_page(session, semaphore, task_url), name=task_url))

                self.logger.info(f'SUCCEED_COUNT: {succeed_count}')
                self.logger.info(f'[NEXT TURN]Pending task count: {len(pending)}')

        # ASSERTION: make sure data is ok.
        for page_content in url_to_page.values():
            if page_content == "NOT_DOWNLOAD_READY":
                raise LinovelibException(
                    ' 如果这个断言被触发，那么证明代码逻辑有问题。青春猪头少年不会梦到奇奇怪怪的 BUG。')

        return url_to_page

    async def _download_page(self, session, semaphore, url) -> str | None:
        async with semaphore:
            timeout = aiohttp.ClientTimeout(total=30, connect=15)  # per request timeout
            async with session.get(url, headers=self.request_headers(), timeout=timeout) as resp:
                if resp.status == 200:
                    self.logger.info(f'page {url} 200 => ok.')
                    return await resp.text()
                elif resp.status == 404:
                    # maybe 404 etc. Now ignore it, don't raise error to avoid retry dead loop
                    # 404 is considered as success => don't retry
                    self.logger.error(f'page {url} 404 => skip it.')
                    pass
                else:
                    # 429 too many requests => should retry
                    if resp.status == 429:
                        # 更好的做法：y=2^x 指数退化规避，目前的线性常数 C 退化效果很差
                        await asyncio.sleep(1)
                    # 503 Service Unavailable => should retry
                    # ...... => should retry
                    self.logger.error(f'page {url} {resp.status} => should retry.')
                    raise LinovelibException(f'fetch page url {url} failed with error status {resp.status}.')

    async def fetch_chapters(self, session: Any, catalog_list: List[CatalogBaseVolume], book):
        """
        A basic implementation for crawling chapters.
        Please consider overriding `extract_body_content()` and `download_pages` in subclass instance.
        :param session:
        :param catalog_list:
        :param book:
        :return:
        """
        page_url_set = {chapter.chapter_url for volume in catalog_list for chapter in volume.chapters}
        url_to_page = await self.download_pages(session, page_url_set)

        # TODO 下面这部分代码提取到单独的func，不涉及网络请求，只是HTML解构解析

        #  Main goals:
        #  1. extract body and update dict
        #  2. update image src to local file path in body content,
        #  3. generate illustration_dict.

        for url, page in url_to_page.items():
            url_to_page[url] = self.extract_body_content(page)

        volume_id = 0
        for catalog_volume in catalog_list:
            volume_id += 1
            new_volume = LightNovelVolume(volume_id=volume_id)
            new_volume.title = catalog_volume.volume_title

            self.logger.info(f'volume: {catalog_volume.volume_title}')

            chapter_id = -1
            chapter_list: List[LightNovelChapter] = []  # store chapters
            for catalog_chapter in catalog_volume.chapters:
                chapter_id += 1
                chapter_title = catalog_chapter.chapter_title

                linovel_chapter = LightNovelChapter(chapter_id=chapter_id)
                linovel_chapter.title = chapter_title
                chapter_illustrations: List[LightNovelImage] = []

                self.logger.info(f'chapter : {chapter_title}')

                chapter_url = catalog_chapter.chapter_url
                chapter_body = url_to_page[chapter_url]

                # one page per chapter
                images_soup = BeautifulSoup(chapter_body, 'lxml').find_all('img')
                for _, image in enumerate(images_soup):
                    # Images src analysis:
                    # https://i.ibb.co/1fRfdhs/6f9fbd2762d0f7039cfafb8d0bfa513d2797c5a0.jpg
                    # https://masiro.moe/data/attachment/forum/202103/07/173827oqkmqhcbylyytty9.jpg => 526 status code
                    # https://www.masiro.me/images/encode/fy-221114012533-99Qz.jpg

                    # 可能为站内链接，也可能是站外链接。因为 url 没有固定格式
                    # 这里我们需要自定义一个中间的文件夹名称，用于分割不同的爬虫实例。
                    # 为了让文件夹名称更加可读和具有语义，这里使用 bookid-volumeid 作为隔离。

                    # 举例，例如 bookid 为 875，volume_id 取本地自增 id(例如 3)，那么 875-3 就是结果。
                    # 最后，将这个分隔符和图片原来的文件名拼接，得到 875-3/fy-221114012533-99Qz.jpg 这样格式的链接。
                    # 更加具体地，为 XXXX/masiro.me/875-3/fy-221114012533-99Qz.jpg

                    remote_src = image.get("src")
                    src_value = re.search('(?<= src=").*?(?=")', str(image))

                    light_novel_image = LightNovelImage(related_page_url=chapter_url,
                                                        remote_src=remote_src,
                                                        chapter_id=chapter_id,
                                                        volume_id=volume_id,
                                                        book_id=self.spider_settings['book_id'])

                    image_local_src = f'{self.spider_settings["image_download_folder"]}/{light_novel_image.local_relative_path}'
                    new_image = str(image).replace(str(src_value.group()), image_local_src)
                    chapter_body = chapter_body.replace(str(image), new_image)
                    chapter_illustrations.append(light_novel_image)

                    self.logger.info(f'Processing page... {chapter_url}')

                linovel_chapter.content = chapter_body
                linovel_chapter.illustrations = chapter_illustrations
                chapter_list.append(linovel_chapter)

            for linovel_chapter in chapter_list:
                new_volume.add_chapter(cid=linovel_chapter.chapter_id, title=linovel_chapter.title,
                                       content=linovel_chapter.content, illustrations=linovel_chapter.illustrations)

            book.add_volume(vid=new_volume.volume_id, title=new_volume.title, chapters=new_volume.chapters)

        book.mark_volumes_content_ready()

    def extract_body_content(self, page):
        """
        return the whole html page content as a chapter of one volume, you need to override it to extract what you need.
        :param page:
        :return:
        """
        return page

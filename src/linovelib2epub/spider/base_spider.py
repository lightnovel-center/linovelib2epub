import asyncio
import os
import pickle
import time
from abc import ABC, abstractmethod
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable, Optional

import aiofiles
import aiohttp as aiohttp
from aiohttp import ClientSession
from requests.exceptions import ProxyError

from ..logger import Logger
from ..models import LightNovel
from ..utils import (check_image_integrity, create_folder_if_not_exists,
                     is_async, is_valid_image_url)

# IMAGE_DOWNLOAD_STRATEGY
MULTIPROCESSING = 'MULTIPROCESSING'
MULTITHREADING = 'MULTITHREADING'
ASYNCIO = 'ASYNCIO'


class BaseNovelWebsiteSpider(ABC):

    def __init__(self, spider_settings: Optional[dict] = None):
        self.spider_settings = spider_settings
        self.logger = Logger(logger_name=self.__class__.__name__,
                             log_filename=self.spider_settings["log_filename"]).get_logger()

    @abstractmethod
    def fetch(self) -> LightNovel:
        raise NotImplementedError()

    def request_headers(self, referer: str = '', random_ua: bool = True) -> dict:
        default_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
        default_referer = 'https://w.linovelib.com'
        headers = {
            'referer': referer if referer else default_referer,
            'user-agent': self.spider_settings['random_useragent'] if random_ua else default_ua
        }
        return headers

    def download_images_by_multiprocessing(self, urls: Iterable = None) -> None:
        if urls is None:
            urls = set()
        else:
            urls = set(urls)

        self.logger.info(f'len of image set = {len(urls)}')

        process_pool = Pool(processes=os.cpu_count() or 4)
        error_links = process_pool.map(self._download_image_legacy, urls)

        while sorted_error_links := list(filter(None, error_links)):
            self.logger.info('Some errors occurred when download images. Retry those links that failed to request.')
            self.logger.info(f'Retry image links: {sorted_error_links}')
            error_links = process_pool.map(self._download_image_legacy, sorted_error_links)

        # downloading image: https://img.linovelib.com/0/682/117082/50748.jpg to [folder]/0-682-117082-50748.jpg
        # re-check image download result:
        # - happy result: urls_set - self.image_download_folder == 0
        # - ? result: urls_set - self.image_download_folder < 0 , maybe you put some other images in this folder.
        # - bad result: urls_set - self.image_download_folder > 0

        download_image_miss_quota = len(urls) - sum([len(files) for root, dirs, files in os.walk(self.spider_settings['image_download_folder'])])
        self.logger.info(f'download_image_miss_quota: {download_image_miss_quota}. Quota <=0 is ok.')
        if download_image_miss_quota <= 0:
            self.logger.info('The result of downloading pictures is perfect.')
        else:
            self.logger.warn('Some pictures to download are missing. Maybe this is a bug. You can Retry.')

    def _download_image_legacy(self, url: str) -> Optional[str]:
        """
        If a image url download failed, return its url(for retry). else return None.

        :param url: single url string
        :return: original url if failed, or None if succeeded.
        """
        if not is_valid_image_url(url):
            return

        filename = self.get_image_filename(url)
        save_path = f"{self.spider_settings['image_download_folder']}/{filename}"
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))

        filename_path = Path(save_path)
        if filename_path.exists():
            return

        # url is valid and never downloaded
        try:
            resp = self.session.get(url, headers=self.request_headers(), timeout=self.spider_settings['http_timeout'])

            expected_length = resp.headers and resp.headers.get('Content-Length')
            actual_length = resp.raw.tell()
            check_image_integrity(expected_length, actual_length)
        except (Exception, ProxyError,) as e:
            # SAD PATH
            return url
        else:
            try:
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                # HAPPY PATH
            except (Exception,):
                # SAD PATH
                return url

    async def download_images_by_asyncio(self, urls: Iterable = None):
        if urls is None:
            urls = set()
        else:
            urls = set(urls)

        self.logger.info(f'len of image set = {len(urls)}')

        async with aiohttp.ClientSession() as session:
            requests = {asyncio.create_task(self._download_image(session, url), name=url) for url in urls}
            pending: set = requests
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
                        self.logger.info(f'Exception: {type(exception)}')
                        self.logger.info(f'FAIL: {task_url}; should retry this url.')
                        pending.add(asyncio.create_task(self._download_image(session, task_url), name=task_url))

                self.logger.info(f'SUCCEED_COUNT: {succeed_count}')
                self.logger.info(f'[NEXT TURN]Pending task count: {len(pending)}')

    async def _download_image(self, session: ClientSession, url: str) -> None:
        if not is_valid_image_url(url):
            return

        filename = self.get_image_filename(url)
        save_path = f"{self.spider_settings['image_download_folder']}/{filename}"
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))

        filename_path = Path(save_path)
        if filename_path.exists():
            self.logger.info(f"The image to download is alreay downloaded at {filename_path}.skip.")
            return

        timeout = aiohttp.ClientTimeout(total=30, connect=15)  # per request timeout
        async with session.get(url, headers=self.request_headers(), timeout=timeout) as resp:
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
                    self.logger.info(f'save image: {url} ok.')
            else:
                # maybe 404 etc. Now ignore it, don't raise error to avoid retry dead loop
                pass

    def post_fetch(self, novel: LightNovel):
        self._save_novel_pickle(novel)

        start = time.perf_counter()
        self._process_image_download(novel)
        self.logger.info('(Perf metrics) Download Images took: {} seconds'.format(time.perf_counter() - start))

    def _process_image_download(self, novel):
        create_folder_if_not_exists(self.spider_settings["image_download_folder"])

        strategy_to_method = {
            MULTIPROCESSING: self.download_images_by_multiprocessing,
            ASYNCIO: self.download_images_by_asyncio,
            # add more
        }
        _download_image = strategy_to_method.get(self.spider_settings['image_download_strategy'],
                                                 self.download_images_by_asyncio)

        self.logger.info(f"Image download strategy: {self.spider_settings['image_download_strategy']}")

        if self.spider_settings['has_illustration']:
            image_set = novel.get_illustration_set()
            image_set.add(novel.book_cover)
        else:
            image_set = {novel.book_cover}

        if is_async(_download_image):
            asyncio.run(_download_image(image_set))
        else:
            _download_image(image_set)

    def _save_novel_pickle(self, novel):
        with open(self.spider_settings['novel_pickle_path'], 'wb') as fp:
            pickle.dump(novel, fp)

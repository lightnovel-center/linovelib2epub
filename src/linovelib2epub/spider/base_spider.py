import asyncio
import os
import pickle
import time
from abc import ABC, abstractmethod
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable, Optional, Callable, Awaitable, Union, Dict, Any, List

import aiofiles
import aiohttp as aiohttp
import requests
from aiohttp import ClientSession
from requests.exceptions import ProxyError

from ..logger import Logger
from ..models import LightNovel, LightNovelImage
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
                             log_filename=self.spider_settings["log_filename"]).get_logger()

        # in base class, http session is bare
        self.session = requests.session()

    @abstractmethod
    def fetch(self) -> LightNovel:
        raise NotImplementedError("Note: subclass must implement this method to do real fetch logic.")

    def request_headers(self) -> Dict[str, Any]:
        """
        Act as a common headers, 这个方法的父类设计似乎作用有限，是不是可以去掉？
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
                        self.logger.info(f'Exception: {type(exception)}')
                        self.logger.info(f'FAIL: {task_url}; should retry this url.')
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
        with open(self.spider_settings['novel_pickle_path'], 'wb') as fp:
            pickle.dump(novel, fp)

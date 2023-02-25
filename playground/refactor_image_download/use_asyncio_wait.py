import asyncio
import logging
from typing import Iterable, Optional

import aiofiles
import aiohttp as aiohttp
from aiohttp import ClientSession
from linovelib2epub.logger import Logger
from linovelib2epub.utils import check_image_integrity

from utils import async_timed, get_image_urls


def get_external_logger():
    logger = Logger(logger_name='ExternalLogger', log_filename='ExternalLogger').get_logger()
    return logger


class MyLogger:

    def __init__(self):
        logger = logging.getLogger()
        fh = logging.FileHandler('use_asyncio_wait.log', encoding='utf-8', mode='w')
        stream_handler = logging.StreamHandler()
        logger.addHandler(fh)
        logger.addHandler(stream_handler)
        logger.setLevel(logging.INFO)
        self.logger = logger

    def get_logger(self):
        return self.logger


class MySpider:

    def __init__(self, logger):
        self.logger = logger

    async def download_image(self, session: ClientSession, url: str) -> None:
        timeout = aiohttp.ClientTimeout(total=30, connect=15)  # per request timeout
        async with session.get(url, timeout=timeout) as resp:
            if resp.status < 400:
                image = await resp.read()

                # check image integrity here, if get partial, MUST raise error
                expected_get = resp.headers.get('Content-Length')
                actual_get = len(image)
                self.logger.debug(f'check_image_integrity: expected_get:{expected_get} vs actual_get: {actual_get}')
                check_image_integrity(expected_get, actual_get)

                # write file, maybe raise IO error
                filename = './images/' + url.rsplit("/", 1)[-1]
                async with aiofiles.open(filename, mode='wb') as afp:
                    await afp.write(image)
                    self.logger.debug(f'image url: {url} writes file done.')
            else:
                # maybe 404 etc. Now ignore it, don't raise error to avoid retry dead loop
                pass

    @async_timed()
    async def download_images(self, urls: Iterable):
        async with aiohttp.ClientSession() as session:

            requests = {asyncio.create_task(self.download_image(session, url), name=url) for url in urls}
            pending: set = requests

            # 1 resps = await asyncio.gather(*requests)

            # 2 for finished_task in asyncio.as_completed(requests):
            #     logger.info(await finished_task)

            # 3 asyncio.wait

            succeed_count = 0

            while pending:
                # done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                # done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_EXCEPTION)
                done, pending = await asyncio.wait(pending, return_when=asyncio.ALL_COMPLETED)

                # Note: This does not raise TimeoutError! Futures that aren't done when the timeout occurs are returned in the second set

                # 1. succeed => normal result in done(# HAPPY CASE)
                # 2. Timeout => No TimeoutError, put timeout tasks in pending(SAD CASE(need retry))
                # 3  Other Exception before timeout => (SAD CASE(need retry)

                # self.logger.info(f'Done task count: {len(done)}')
                # self.logger.info(f'Pending task count: {len(pending)}')

                for done_task in done:
                    exception = done_task.exception()
                    task_url = done_task.get_name()

                    if exception is None:
                        # result = done_task.result()
                        succeed_count += 1
                    else:
                        # make connect=.1 to reach this branch, should retry all the urls that entered this case
                        # Done task count: 39
                        # Pending task count: 0
                        self.logger.info(f'Exception: {type(exception)}')
                        self.logger.info(f'FAIL: {task_url}; should retry this url.')
                        pending.add(asyncio.create_task(self.download_image(session, task_url), name=task_url))

                self.logger.info(f'SUCCEED_COUNT: {succeed_count}')
                self.logger.info(f'[NEXT TURN]Pending task count: {len(pending)}')


async def main():
    urls = set(get_image_urls())

    # logger = MyLogger().get_logger()
    logger = get_external_logger()

    spider = MySpider(logger)
    await spider.download_images(urls)


async def test_aiofiles():
    async with aiofiles.open('tmp.txt', mode='w') as afp:
        await afp.write('hello aiofiles')


if __name__ == '__main__':
    asyncio.run(main())
    # asyncio.run(test_aiofiles())

# 3x faster than multiprocessing approximately

# finished <function main at 0x0000017D4072F5B0> in 3.7227 second(s)
# finished <function main at 0x00000114625EF5B0> in 3.6460 second(s)
# finished <function main at 0x000002778B6CF5B0> in 4.6501 second(s)

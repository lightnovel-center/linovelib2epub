import asyncio
import logging
from typing import Iterable

import aiohttp as aiohttp
from aiohttp import ClientSession

from utils import async_timed, get_image_urls

logger = logging.getLogger()
fh = logging.FileHandler('use_asyncio_wait.log', encoding='utf-8', mode='w')
stream_handler = logging.StreamHandler()
logger.addHandler(fh)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

# @async_timed()
async def download_image(session: ClientSession, url: str) -> bytes:
    # per request timeout
    timeout = aiohttp.ClientTimeout(total=30, connect=15)
    async with session.get(url, timeout=timeout) as resp:
        if resp.status < 400:
            # TODO check image integrity here, if get partial, raise error
            image = await resp.read()
            return image
        else:
            # maybe 404 etc. Now ignore it, don't raise error to avoid retry dead loop
            pass


@async_timed()
async def download_images(urls: Iterable):
    async with aiohttp.ClientSession() as session:

        requests = {asyncio.create_task(download_image(session, url), name=url) for url in urls}
        pending: set = requests

        # 1 resps = await asyncio.gather(*requests)

        # 2 for finished_task in asyncio.as_completed(requests):
        #     logger.info(await finished_task)

        # 3 asyncio.wait: 这种方式不能很好地获取及时的下载反馈。因为请考虑 asyncio.as_completed()

        while pending:
            # 这个策略性能比ALL要稳定，也略好
            # test result(s): 14 16 26 41 47 => AVG 144/5 ≈ 30
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

            # Test result: 35 41 37 34 23 => AVG 170/5 = 34
            # done, pending = await asyncio.wait(pending, return_when=asyncio.ALL_COMPLETED)

            # Note: This does not raise TimeoutError! Futures that aren't done when the timeout occurs are returned in the second set

            # 1. succeed => normal result in done(# HAPPY CASE)
            # 2. Timeout => No TimeoutError, put timeout tasks in pending(SAD CASE(need retry))
            # 3  Other Exception before timeout => ? how to handle(SAD CASE(need retry)

            logger.info(f'Done task count: {len(done)}')
            logger.info(f'Pending task count: {len(pending)}')

            for done_task in done:
                exception = done_task.exception()
                task_url = done_task.get_name()

                if exception is None:
                    result = done_task.result()
                    # logger.info(f'SUCCEED: {task_url}; size: {len(result)}')
                    logger.info(f'SUCCEED: {task_url};')
                else:
                    # make connect=.1 to reach this branch, should retry all the urls that entered this case
                    # Done task count: 39
                    # Pending task count: 0
                    logger.info(f'Exception: {type(exception)}')
                    logger.info(f'FAIL: {task_url}; should retry this url.')
                    pending.add(asyncio.create_task(download_image(session, task_url), name=task_url))

            logger.info(f'[FINAL]Pending task count: {len(pending)}')


async def main():
    urls = get_image_urls()
    await download_images(urls)

    # async with aiofiles.open('./tmp.jpg', mode='wb') as afp:
    #     await afp.write(resps[0])
    #     logger.info('write file done.')


asyncio.run(main())

# 3x faster than multiprocessing approximately

# finished <function main at 0x0000017D4072F5B0> in 3.7227 second(s)
# finished <function main at 0x00000114625EF5B0> in 3.6460 second(s)
# finished <function main at 0x000002778B6CF5B0> in 4.6501 second(s)

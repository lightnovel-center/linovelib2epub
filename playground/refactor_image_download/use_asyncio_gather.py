import asyncio
import functools
import logging
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import requests

from utils import async_timed, get_image_urls

counter_lock = Lock()
counter: int = 0

logger = logging.getLogger(__name__)


def download_image(url: str) -> str:
    global counter
    try:
        resp = requests.get(url, headers={}, timeout=10)
        print(f'SUCCEED: {url} ; STATUS: {resp.status_code}')
        with counter_lock:
            counter = counter + 1
    except (Exception,) as e:
        # timeout or other exceptions
        print(f'FAIL: {e}')
        return url


async def reporter(request_count: int):
    while counter < request_count:
        print(f'Finished {counter}/{request_count} requests')
        await asyncio.sleep(.5)


@async_timed()
async def main():
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        image_urls = get_image_urls()
        image_url_set = set(image_urls)

        request_count = len(image_url_set)
        urls = [url for url in image_url_set]

        print('Image download progress...')
        reporter_task = asyncio.create_task(reporter(request_count))
        tasks = [loop.run_in_executor(pool, functools.partial(download_image, url)) for url in urls]

        while tasks:
            results = await asyncio.gather(*tasks)

            need_retry_urls = list(filter(None, results))
            print(f'Retry: {need_retry_urls}')
            tasks = [loop.run_in_executor(pool, functools.partial(download_image, url)) for url in need_retry_urls]

        await reporter_task


asyncio.run(main())

# benchmark: 20 27 22 38 19 19 21 24

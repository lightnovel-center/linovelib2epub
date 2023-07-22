import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, Optional

import requests
from requests.exceptions import ProxyError

from utils import (async_timed, get_image_urls, )


def download_images(urls: Iterable = None, pool_size=os.cpu_count()) -> None:
    if urls is None:
        urls = set()
    else:
        urls = set(urls)

    thread_pool = ThreadPoolExecutor(max_workers=int(pool_size))
    error_links = thread_pool.map(download_image, urls)

    while sorted_error_links := list(filter(None, error_links)):
        error_links = thread_pool.map(download_image, sorted_error_links)


def download_image(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, headers={}, timeout=10)
        print(f'url :{url} request succeeded. {resp.status_code}')
    except (Exception, ProxyError,) as e:
        # timeout 或者其他Exception都会走到这里。
        print(f'e: {e}')
        return url


@async_timed()
async def main():
    image_sets = set(get_image_urls())
    print(len(image_sets))
    # benchmark: 15 22 24 28 15 => AVG 20.8
    download_images(image_sets)


if __name__ == '__main__':
    asyncio.run(main())

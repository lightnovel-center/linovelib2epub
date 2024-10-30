import asyncio
from typing import Tuple

import requests

from linovelib2epub.logger import Logger
from linovelib2epub.utils import requests_get_with_retry

logger = Logger(logger_name=__name__,
                logger_level='DEBUG').get_logger()

url1 = "https://tw.linovelib.com/themes/zhmb/js/hm.js"
url2 = "https://tw.linovelib.com/themes/zhmb/js/readtool.js"
urls = [url1, url2]

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "cache-control": "max-age=0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
}


def fetch_with_retry(url) -> Tuple[str, str | None]:
    resp = requests_get_with_retry(requests, url, headers=headers, logger=logger)
    if resp:
        return url, resp.text

    return url, None


async def fetch_async(url, fetch_func):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetch_func, url)


async def fetch_js(urls):
    tasks = [asyncio.create_task(fetch_async(url, fetch_with_retry)) for url in urls]
    completed, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    for task in completed:
        url, resp_text = task.result()
        if resp_text:
            return url, resp_text

    # 没有任何一个url能返回文本
    return None, None


if __name__ == '__main__':
    url, text = asyncio.run(fetch_js(urls))
    print(url, text)

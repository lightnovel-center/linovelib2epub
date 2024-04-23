import asyncio

import aiohttp

from linovelib2epub.logger import Logger
from linovelib2epub.utils import aiohttp_get_with_retry

logger = Logger(logger_name=__name__,
                logger_level='DEBUG').get_logger()

url1 = "https://tw.linovelib.com/themes/zhmb/js/hm.js"
url2 = "https://tw.linovelib.com/themes/zhmb/js/readtool.js"
urls = [url1, url2]

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh,zh-HK;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,en-US;q=0.6,en;q=0.5,en-GB;q=0.4",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    # "Origin": "https://tw.linovelib.com",
}


async def fetch_js():
    timeout = aiohttp.ClientTimeout(total=30, connect=15)
    conn = aiohttp.TCPConnector(ssl=False)
    trust_env = True
    async with aiohttp.ClientSession(timeout=timeout, connector=conn, trust_env=trust_env) as session:
        tasks = [asyncio.create_task(aiohttp_get_with_retry(session, url, headers=headers, logger=logger)) for url in
                 urls]
        completed, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

        # 获取第一个成功返回的任务结果
        for task in completed:
            text = task.result()
            if text:
                return text


if __name__ == '__main__':
    js_file_text = asyncio.run(fetch_js())
    print(js_file_text)

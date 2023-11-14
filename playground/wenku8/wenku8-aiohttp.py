import asyncio

import aiohttp

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.57'
}

book_id = 2961
book_index_url = f"https://www.wenku8.net/book/{book_id}.htm"


async def main():
    jar = aiohttp.CookieJar(unsafe=True)
    conn = aiohttp.TCPConnector(ssl=False)
    trust_env = False
    timeout = aiohttp.ClientTimeout(total=30, connect=15)
    async with aiohttp.ClientSession(trust_env=True,timeout=timeout,connector=conn,cookie_jar=jar) as session:
        async with session.get(book_index_url, headers=headers) as response:
            print(response.status)
            text_ = await response.text()
            print(text_[:300])


asyncio.run(main())

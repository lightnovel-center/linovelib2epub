import aiohttp
import asyncio

# see also https://stackoverflow.com/a/69605432

async def main(url):
    # 尝试下 ssl=True 会发生什么事情？是否还能正常下载？
    tcp_connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=tcp_connector) as session:
        async with session.get(url) as response:
            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])
            bytes = await response.read()
            print("Body:", len(bytes), "...")


url = 'https://iili.io/JEbYIus.jpg'
url2 = 'https://iili.io/JEbYz9n.jpg'

asyncio.run(main(url))

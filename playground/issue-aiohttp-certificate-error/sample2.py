import aiohttp
import asyncio
import ssl
import certifi

print(f'{certifi.where()=}')

async def main(url):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(url) as response:
            print("Status:", response.status)


url = 'https://iili.io/JEbYIus.jpg'

loop = asyncio.get_event_loop()
loop.run_until_complete(main(url))
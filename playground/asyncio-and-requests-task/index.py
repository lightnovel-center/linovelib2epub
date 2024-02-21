import asyncio
import requests


async def async_request(url):
    response = requests.get(url)
    # The request was rejected because of the bilibili security control policy.
    if url == "https://www.bilibili.com":
        print(response.text)
    print(f"Response from {url}: {response.status_code}")


async def main():
    urls = ["https://www.example.com", "https://www.google.com", "https://www.github.com", "https://www.bilibili.com",
            "https://www.not-found-not-found.com/path"]

    tasks = [asyncio.create_task(async_request(url)) for url in urls]

    await asyncio.gather(*tasks)


asyncio.run(main())

import aiohttp
import asyncio


async def fetch(session, url):
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception as e:
        # 抛出异常
        raise Exception(f"请求 {url} 时出现异常: {e}")


async def main():
    urls = {'https://jsonplaceholder.typicode.com/todos/1': 'None',
            'https://jsonplaceholder.typicode.com/todos/2': 'SKIP',
            'https://jsonplaceholder.typicode.com/todos/3': 'None'}
    async with aiohttp.ClientSession() as session:
        while 'None' in urls.values():
            tasks = []
            for url, value in urls.items():
                if value == 'None':
                    tasks.append(asyncio.ensure_future(fetch(session, url)))
            # 无法实时追踪爬取的进度，所以不喜欢gather()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for url, result in zip(urls.keys(), results):
                if isinstance(result, Exception):
                    # 处理异常的逻辑
                    print(result)
                else:
                    urls[url] = result
            print(urls)  # 输出当前的结果


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

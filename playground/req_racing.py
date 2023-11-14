import asyncio
import aiohttp


async def fetch(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_status = response.status
                if response_status == 200:
                    text = await response.text()
                    return 'SUCCESS', text
                else:
                    return 'FAIL', None
    except:
        return 'FAIL', None


async def main():
    # parse urls from chapter sample page
    url1 = "https://w.linovelib.com/themes/zhmb/js/hm.js"
    url2 = "https://w.linovelib.com/themes/zhmb/js/readtool.js"
    urls = [url1, url2]

    # 使用asyncio.gather()同时执行多个异步任务
    tasks = [asyncio.create_task(fetch(url)) for url in urls]
    completed, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    # 获取第一个成功返回的任务结果
    for task in completed:
        # 'SUCCESS', text
        # 'FAIL', None
        msg, text = task.result()
        if msg == 'SUCCESS':
            return text
        else:
            print('skip')


# 运行主协程
result = asyncio.run(main())
print(result[:50])

# make sure result is not None

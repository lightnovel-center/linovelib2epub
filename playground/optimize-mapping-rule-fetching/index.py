import asyncio


# 在这个示例中，我们传递了一个事件循环给ACrawler的构造函数，并使用await self.init()来确保在执行crawl()方法之前初始化已经完成。
# 通过这种方式，您可以在初始化时提前获取解析规则，而不会同步阻塞代码。

class ACrawler:
    def __init__(self, loop):
        self.parse_rule = None
        self.loop = loop

    async def fetch_parse_rule(self):
        # 模拟异步网络IO查询，获取解析规则
        await asyncio.sleep(1)  # 假设这里需要1秒钟来获取解析规则
        self.parse_rule = "Your parse rule here"

    async def init(self):
        task = asyncio.create_task(self.fetch_parse_rule())
        await task

    async def crawl(self, url):
        if self.parse_rule is None:
            # 如果解析规则尚未获取，等待初始化完成
            await self.init()

        # 在这里执行爬取和解析操作，使用self.parse_rule来解析数据
        print(f"Crawling {url} using parse rule: {self.parse_rule}")


# 创建事件循环并传递给ACrawler构造函数
loop = asyncio.get_event_loop()
crawler = ACrawler(loop)


# 启动事件循环并执行初始化任务
async def main():
    await crawler.init()


# 使用asyncio.run运行初始化任务，以便在初始化完成后进行爬取
asyncio.run(main())


# 执行爬取操作
async def crawl_task():
    await crawler.crawl("https://example.com")


loop.run_until_complete(crawl_task())

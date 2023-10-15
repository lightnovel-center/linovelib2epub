import asyncio


async def task1():
    print("Task 1 started")
    await asyncio.sleep(3)  # 模拟一个耗时操作
    print("Task 1 completed")
    return {"a": 1, "b": 2}


async def main():
    # 启动任务1
    task1_result = asyncio.create_task(task1())

    # mock do something heavy
    print('do something...')
    await asyncio.sleep(1)
    # await asyncio.sleep(5)

    # 等待任务1完成,这里必须等待，直到rule获取完成
    rule = await task1_result
    print(f'rule={rule}')

    # 任务1完成后继续任务3
    print("Task 3 started")
    await asyncio.sleep(1)  # 模拟一个耗时操作
    print("Task 3 completed")


if __name__ == "__main__":
    asyncio.run(main())

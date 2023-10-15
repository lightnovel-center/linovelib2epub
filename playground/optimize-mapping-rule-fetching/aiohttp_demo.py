import asyncio
from typing import Any, Dict

import aiohttp


# move this func to utils
async def aiohttp_with_retry(client: aiohttp.ClientSession,
                             url: str,
                             headers: Dict[str, Any] | None = None,
                             retry_max: int = 5,
                             timeout: int = 10,
                             logger: Any = None) -> Any:
    if headers is None:
        headers = {}

    current_num_of_request: int = 0

    while current_num_of_request <= retry_max:
        try:
            async with client.get(url, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    if logger:
                        logger.warning(f'Request {url} succeed but status code is {response.status}.')
                    await asyncio.sleep(1)
        except Exception as e:
            if logger:
                logger.error(f'Request {url} failed: {e}')
            await asyncio.sleep(1)

        current_num_of_request += 1
        if logger:
            logger.warning('current_num_of_request: ', current_num_of_request)

    return None

async def main():
    async with aiohttp.ClientSession() as session:
        result = await aiohttp_with_retry(session, 'https://example.com')
        if result:
            print(result)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import os
import random
import re
import time
from functools import wraps
from http.cookies import SimpleCookie
from typing import Any, Callable, Dict, NoReturn

import aiohttp
import pkg_resources
from fake_useragent import UserAgent


def cookiedict_from_str(cookie_str: str = '') -> Dict[str, str]:
    cookie: SimpleCookie[str] = SimpleCookie()
    cookie.load(cookie_str)
    cookie_dict = {k: v.value for k, v in cookie.items()}
    return cookie_dict


def random_useragent() -> str:
    try:
        return UserAgent().random  # type: ignore
    except (Exception,):
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'


def create_folder_if_not_exists(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def requests_get_with_retry(client: Any,
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
            response = client.get(url, headers=headers, timeout=timeout)
            if response:
                return response
            else:
                if logger:
                    logger.warning(f'Request {url} succeed but data is empty, retry {current_num_of_request + 1} times')
        except (Exception,) as e:
            if logger:
                logger.error(f'Request {url} failed.', e)

        current_num_of_request += 1
        # 指数退避参考 https://cloud.google.com/memorystore/docs/redis/exponential-backoff?hl=zh-cn#example_algorithm
        # 具体逻辑：
        # 1.向服务器特定API发出请求。
        # 2.如果请求失败，请等待 1 + random_number_milliseconds 秒后再重试请求。
        # 3.如果请求失败，请等待 2 + random_number_milliseconds 秒后再重试请求。
        # 4.如果请求失败，请等待 4 + random_number_milliseconds 秒后再重试请求。
        # 5.依此类推，等待时间上限为 maximum_backoff。
        # 等待时间达到上限后，您可以继续等待并重试，直到达到重试次数上限（但接下来的重试操作不会增加各次重试之间的等待时间）。

        # 等待时间为 min(((2^n)+random_number_seconds), maximum_backoff)，其中，n 会在每次迭代（请求）后增加 1。
        # 其中：
        # - random_number_seconds 是小于1的秒数（随机值）。
        # - maximum_backoff 设置为一个较大的容忍值，这里设置为10s。这是基于经验的估计。
        n = current_num_of_request
        random_number_seconds = round(random.uniform(0, 1), 2)  # 0.01-0.99s
        maximum_backoff = 10
        retry_interval = min(round(((2 ** (n - 1)) + random_number_seconds), 2), maximum_backoff)

        if logger:
            logger.warning(f'current_num_of_request: {current_num_of_request}; retry_interval: {retry_interval}(s)')

        time.sleep(retry_interval)

    logger.error(f'Request {url} failed after {retry_max} retries.')
    return None


async def aiohttp_get_with_retry(client: aiohttp.ClientSession,
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
                elif response.status == 404:
                    return None
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
            logger.warning(f'current_num_of_request: {current_num_of_request}')

    return None


async def aiohttp_post_with_retry(client: aiohttp.ClientSession,
                                  url: str,
                                  params: Any,
                                  headers: Dict[str, Any] | None = None,
                                  retry_max: int = 5,
                                  timeout: int = 10,
                                  logger: Any = None,
                                  ) -> Any:
    if headers is None:
        headers = {}

    current_num_of_request: int = 0

    while current_num_of_request <= retry_max:
        try:
            async with client.post(url, data=params, headers=headers, timeout=timeout) as response:
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
            logger.warning(f'current_num_of_request: {current_num_of_request}')

    return None


def is_valid_image_url(url: str) -> bool:
    """
    Example image link: https://img.linovelib.com/3/3211/163938/193293.jpg
    Refer: https://www.ietf.org/rfc/rfc2396.txt, https://stackoverflow.com/a/169631

    ^https?://(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpe?g|gif|png|webp|bmp|svg)$    # noqa
             |-------- domain -----------|--- path ------|--------- --extension -----|
    """
    image_pattern = r"^https?://(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpe?g|gif|png|webp|bmp|svg)$"
    return bool(re.match(image_pattern, url))


def check_image_integrity(expected_length: str | int, actual_length: str | int) -> None | NoReturn:
    """
    check file integrity by comparing expected_get and actual_get

    :param expected_length:
    :param actual_length:
    :return:
    """
    if expected_length and actual_length:
        # actual_length should be >= expected_length
        if int(actual_length) < int(expected_length):
            raise IOError(
                'incomplete read ({} bytes get, {} bytes expected)'.format(actual_length, expected_length)
            )

    return None


# Replace invalid character for file/folder name
def sanitize_pathname(pathname: str) -> str:
    # '/ \ : * ? " < > |'
    return re.sub(r"[/\\:*?\"<>|]", "_", pathname)


def read_pkg_resource(file_path: str) -> bytes:
    # file_path example: "./styles/chapter.css"
    return pkg_resources.resource_string(__name__, file_path)


def async_timed() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapped(*args: Any, **kwargs: Any) -> Any:
            print(f'starting {func} with args {args} {kwargs}')
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                print(f'finished {func} in {end - start :.4f} second(s)')

        return wrapped

    return wrapper


def is_async(func: Callable[..., Any]) -> bool:
    return asyncio.iscoroutinefunction(func)

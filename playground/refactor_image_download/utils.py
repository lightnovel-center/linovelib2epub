import json
import time
from functools import wraps
from typing import Callable, Any


def get_image_urls():
    with open('./image_urls.json', mode='r', encoding='utf-8') as fp:
        return json.load(fp)

def async_timed():
    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            print(f'starting {func} with args {args} {kwargs}')
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                print(f'finished {func} in {end - start :.4f} second(s)')

        return wrapped

    return wrapper

if __name__ == '__main__':
    print(get_image_urls())

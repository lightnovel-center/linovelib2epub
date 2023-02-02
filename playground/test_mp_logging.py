import logging
from multiprocessing import Pool

from multiprocessing_logging import install_mp_handler

logging.basicConfig()
logger = logging.getLogger('mp')
install_mp_handler(logger=logger)

def log_url(url):
    print(url)
    # logger.info(url)

# 难题，多进程下如何写logging。

if __name__ == '__main__':
    urls = ['u1', 'u2', 'u3', 'u4']
    process_pool = Pool(processes=int(4))
    error_links = process_pool.map(log_url, urls)

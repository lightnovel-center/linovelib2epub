import logging
import multiprocessing

logger = logging.getLogger()
fh = logging.FileHandler('my_log.log', encoding='utf-8')
logger.addHandler(fh)
logger.setLevel(logging.INFO)

data_to_process = [1, 2, 3]


# 将logger 明确地pass到子进程中执行是可行的，但是似乎不够优雅
def my_function(num, logger):
    logger.info('hello from inside process')
    return num


def run():
    with multiprocessing.Pool(processes=3) as pool:
        logger.info('hello from before process')
        params = []
        for data in data_to_process:
            params.append((data, logger))  # Logger is passed to my_function
        for result in pool.starmap(my_function, params):
            logger.info(f'result of process: {result}')


if __name__ == '__main__':
    run()

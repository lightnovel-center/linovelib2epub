import logging
from logging import StreamHandler
import multiprocessing


class MyLogger:
    def __init__(self):
        logger = logging.getLogger()
        # fh = logging.FileHandler('logger_incubator.log', encoding='utf-8')
        stream_handler = StreamHandler()
        logger.addHandler(stream_handler)
        logger.setLevel(logging.INFO)
        self.logger = logger

    def get_logger(self):
        return self.logger


data_to_process = [1, 2, 3]


def my_function(num, logger):
    # the line below is not logged!
    logger.info('hello from inside process')
    return num


class MySpider:

    def __init__(self, logger):
        self.logger = logger

    def run(self):
        with multiprocessing.Pool(processes=3) as pool:
            self.logger.info('hello from before process')
            params = []
            for data in data_to_process:
                params.append((data, logger))  # Logger is passed to my_function
            for result in pool.starmap(my_function, params):
                self.logger.info(f'result of process: {result}')


if __name__ == '__main__':
    logger = MyLogger().get_logger()
    spider = MySpider(logger)
    spider.run()

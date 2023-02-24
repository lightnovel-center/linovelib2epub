import logging
import logging.handlers
import multiprocessing
import sys
import traceback
from logging import StreamHandler
from os import path


# https://www.jamesfheath.com/2020/06/logging-in-python-while-multiprocessing.html

class MultiprocessingLogHelper:
    def __init__(self, queue, log_name, log_file_path):
        self.queue = queue
        self.log_name = log_name
        self.log_file_path = log_file_path
        self.logger = self.listener_configurer()

    def listener_configurer(self):
        logger = logging.getLogger(self.log_name)

        # fh = logging.FileHandler(
        #     path.join(self.log_file_path, f'{self.log_name}.log'), encoding='utf-8')
        # fmtr = logging.Formatter(
        #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # fh.setFormatter(fmtr)
        logger.setLevel(logging.INFO)

        # current_fh_names = [fh.__dict__.get(
        #     'baseFilename', '') for fh in logger.handlers]
        # if not fh.__dict__['baseFilename'] in current_fh_names:  # This prevents multiple logs to the same file
        #     logger.addHandler(fh)

        # logger.addHandler(fh)
        stream_handler = StreamHandler()
        logger.addHandler(stream_handler)

        return logger

    def listener_process(self):
        self.listener_configurer()

        while True:
            try:
                record = self.queue.get()
                if record is None:
                    break
                logger = logging.getLogger(record.name)
                logger.handle(record)
            except Exception:
                print('Failure in listener_process', file=sys.stderr)
                traceback.print_last(limit=1, file=sys.stderr)


class MySpider:
    def __init__(self, log_helper):
        self.log_helper = log_helper
        self.logger = self.log_helper.logger

    def run(self):
        data_to_process = [1, 2, 3]
        num_processes = 3
        with multiprocessing.Pool(num_processes) as pool:
            self.logger.info('hello from before process')
            params = []
            for i, data in enumerate(data_to_process):
                params.append((data, self.log_helper.queue))  # Log QUEUE is passed to my_function, along with i

            for result in pool.starmap(self.my_function, params):
                self.logger.info(f'result of process: {result}')

    def my_function(self, num, log_queue):
        qh = logging.handlers.QueueHandler(log_queue)
        root_name = path.join(self.log_helper.log_file_path, self.log_helper.log_name)
        root_logger = logging.getLogger(root_name)
        root_logger.addHandler(qh)
        root_logger.setLevel(logging.INFO)

        logger = logging.getLogger(self.log_helper.log_name)
        logger.setLevel(logging.INFO)

        logger.info('hello from inside process')

        return num


def run():
    # create MyLogger
    log_queue = multiprocessing.Manager().Queue()
    # !!!!!!!这个路径不为“” 就无法打印,太坑了python!!!!!!!!!!!!
    log_file_path = ''
    # log_file_path = './logs'
    log_name = 'my_log'

    log_helper = MultiprocessingLogHelper(log_queue, log_name, log_file_path)

    # listen
    listener = multiprocessing.Process(target=log_helper.listener_process,
                                       args=())
    listener.start()  # Start the listener process

    # client send logs
    my_spider = MySpider(log_helper)
    my_spider.run()

    # stop
    log_queue.put_nowait(None)  # End the queue
    listener.join()  # Stop the listener


if __name__ == '__main__':
    run()

import logging
import logging.handlers
import multiprocessing
import sys
import traceback
from os import path

log_file_path = ''  # Wherever your log files live
log_name = 'my_log'


def listener_configurer(log_name, log_file_path):
    """ Configures and returns a log file based on
    the given name

    Arguments:
        log_name (str): String of the log name to use
        log_file_path (str): String of the log file path

    Returns:
        logger: configured logging object
    """
    logger = logging.getLogger(log_name)

    fh = logging.FileHandler(
        path.join(log_file_path, f'{log_name}.log'), encoding='utf-8')
    fmtr = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(fmtr)
    logger.setLevel(logging.INFO)
    current_fh_names = [fh.__dict__.get(
        'baseFilename', '') for fh in logger.handlers]
    if not fh.__dict__['baseFilename'] in current_fh_names:  # This prevents multiple logs to the same file
        logger.addHandler(fh)

    return logger


def listener_process(queue, configurer, log_name):
    """ Listener process is a target for a multiprocess process
    that runs and listens to a queue for logging events.

    Arguments:
        queue (multiprocessing.manager.Queue): queue to monitor
        configurer (func): configures loggers
        log_name (str): name of the log to use

    Returns:
        None
    """
    configurer(log_name, log_file_path)

    while True:
        try:
            record = queue.get()
            if record is None:
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except Exception:
            print('Failure in listener_process', file=sys.stderr)
            traceback.print_last(limit=1, file=sys.stderr)


def my_function(num, log_queue, i):
    qh = logging.handlers.QueueHandler(log_queue)
    root_logger = logging.getLogger(path.join(log_file_path, log_name))
    root_logger.addHandler(qh)
    root_logger.setLevel(logging.INFO)

    logger = logging.getLogger(log_name).getChild(f'child_{i}')  # This allows you to know what process you're in
    logger.setLevel(logging.INFO)

    logger.info('hello from inside process')

    return num


def run():
    logger = listener_configurer(log_name, log_file_path)

    manager = multiprocessing.Manager()
    log_queue = manager.Queue()
    listener = multiprocessing.Process(target=listener_process,
                                       args=(log_queue, listener_configurer, log_name))
    listener.start()  # Start the listener process

    data_to_process = [1, 2, 3]

    num_processes = 3
    with multiprocessing.Pool(num_processes) as pool:
        logger.info('hello from before process')
        params = []
        for i, data in enumerate(data_to_process):
            params.append((data, log_queue, i))  # Log QUEUE is passed to my_function, along with i
        for result in pool.starmap(my_function, params):
            logger.info(f'result of process: {result}')

    log_queue.put_nowait(None)  # End the queue
    listener.join()  # Stop the listener


if __name__ == '__main__':
    run()

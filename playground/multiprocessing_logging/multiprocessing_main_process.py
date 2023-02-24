import logging
import logging.config
import logging.handlers
import multiprocessing
import threading
from multiprocessing import Process, Queue


def logger_listener(queue):
    while True:
        record = queue.get()
        print(record)
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)


def worker_process(queue):
    _worker_configure(queue)

    logger_name = 'foo'
    logger = logging.getLogger(logger_name)

    level = logging.INFO
    processing_name = multiprocessing.current_process().name
    message = f"Message no. {processing_name}"

    logger.log(level, message)


def _worker_configure(queue):
    qh = logging.handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(qh)


if __name__ == '__main__':
    # new queue
    q = Queue()

    # listener run in main process (separate thread)
    # https://docs.python.org/3/howto/logging.html#logging-flow
    # logger flow 和 handler flow 都会进行：level的通行判定 -> filter的通行判定
    d = {
        'version': 1,
        'formatters': {
            'console': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
            },
            'detailed': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'console'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'mplog.log',
                'mode': 'w',
                'formatter': 'detailed',
            },
            'foofile': {
                'class': 'logging.FileHandler',
                'filename': 'mplog-foo.log',
                'mode': 'w',
                'formatter': 'detailed',
            },
            'errors': {
                'class': 'logging.FileHandler',
                'filename': 'mplog-errors.log',
                'mode': 'w',
                'level': 'ERROR',
                'formatter': 'detailed',
            },
        },
        'loggers': {
            'foo': {
                'handlers': ['foofile']
            }
        },
        # root logger
        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'file', 'errors']
        },
    }
    logging.config.dictConfig(d)
    lp = threading.Thread(target=logger_listener, args=(q,))
    lp.start()

    # worker
    wp = Process(target=worker_process, name='worker 1', args=(q,))
    wp.start()

    # At this point, the main process could do some useful work of its own
    # Once it's done that, it can wait for the workers to terminate...
    wp.join()

    # And now tell the logging thread to finish up, too
    q.put(None)
    lp.join()

# refer:
# https://www.zopatista.com/python/2019/05/11/asyncio-logging/
# https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes

# Why logging module in multiprocessing is not worked?
# logging to a single file from multiple processes is not supported,
# because there is no standard way to serialize access to a single file across multiple processes in Python

# Why print works in multiprocessing?
# Every print has its own input and output buffer in different processors.

# Solution:
# one way of doing this is to have all the processes log to a SocketHandler,
# and have a separate process which implements a socket server which reads from the socket and logs to file

import asyncio
import logging
import logging.handlers

try:
    # Python 3.7 and newer, fast reentrant implementation
    # without task tracking (not needed for that when logging)
    from queue import SimpleQueue as Queue
except ImportError:
    from queue import Queue
from typing import List


class LocalQueueHandler(logging.handlers.QueueHandler):
    def emit(self, record: logging.LogRecord) -> None:
        # Removed the call to self.prepare(), handle task cancellation
        try:
            self.enqueue(record)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.handleError(record)


def setup_logging_queue() -> None:
    """Move log handlers to a separate thread.

    Replace handlers on the root logger with a LocalQueueHandler,
    and start a logging.QueueListener holding the original
    handlers.

    """
    queue = Queue()
    root = logging.getLogger()

    handlers: List[logging.Handler] = []

    handler = LocalQueueHandler(queue)
    root.addHandler(handler)
    for h in root.handlers[:]:
        # if not a queue handler, that means it's a normal log handler, moves it to handlers and deletes from root
        if h is not handler:
            root.removeHandler(h)
            handlers.append(h)

    # root has one queue handler to listen
    listener = logging.handlers.QueueListener(
        queue, *handlers, respect_handler_level=True
    )
    listener.start()
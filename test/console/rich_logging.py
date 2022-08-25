import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

log.info("Logging set up.")

def division(a, b):
    log.debug(f"Dividing {a} by {b}.")
    try:
        return a / b
    except ZeroDivisionError:
        log.exception("Oh noes!")

division(3, 2)
division(5, 0)

#[16:04:17] INFO     Logging set up.                          rich_logging.py:11
           # DEBUG    Dividing 3 by 2.                         rich_logging.py:14
           # DEBUG    Dividing 5 by 0.                         rich_logging.py:14
           # ERROR    Oh noes!                                 rich_logging.py:18
           #          Traceback (most recent call last):
           #            File
           #          "D:/Code/PycharmProjects/linovelib2epub/
           #          test/console/rich_logging.py", line 16,
           #          in division
           #              return a / b
           #          ZeroDivisionError: division by zero
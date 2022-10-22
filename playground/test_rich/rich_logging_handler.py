import logging
import random

from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    # tracebacks_suppress=[click])
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")

# log.info("Hello, World!")
# log.error("[bold red blink]Server is shutting down![/]", extra={"markup": True})
# log.error("123 will not be highlighted", extra={"highlighter": None})

try:
    print(1 / 0)
except Exception:
    log.exception("unable print!")



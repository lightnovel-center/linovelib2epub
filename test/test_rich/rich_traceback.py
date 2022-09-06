from rich.console import Console
# console = Console()

# try:
#     do_something()
# except Exception:
#     console.print_exception(show_locals=True)


# from rich.traceback import install
# install(show_locals=True)
#
# # make unCaughtException
# do_something()


# Automatic Traceback Handler
# https://rich.readthedocs.io/en/stable/traceback.html#:~:text=./.venv/lib/python3.9/site%2Dpackages/sitecustomize.py

# max frames
from rich.console import Console


def foo(n):
    return bar(n)


def bar(n):
    return foo(n)


console = Console()

try:
    foo(1)
except Exception:
    console.print_exception(max_frames=20)
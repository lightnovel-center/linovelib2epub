from time import sleep

from rich.console import Console

console3 = Console()


# console print
# console.print([1, 2, 3])
# console.print("[blue underline]Looks like a link")
# console.print(locals())
# console.print("FOO", style="white on blue")

# console logging
# console.log("Hello, World!")
# [17:04:39] Hello, World!     D:/Code/PycharmProjects/linovelib2epub/test/rich_test/rich_logging.py:5

# console.print_json('[false, true, null, "foo"]')
# [
#   false,
#   true,
#   null,
#   "foo"
# ]

# low-level output
# console.out("Locals", locals())
# Locals {'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x000001E558A3FD48>,
# '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, '__file__': 'D:/Code/PycharmProjects/linovelib2epub/test/rich_test/rich
# _console.py', '__cached__': None, 'Console': <class 'rich.console.Console'>, 'console': <console width=159 ColorSystem.WINDOWS>}

# console rule
# from rich.style import Style
# console.rule("[bold red]Chapter 2", style=Style(color='blue'), align='center')

# console status
# >python -m rich.status
# [17:21:29] Importing advanced AI                                                                                                                     status.py:118
# [17:21:32] Advanced Covid AI Ready                                                                                                                   status.py:120
# [17:21:38] Found 10,000,000,000 copies of Covid32.exe                                                                                                status.py:124
# Covid deleted successfully

# console spinner
# def do_work():
#     sleep(3)
#
#
# with console.status("Monkeying around...", spinner="monkey"):
#     do_work()

# run python -m rich.spinner to see all spinner choices

# console alignment
# console2 = Console(width=20)
#
# style = "bold white on blue"
# console2.print("Rich", style=style)
# console2.print("Rich", style=style, justify="left")
# console2.print("Rich", style=style, justify="center")
# console2.print("Rich", style=style, justify="right")
# Rich
# Rich
#         Rich
#                 Rich

# console overflow
# from typing import List
# from rich.console import Console, OverflowMethod
#
# console3 = Console(width=14)
# supercali = "supercalifragilisticexpialidocious"
#
# overflow_methods: List[OverflowMethod] = ["fold", "crop", "ellipsis"]
# for overflow in overflow_methods:
#     console3.rule(overflow)
#     console3.print(supercali, overflow=overflow, style="bold blue")
#     console3.print()

# ──── fold ────
# supercalifragi
# listicexpialid
# ocious
#
# ──── crop ────
# supercalifragi
#
# ── ellipsis ──
# supercalifrag…

#  todo: https://rich.readthedocs.io/en/stable/console.html#console-style

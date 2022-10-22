# https://rich.readthedocs.io/en/stable/text.html
from rich.console import Console

console = Console()

# text = Text("Hello, World!")
# text.stylize("bold magenta", 0, 6)
# console.print(text)

# print("\033[1m"+"Title"+"\033[0m") bold: \033[1m
# text = Text.from_ansi("\033[1mHello, World!\033[0m")
# console.print(text)
#
# text = Text.assemble(("Hello", "bold magenta"), " World!")
# console.print(text)

from rich import print
from rich.panel import Panel
from rich.text import Text

panel = Panel(Text("Hello", justify="left"))
print(panel)

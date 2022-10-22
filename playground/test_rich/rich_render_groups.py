# from rich import print
# from rich.console import Group
# from rich.panel import Panel
#
# panel_group = Group(
#     Panel("Hello", style="on blue"),
#     Panel("World", style="on red"),
# )
# print(Panel(panel_group))

from rich import print
from rich.console import group
from rich.panel import Panel


@group()
def get_panels():
    yield Panel("Hello", style="on blue")
    yield Panel("World", style="on red")


print(Panel(get_panels()))

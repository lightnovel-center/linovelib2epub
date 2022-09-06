from rich.console import Console

console = Console()
# console.print("Hello", style="magenta")
# console.print("Hello", style="#af00ff")
# console.print("Hello", style="rgb(175,0,255)")

# console.print("DANGER!", style="red on white")
#
# console.print("Danger, Will Robinson!", style="blink bold red underline on white")
#
# console.print("foo [not bold]bar[/not bold] baz", style="bold")

# console.print("Google", style="link https://google.com")

# style class
# from rich.style import Style
# danger_style = Style(color="red", blink=True, bold=True)
# console.print("Danger, Will Robinson!", style=danger_style)


# from rich.style import Style
#
# base_style = Style.parse("cyan")
# console.print("Hello, World", style = base_style + Style(underline=True))

# style = Style(color="magenta", bgcolor="yellow", italic=True)
# style = Style.parse("italic magenta on yellow")

# style themes
# from rich.console import Console
# from rich.theme import Theme
# custom_theme = Theme({
#     "info": "dim cyan",
#     "warning": "magenta",
#     "danger": "bold red"
# })
# console = Console(theme=custom_theme)
# console.print("This is information", style="info")
# console.print("[warning]The pod bay doors are locked[/warning]")
# console.print("Something terrible happened!", style="danger")

# custom defaults
# from rich.console import Console
# from rich.theme import Theme
# console = Console(theme=Theme({"repr.number": "bold green blink"}))
# console.print("The total is 128")

# load themes in  a config file
# [styles]
# info = dim cyan
# warning = magenta
# danger = bold red
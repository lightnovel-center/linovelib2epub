from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.theme import Theme


class EmailHighlighter(RegexHighlighter):
    """Apply style to anything that looks like an email."""

    base_style = "example."
    # http://docs.python.org/library/re.html
    # (?P<name>...) Similar to regular parentheses,
    # but the substring matched by the group is accessible within the rest of the regular expression
    # via the symbolic group name name. Group names must be valid Python identifiers,
    # and each group name must be defined only once within a regular expression.
    # A symbolic group is also a numbered group, just as if the group were not named.
    # So the group named id in the example below can also be referenced as the numbered group 1.
    highlights = [r"(?P<email>[\w-]+@([\w-]+\.)+[\w-]+)"]


theme = Theme({"example.email": "bold magenta"})
console = Console(highlighter=EmailHighlighter(), theme=theme)
console.print("Send funds to money@example.org")

from rich import print
print("Visit file [link=D:\Code\lightnovel-center\linovelib2epub\playground\\test_rich\\]blog[/link]!")

#
# console = Console(theme=theme)
# highlight_emails = EmailHighlighter()
# console.print(highlight_emails("Send funds to money@example.org"))


from random import randint

from rich import print
from rich.highlighter import Highlighter


class RainbowHighlighter(Highlighter):
    def highlight(self, text):
        for index in range(len(text)): # index: 0...n-1
            text.stylize(f"color({randint(16, 255)})", index, index + 1)


# rainbow = RainbowHighlighter()
# print(rainbow("I must not fear. Fear is the mind-killer."))
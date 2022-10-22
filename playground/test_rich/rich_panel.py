#  https://rich.readthedocs.io/en/stable/panel.html

from rich import print
from rich.panel import Panel
print(Panel("Hello, [red]World!"))

print(Panel.fit("Hello, [red]World!"))


print(Panel("Hello, [red]World!", title="Welcome", subtitle="Thank you"))
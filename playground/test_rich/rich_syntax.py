from rich.console import Console
from rich.syntax import Syntax

console = Console()
# with open("rich_syntax.py", "rt") as code_file:
#     syntax = Syntax(code_file.read(), "python")

syntax = Syntax.from_path("rich_syntax.py",line_numbers=True)
console.print(syntax)
from rich.tree import Tree
from rich import print

tree = Tree("Rich Tree")
tree.add("foo")
tree.add("bar")
print(tree)

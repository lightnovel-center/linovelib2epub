# from rich import print
# from rich.padding import Padding
# test = Padding("Hello", 1)
# print(test)

# from rich import print
# from rich.padding import Padding
#
# test = Padding("Hello", (2, 4))  # 2 line for Y and 4 spaces for X
# print(test)

from rich import print
from rich.padding import Padding

test = Padding("Hello", (2, 4), style="on blue", expand=False)
print(test)

# For instance, if you want to emphasize an item in a Table you could add a Padding object to a row
# with a padding of 1 and a style of “on red”.

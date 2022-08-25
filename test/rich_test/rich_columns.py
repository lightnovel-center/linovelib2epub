import os

from rich import print
from rich.columns import Columns

directory = os.listdir('./')
print(Columns(directory))
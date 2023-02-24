import psutil
from rich.console import Console
console = Console()

p = psutil.Process()
# console.log(p.as_dict())

# *unix only, goodbye windows
# num = p.cpu_num()
# print(num)

print(p.cpu_affinity())

# set; from now on, process will run on CPU #0 and #1 only
p.cpu_affinity([0, 1])
print(p.cpu_affinity())

# reset affinity against all eligible CPUs
p.cpu_affinity([])
print(p.cpu_affinity())
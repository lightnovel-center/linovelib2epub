from rich.console import Console
console = Console()
# name_ = cpuinfo.cpu.info[0]['model name']

from cpuinfo import get_cpu_info

for key, value in get_cpu_info().items():
    console.log("{0}: {1}".format(key, value))

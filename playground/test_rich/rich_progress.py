# For basic usage call the track() function, which accepts a sequence (such as a list or range object)
# and an optional description of the job you are working on.
# The track function will yield values from the sequence and update the progress information on each iteration.
import time

import rich.progress

import time
from rich.progress import track

# for i in track(range(20), description="Processing..."):
#     time.sleep(1)  # Simulate work being done

from rich.progress import Progress
# with Progress() as progress:
#
#     task1 = progress.add_task("[red]Downloading...", total=1000)
#     task2 = progress.add_task("[green]Processing...", total=1000)
#     task3 = progress.add_task("[cyan]Cooking...", total=1000)
#
#     while not progress.finished:
#         progress.update(task1, advance=0.5)
#         progress.update(task2, advance=0.3)
#         progress.update(task3, advance=0.9)
#         time.sleep(0.02)

# transient
# with Progress(transient=True) as progress:
#     task = progress.add_task("Working", total=100)
#     while not progress.finished:
#         progress.update(task, advance=5)
#         time.sleep(.2)

# Indeterminate progress
# In these cases you can call add_task() with start=False or total=None
# which will display a pulsing animation that lets the user know something is working
# 适用于请求server，等待响应。此时server什么时候返回，是不确定的。除非是下载文件，可以计算下载进度。
# with Progress(transient=True) as progress:
#     task1 = progress.add_task("Task 1", start=False)
#     task2 = progress.add_task("Task 2", total=None)
#     while not progress.finished:
#         progress.update(task1, advance=5)
#         progress.update(task2, advance=5)
#         time.sleep(.2)

# When you have the number of steps you can call start_task()
# which will display the progress bar at 0%, then update() as normal.
# with Progress(transient=True, expand=True) as progress:
#     # thinking: how to know this indeterminate task elapsed time.
#     task1 = progress.add_task("Task 1", start=False, total=None)
#
#     print('MOCK:　wait for task 1 to get the response')
#     time.sleep(2)
#
#     print('Now start task1')
#     progress.start_task(task1)

# Auto refresh
# By default, the progress information will refresh 10 times a second.
# You can set the refresh rate with the refresh_per_second argument on the Progress constructor.
# You should set this to something lower than 10 if you know your updates will not be that frequent.
#
# You might want to disable auto-refresh entirely if your updates are not very frequent,
# which you can do by setting auto_refresh=False on the constructor.
# If you disable auto-refresh you will need to call refresh() manually after updating your task(s).
# column
# progress = Progress(
#     TextColumn("[progress.description]{task.description}"),
#     BarColumn(),
#     TaskProgressColumn(),
#     TimeRemainingColumn(),
# )
#
# progress = Progress(
#     SpinnerColumn(),
#     *Progress.get_default_columns(),
#     TimeElapsedColumn(),
# )
# BarColumn Displays the bar.
# TextColumn Displays text.
# TimeElapsedColumn Displays the time elapsed.
# TimeRemainingColumn Displays the estimated time remaining.
# MofNCompleteColumn Displays completion progress as "{task.completed}/{task.total}" (works best if completed and total are ints).
# FileSizeColumn Displays progress as file size (assumes the steps are bytes).
# TotalFileSizeColumn Displays total file size (assumes the steps are bytes).
# DownloadColumn Displays download progress (assumes the steps are bytes).
# TransferSpeedColumn Displays transfer speed (assumes the steps are bytes.
# SpinnerColumn Displays a “spinner” animation.
# RenderableColumn Displays an arbitrary Rich renderable in the column.
# text_column = TextColumn("{task.description}", table_column=Column(ratio=1))
# bar_column = BarColumn(bar_width=None, table_column=Column(ratio=2))
# time_elapsed_column = TimeElapsedColumn(table_column=Column(ratio=1))
# progress = Progress(text_column, bar_column, time_elapsed_column, expand=True)

# with progress:
#     for n in progress.track(range(100)):
#         progress.print(n)
#         sleep(0.1)
# print /log
# with Progress() as progress:
#     task = progress.add_task("twiddling thumbs", total=10)
#     for job in range(10):
#         progress.console.print(f"Working on job #{job}")
#         # run_job(job)
#         progress.advance(task)
#         time.sleep(.5)
# from my_project import my_console
#
# with Progress(console=my_console) as progress:
#     my_console.print("[bold blue]Starting work!")
#     do_work(progress)
# customizing
# from rich.panel import Panel
# from rich.progress import Progress
#
# class MyProgress(Progress):
#     def get_renderables(self):
#         yield Panel(self.make_tasks_table(self.tasks))

# with rich.progress.open("report.txt", "r") as file:
#     data = file.read()
# print(data)

# from time import sleep
# from urllib.request import urlopen
#
# from rich.progress import wrap_file
#
# response = urlopen("https://www.textualize.io")
# size = int(response.headers["Content-Length"])
#
# with wrap_file(response, size) as file:
#     for line in file:
#         # print(line.decode("utf-8"), end="")
#         sleep(0.1)

# download
# https://github.com/Textualize/rich/blob/master/examples/downloader.py

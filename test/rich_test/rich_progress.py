from time import sleep

from rich.progress import track

for step in track(range(100), description="Image downloading..."):
    sleep(1)

# Image downloading... ----- ----------------------------------  13% 0:01:28

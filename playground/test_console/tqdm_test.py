import time

from tqdm import tqdm

# for i in tqdm(range(10)):
#     time.sleep(0.2)

# with tqdm(total=100) as pbar:
#     for i in range(10):
#         time.sleep(0.1)
#         pbar.update(10)

pbar = tqdm(total=100)
for i in range(100):
    time.sleep(0.1)
    pbar.update(1)
pbar.close()
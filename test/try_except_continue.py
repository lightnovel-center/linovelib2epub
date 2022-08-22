retry = 0

while retry <= 5:
    try:
        2 / 0
    except:
        print(f'retry: {retry}')
        retry += 1
        continue

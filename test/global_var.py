a = 3


def foo():
    global a
    print(a)  # 4
    a = a + 1


if __name__ == '__main__':
    print(a)  # 3
    a = a + 1
    foo()
    print(a)  # 5

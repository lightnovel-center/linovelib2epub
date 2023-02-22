def outer():
    x = "local"

    def inner():
        nonlocal x
        x = "nonlocal"
        print("inner:", x)

    inner()
    print("outer:", x)


outer()

foo = 0  # <- 〇


def outer2():
    foo = 5  # <- ✖

    def middle():
        foo = 10  # <- ✖

        def inner():
            global foo  # Here
            foo += 1
            print(foo)  # 1

        inner()

    middle()


outer2()

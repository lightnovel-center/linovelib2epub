def foo(*args, **kwargs):
    print(type(args))
    print(args)

    print(type(kwargs))
    print(kwargs)


foo(1, 2, 3, 4,e=5,f=6)

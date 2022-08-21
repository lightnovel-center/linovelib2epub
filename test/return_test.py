def foo(num=0):
    if num >= 0:
        return 1, 3
    else:
        return None


print(foo(10))
print(foo(-6))

rs = foo(10)
if rs:
    n1, n2 = rs
    print(n1, n2)

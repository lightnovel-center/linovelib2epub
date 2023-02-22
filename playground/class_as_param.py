class book(object):
    pass


class pen(object):
    pass


def createModel(model):
    info = model()
    return info


# book is one class definition passed as a parameter
obj1 = createModel(book)
obj2 = createModel(pen)

print(obj1, obj2)

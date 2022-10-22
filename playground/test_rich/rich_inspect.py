from rich import inspect

class foo():

    def bar(self):
        pass

    def baz(self):
        pass


inspect(foo, methods=True)

# ┌─ <class '__main__.foo'> ─┐
# │ class foo():             │
# │                          │
# │ bar = def bar(self):     │
# │ baz = def baz(self):     │
# └──────────────────────────┘

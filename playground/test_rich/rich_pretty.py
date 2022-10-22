# pprint(locals())
#
# pprint(["eggs", "ham"], expand_all=True)

# truncate
# pprint(locals(), max_length=6)
# pprint("Where there is a Will, there is a Way", max_string=21)
import rich.repr
from rich import print


#
# pretty = Pretty(locals())
# panel = Panel(pretty)
# print(panel)

# @rich.repr.auto
class Bird:
    def __init__(self, name, eats=None, fly=True, extinct=False):
        self.name = name
        self.eats = list(eats) if eats else []
        self.fly = fly
        self.extinct = extinct

    def __repr__(self):
        return f"Bird({self.name!r}, eats={self.eats!r}, fly={self.fly!r}, extinct={self.extinct!r})"


BIRDS = {
    "gull": Bird("gull", eats=["fish", "chips", "ice cream", "sausage rolls"]),
    "penguin": Bird("penguin", eats=["fish"], fly=False),
    "dodo": Bird("dodo", eats=["fruit"], fly=False, extinct=True)
}
print(BIRDS)
# {
#     'gull': Bird('gull', eats=['fish', 'chips', 'ice cream', 'sausage rolls'], fly=True, extinct=False),
#     'penguin': Bird('penguin', eats=['fish'], fly=False, extinct=False),
#     'dodo': Bird('dodo', eats=['fruit'], fly=False, extinct=True)
# }

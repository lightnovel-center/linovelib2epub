from dataclasses import dataclass, field

# - [dataclasses — Data Classes](https://docs.python.org/3/library/dataclasses.html)
# - [This Is Why Python Data Classes Are Awesome](https://www.youtube.com/watch?v=CvQ7e6yUtnw)

def generated_id():
    return 'fake id'


# @dataclass(frozen=True)
# @dataclass(frozen=False,kw_only=True)
# @dataclass(frozen=False,slots=False) # slot fast but has inheritance problem
@dataclass(frozen=False)
class User:
    name: str
    address: str
    active: bool = True
    email_addressed: list[str] = field(default_factory=list)
    # generate id by func, not initializer
    id: str = field(init=False, default_factory=generated_id)
    # not show in __repr__()
    _protected_field: str = field(init=False, repr=False)

    def __post_init__(self):
        self._protected_field = 'a protected field'


user = User('foo', 'Earth')
print(user.__dict__)
print(user)


@dataclass
class Classroom:
    users: list[User] = field(default_factory=list)

    def add_user(self, user: User):
        self.users.append(user)


classroom = Classroom()
classroom.add_user(user)
classroom.add_user(user)
print(classroom)
print(len(classroom.users))

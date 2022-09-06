# from rich.prompt import Prompt
# name = Prompt.ask("Enter your name")

# default value
# from rich.prompt import Prompt
# name = Prompt.ask("Enter your name", default="Paul Atreides")

#  list choices
from rich.prompt import Prompt
#
# name = Prompt.ask("Enter your name", choices=["Paul", "Jessica", "Duncan"], default="Paul")


# The Prompt class was designed to be customizable via inheritance. See prompt.py for examples.
# 这里我希望能够实现输入list的序号/ID，也能被视为正常的选项。因此可以重写这个方法：
# def check_choice(self, value: str) -> bool:

# 1.第一卷  2.第二卷 3.第三卷
# 合法的输入选项为： 1 或者 1.第一卷 。主要是因为有时卷名称很长，不能让用户直接手打，连复制都不想复制。

class IdChoicePrompt(Prompt):

    def check_choice(self, value: str) -> bool:
        """Check value is in the list of valid choices.

        Args:
            value (str): choice id entered by user.

        Returns:
            bool: True if choice was valid, otherwise False.
        """
        assert self.choices is not None
        choice_ids = [choice.split('.')[0] for choice in self.choices]
        return value in choice_ids


choice = IdChoicePrompt.ask("Enter your name", choices=["1.第一卷", "2.第二卷", "3.第三卷"], default=None)
print(choice)
# Enter your name [1.第一卷/2.第二卷/3.第三卷]: 2
# 2

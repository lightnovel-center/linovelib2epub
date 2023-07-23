class MyClass:
    class_variable = "This is a class variable"

    def __init__(self, instance_variable):
        self.instance_variable = instance_variable


# 创建两个实例
my_instance_1 = MyClass("This is an instance variable 1")
my_instance_2 = MyClass("This is an instance variable 2")

# 打印类变量和实例变量
print(MyClass.class_variable)
print(my_instance_1.instance_variable)
print(my_instance_2.instance_variable)

# 修改类变量
MyClass.class_variable = "This is a new class variable"

# 打印类变量和实例变量
print(MyClass.class_variable)

print(my_instance_1.class_variable)
print(my_instance_2.class_variable)
# This is a new class variable
# This is a new class variable

# 可以看到class_variable是类变量，被两个实例共享

print("==========================================")

from dataclasses import dataclass


@dataclass
class MyClass:
    class_variable: str
    instance_variable: str

    def my_method(self):
        print("This is a method of MyClass")


# 创建一个实例
my_instance = MyClass("This is a class variable", "This is an instance variable")

# 打印属性值
print(MyClass.class_variable)
# AttributeError: type object 'MyClass' has no attribute 'class_variable'
# 这里证明了添加@dataclass后，class_variable变成了实例变量

print(my_instance.class_variable)
print(my_instance.instance_variable)

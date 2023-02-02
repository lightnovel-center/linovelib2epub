# 技术调研

## 问答
- [x] [python-inquirer](https://github.com/magmax/python-inquirer)
  
  - 可行，在windows os上的基本功能支持也不错。
  - however it has a rather limited customisation options and an older UI.
- [ ] [InquirerPy](https://github.com/kazhala/InquirerPy)
  - 支持list的多选，支持index序号输入选取和方向键选取，多项的选取使用space键确认，
  - 单选选取使用Enter键确认。很棒的一个python问卷库。
  - rawlist 多选默认不能超过10个。除非重写某些特定方法。这是个设计缺点。

  
## cli

- [ ] argparse

  - python 自带的解析cli的库，可以解析基本的命令行参数，对于快速原型验证很有用。

- [ ] docopt
  
  - 利用严格的docstring格式来进行解析，生成cli程序。文档驱动。
  
## 选择

选用 python-inquirer ， 但是出现了问题：
```
{'Selecting volumes': ['第1部 第1章 转生王女和天才千金', '第3章 转生王女和王位继承权']}
```
没有index，name有可能重名。

参考 [这个文档](https://github.com/magmax/python-inquirer/blob/main/docs/usage.md#choices) ，可以传递tuple数组。
格式：`[(label,value),(label,value)]`。label用作显示，value用作array index。从而可以支持label为重复的卷名。


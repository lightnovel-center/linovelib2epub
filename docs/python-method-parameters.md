# python method parameters
讲述python方法传递参数的风格，~~这点比Java那货灵活多了。~~

## positional-parameters: 顺序的位置参数
```python
def add(a,b,c,d):
    return  a+b+c+d

add(1,2,3,4)
```
类似于一个萝卜一个坑，从左到右，分别对应。

## keywords-parameters: 关键字参数
```python
def add(a=0,b=0,c=0,d=0):
    return  a+b+c+d

add(a=1,b=2,c=3,d=4)
add(a=1,c=3,b=2,d=4)
```
采用关键字传参，可以严格按照方法定义的参数顺序。但是，也可以不按照方法定义的参数顺序。因为此时顺序不重要。

## positional-parameters + keywords-parameters
```python
def add(a,b,c=0,d=0):
    return  a+b+c+d

add(1,2,c=3,d=4)
```
这里混合了两种传参方式：

- 1,2分别对应a,b。采用位置参数传值。 
- c和d使用关键字传值。

## 独立星号? 全部采用keywords-parameters: 关键字参数
```python
def add(*, a, b, c=0, d=0):
    return a + b + c + d

res = add(a=1, b=2, c=3, d=4)
```
注意这里`add(*, a, b, c=0, d=0)`中的`*`号，它表示`*`之后的所有参数都是key-value传值的方式，位置参数传值被禁止。

## *args与 **kwargs
```python
def foo(*args, **kwargs):
    print(type(args))
    print(args)

    print(type(kwargs))
    print(kwargs)


foo(1, 2, 3, 4,e=5,f=6)
```
观察输出
```bash
<class 'tuple'>
(1, 2, 3, 4)
<class 'dict'>
{'e': 5, 'f': 6}
```
args被收集为tuple类型，kwargs被收集为dict类型。
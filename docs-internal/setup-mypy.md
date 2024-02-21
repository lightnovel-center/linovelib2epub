# 类型提示

## Installation

```bash
pip install mypy
# update requirement_*.txt if needed
```

## Usage
```bash
mypy example.py --pretty
# strict mode
mypy example.py --strict

# generate *.pyi file
stubgen foo.py
```

> In Python 3.10, you no longer need to import Union at all. All the details are in PEP 604. 
The PEP allows you to replace it entirely with the | operator.


## toml

设置 strict = True 后，mypy 会应用更严格的类型检查，包括但不限于以下内容：
- check_untyped_defs：检查未注释的函数和变量是否有类型注解。
- disallow_untyped_calls：不允许调用未注释的函数而没有类型注解。
- disallow_untyped_defs：不允许函数和变量没有类型注解。
- disallow_incomplete_defs：不允许函数和方法的部分参数有类型注解，所有参数必须有注解。
- disallow_untyped_decorators：不允许装饰器未注释

## 步骤

渐进式改善：

1. 先不打开strict模式，开始修复
2. 打开strict 模式，接着修复

## issues

### 1. Library stubs not installed for "pkg_resources"
> mypy --install-types
# 建立github action构建流程

参考教程：
> - [Publishing package distribution releases using GitHub Actions CI/CD workflows](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
> - https://github.com/pypa/gh-action-pypi-publish
> - https://docs.github.com/cn/actions/automating-builds-and-tests/building-and-testing-python

## trigger github actions
### 1. by a specific commit message
```yml
jobs:
  deploy:

    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.7"]
    # "PUBLISH-PYPI" or "PUBLISH-TESTPYPI" is treated as a command
    if: "contains(github.event.head_commit.message, 'PUBLISH-')"
```
The workflow will run, then skip if the commit message contains "PUBLISH-".

### 2. by a specific file changed
> - https://stackoverflow.com/a/72617099
> - https://docs.github.com/cn/actions/using-workflows/triggering-a-workflow#accessing-and-using-event-properties

这种方式在特定文件内容发生变更时，触发工作流程。因此，如果PUSH一个VERSION文件的变更，将会触发工作流。

显然，这个方式是非常合理的。免去了`by a specific commit message`方式的额外负担（因为需要运行，然后忽略）。

下面问题来了，应该如何在pyproject.toml中读取VERSION文件的内容作为 version 字段的值呢？
> https://stackoverflow.com/questions/71412385/can-python-snippets-be-placed-in-pyproject-toml

修改pyproject.toml
```toml
[project]
dynamic = ["version"]

[tool.hatch.version]
path = "src/linovelib2epub/__about__.py"
```
这里，使用了src/linovelib2epub/__about__.py作为VERSION BUMP的唯一源头。

现在就可以更改github action的build file了。

目标：当 __about__.py 文件发生更改时，触发PUBLISH流程。
```yml
on:
  push:
    paths:
      - 'src/linovelib2epub/__about__.py'

...
```
这里有一个明显的弊端/隐患，**这里将`__about__.py`文件内容的变更等同于视为其中__version__字段的变更**
，这种假设不合理。因为有时`__about__.py`会因为编辑器配置或者添加注释等其他行为而改变，
此时，也会触发PUBLISH流程。

更好的做法是github action能够在`on->push`字段下存在一种检测机制：检测某个特定文件的某个字段是否变更。
否则，优雅地根据version字段触发更新就无从谈起。

### 小结
根据上面的讨论，`by a specific file changed`这种机制目前而言还是残缺状态，因此推荐第一种方式：`by a specific commit message`,
即使它存在需要先运行然后退出的额外负担，但是它很简单，语义性很强。

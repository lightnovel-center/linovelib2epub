# 建立github action构建流程

参考教程：
> - [Publishing package distribution releases using GitHub Actions CI/CD workflows](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
> - https://github.com/pypa/gh-action-pypi-publish
> - https://docs.github.com/cn/actions/automating-builds-and-tests/building-and-testing-python

## trigger github actions
### by a specific commit message
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

### by a specific file changed
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

那么，现在就可以更改github action的build file了。
```yml
on:
  push:
    paths:
      - '**__about__.py'
```


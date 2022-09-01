# 如果发布一个python库到pip

这篇文章介绍的是使用toml配置(hatchling/setuptools)+ build + twine的工具链。

## 教程资源

- [Python Packaging User Guide](https://packaging.python.org/en/latest/#python-packaging-user-guide)
- [pypa sample project](https://github.com/pypa/sampleproject/)
- [Configuring a .pypirc File for Easier Python Packaging](https://truveris.github.io/articles/configuring-pypirc/)

## 过程描述

1. 使用VCS管理项目文件Tree
2. 使用TOML文件定义package的metadata，可以看作一系列的key-value pairs。
3. 决定build artifacts的形式，sdist（源码形式）或者wheel（二进制形式）
    1. sdist：A source distribution contains enough to install the package from source in an end user’s Python
       environment.
   ```bash
   python3 -m build --sdist source-tree-directory
   ```

    2. wheel：A built distribution contains only the files needed for an end user’s Python environment.

    ```bash
    python3 -m build --wheel source-tree-directory
    ```

4. 使用工具库将构架结果push到pypi，常见工具有twine。

```bash
twine upload dist/package-name-version.tar.gz dist/package-name-version-py3-none-any.whl
```

5. 下载package和安装

```bash
python3 -m pip install package-name
```

## 使用pipenv管理依赖

```
pip install --user --upgrade pipenv
```

然后将pipenv的路径添加到PATH环境变量，示例路径如下：

> C:\Users\wdpm\AppData\Roaming\Python\Python37\Scripts

```bash
mkdir test && cd test
pipenv install requests
```

输出log：

```bash
C:\Users\wdpm\test>pipenv install requests
Installing requests...
Adding requests to Pipfile's [packages]...
Installation Succeeded
Pipfile.lock not found, creating...
Locking [packages] dependencies...
           Building requirements...
Resolving dependencies...
Success!
Locking [dev-packages] dependencies...
Updated Pipfile.lock (444a6d)!
Installing dependencies from Pipfile.lock (444a6d)...
  ================================ 0/0 - 00:00:00
To activate this project's virtualenv, run pipenv shell.
Alternatively, run a command inside the virtualenv with pipenv run.
```

然后，可以利用`pipenv shell`直接激活虚拟环境。

```
C:\Users\wdpm\test>pipenv shell
Launching subshell in virtual environment...
Microsoft Windows [版本 10.0.19044.1889]
(c) Microsoft Corporation。保留所有权利。

(wdpm-9608vG8M) C:\Users\wdpm>
```

或者，根据这句提示：

> Alternatively, run a command inside the virtualenv with pipenv run.

找到该路径：`C:\Users\wdpm\.virtualenvs\wdpm-9608vG8M`

在这个路径下，存在Scripts目录，观察里面的文件：

```
wdpm@DESKTOP-QLDBOG2 MINGW64 ~/.virtualenvs/wdpm-9608vG8M/Scripts
$ ll
total 2026
-rw-r--r-- 1 wdpm 197121   2171 Aug 24 15:38 activate
-rw-r--r-- 1 wdpm 197121   1011 Aug 24 15:38 activate.bat
-rw-r--r-- 1 wdpm 197121   3048 Aug 24 15:38 activate.fish
-rw-r--r-- 1 wdpm 197121   2607 Aug 24 15:38 activate.nu
-rw-r--r-- 1 wdpm 197121   1766 Aug 24 15:38 activate.ps1
-rw-r--r-- 1 wdpm 197121   1169 Aug 24 15:38 activate_this.py
-rw-r--r-- 1 wdpm 197121    510 Aug 24 15:38 deactivate.bat
-rw-r--r-- 1 wdpm 197121    682 Aug 24 15:38 deactivate.nu
-rwxr-xr-x 1 wdpm 197121 107929 Aug 24 15:45 normalizer.exe*
-rwxr-xr-x 1 wdpm 197121 107906 Aug 24 15:38 pip-3.7.exe*
-rwxr-xr-x 1 wdpm 197121 107906 Aug 24 15:38 pip.exe*
-rwxr-xr-x 1 wdpm 197121 107906 Aug 24 15:38 pip3.7.exe*
-rwxr-xr-x 1 wdpm 197121 107906 Aug 24 15:38 pip3.exe*
-rw-r--r-- 1 wdpm 197121     24 Aug 24 15:38 pydoc.bat
-rwxr-xr-x 1 wdpm 197121 522768 Aug 24 15:38 python.exe*
-rwxr-xr-x 1 wdpm 197121 522256 Aug 24 15:38 pythonw.exe*
-rwxr-xr-x 1 wdpm 197121 107893 Aug 24 15:38 wheel-3.7.exe*
-rwxr-xr-x 1 wdpm 197121 107893 Aug 24 15:38 wheel.exe*
-rwxr-xr-x 1 wdpm 197121 107893 Aug 24 15:38 wheel3.7.exe*
-rwxr-xr-x 1 wdpm 197121 107893 Aug 24 15:38 wheel3.exe*
```

其中activate和deactivate分别表示激活和反激活虚拟环境。

## package example project

```bash
packaging_tutorial/
├── LICENSE
├── pyproject.toml
├── README.md
├── src/
│   └── example_package_YOUR_USERNAME_HERE/
│       ├── __init__.py
│       └── example.py
└── tests/
```

`__init__.py` 这个就是python中package的概念，类似于namespace，起到命名空间隔离的作用。内容可为空。

`example.py`为示例python文件。

```python
def add_one(number):
    return number + 1
```

> take a few minutes to read over the [Python documentation for packages and modules](https://docs.python.org/3/tutorial/modules.html#packages).

### Edit pyprojejct.toml

If using hatch:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

If using setuptools:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

configure other metadata:

```toml
[project]
name = "example_package_YOUR_USERNAME_HERE"
version = "0.0.1"
authors = [
    { name = "Example Author", email = "author@example.com" },
]
description = "A small example package"
readme = "README.md"
license = { file = "LICENSE" }
requires-python = ">=3.7"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.urls]
"Homepage" = "https://github.com/pypa/sampleproject"
"Bug Tracker" = "https://github.com/pypa/sampleproject/issues"
```

此外，常见的字段还有 `keywords` 来提高搜索度，和  `dependencies` 来定义你这个package的依赖库。

## build distribution files

```
py -m pip install --upgrade build
```

```
py -m build

# Only build wheel
py -m build --wheel
```

输出log：

```bash
* Creating virtualenv isolated environment...
* Installing packages in isolated environment... (hatchling)
* Getting dependencies for sdist...
* Building sdist...
* Building wheel from sdist
* Creating virtualenv isolated environment...
* Installing packages in isolated environment... (hatchling)
* Getting dependencies for wheel...
* Building wheel...
Successfully built example_package_wdpm-0.0.1.tar.gz and example_package_wdpm-0.0.1-py3-none-any.whl
```

dist/ 文件夹下生成了两个文件。分别对应源码模式(sdist)和二进制模式(whl)。

解压 example_package_wdpm-0.0.1.tar.gz 文件，并打印里面文件列表：

```
-rw-r--r-- 1 wdpm 197121 1082 Feb  2  2020 LICENSE
-rw-r--r-- 1 wdpm 197121 1794 Feb  2  2020 PKG-INFO
-rw-r--r-- 1 wdpm 197121   61 Feb  2  2020 README.md
-rw-r--r-- 1 wdpm 197121  733 Feb  2  2020 pyproject.toml
drwxr-xr-x 1 wdpm 197121    0 Aug 24 17:10 src/
```

发现VCS仓库的所有文件一并被打包进入了。这或许是一个问题， 更灵活的做法是精确地挑选需要打包的文件列表。

## Uploading the distribution archives

前往 [testPYPI](https://test.pypi.org/account/register/) 注册一个账户。验证邮箱后在 https://test.pypi.org/manage/account/#api-tokens
页面创建一个全局的token。

```
Token for "upload packages"
Permissions: Upload packages
Scope: Entire account (all projects)

pypi-AgENdGVzdC5weXBpLm9yZwIkMDg4NTNkZWUtZTg0Mi00NTIxLTlkNWQtMjdhNDJkNzFiNTQwAAIleyJwZXJtaXNzaW9ucyI6ICJ1c2VyIiwgInZlcnNpb24iOiAxfQAABiCdvE469IJiVlVxh_cuPbT38hPUgL7KdwFlf5wkxeAhQA
```

For example, if you are using [Twine](https://pypi.org/project/twine/) to upload your projects to PyPI, set up
your `$HOME/.pypirc` file like this:

> https://packaging.python.org/en/latest/specifications/pypirc/

```
[testpypi]
  username = __token__
  password = pypi-AgENdGVzdC5weXBpLm9yZwIkMDg4NTNkZWUtZTg0Mi00NTIxLTlkNWQtMjdhNDJkNzFiNTQwAAIleyJwZXJtaXNzaW9ucyI6ICJ1c2VyIiwgInZlcnNpb24iOiAxfQAABiCdvE469IJiVlVxh_cuPbT38hPUgL7KdwFlf5wkxeAhQA
```

For further instructions on how to use this token, [visit the PyPI help page](https://test.pypi.org/help#apitoken).

### use [twine](https://packaging.python.org/en/latest/key_projects/#twine) to upload the distribution packages

```
py -m pip install --upgrade twine
```

```
py -m twine upload --repository testpypi dist/*
# py -m twine upload --repository testpypi dist/*.whl
```

当询问账号和密码时，使用上面的账号和密码值。

过程log：

```bash
D:\Code\PycharmProjects\python-package-sample>py -m twine upload --repository testpypi dist/*
Uploading distributions to https://test.pypi.org/legacy/
Enter your username: __token__
Enter your password:
Uploading example_package_wdpm-0.0.1-py3-none-any.whl
100% ---------------------------------------- 7.4/7.4 kB • 00:00 • ?
Uploading example_package_wdpm-0.0.1.tar.gz
100% ---------------------------------------- 6.1/6.1 kB • 00:00 • ?

View at:
https://test.pypi.org/project/example-package-wdpm/0.0.1/
```

## 一个注意点：源码根目录

上面的例子中，源码是位于项目根目录下的`src`文件夹。 通过观察社区的一些开源python package，发现有两种流派。

- 一种是采用src约定，所有源码位于src的子文件夹下。例如 `click`。
  ```
  ...
  src/
    click/
      __init__.py
  ```
- 一种是舍弃src约定，所有源码直接位于项目根目录下，以package名称命名文件夹。例如：`ebooklib`。
  ```
  ...
  ebooklib/
    __init__.py
  ```

两种流派都是可行的，其中:

- click 采用setup.cfg在配置文件夹指定src作为package_dir.
- ebooklib 不需要做额外的指定。
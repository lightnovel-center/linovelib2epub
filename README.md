# linovelib2epub

Crawl light novel from [哔哩轻小说(linovelib)](https://w.linovelib.com/) and convert to epub.

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg?style=flat)](https://github.com/pypa/hatch)
[![flake8](https://img.shields.io/badge/linter-flake8-brightgreen)](https://github.com/PyCQA/flake8)
[![Build and Publish](https://github.com/lightnovel-center/linovelib2epub/actions/workflows/build-and-publish.yml/badge.svg?branch=main)](https://github.com/lightnovel-center/linovelib2epub/actions/workflows/build-and-publish.yml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/linovelib2epub?color=blue&label=PyPI%20Download)
![PyPI](https://img.shields.io/pypi/v/linovelib2epub)
![Lines of code](https://www.aschey.tech/tokei/github/lightnovel-center/linovelib2epub)
[![Hits-of-Code](https://hitsofcode.com/github/lightnovel-center/linovelib2epub?branch=main)](https://hitsofcode.com/github/lightnovel-center/linovelib2epub/view?branch=main)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/lightnovel-center/linovelib2epub)

## preview
> A picture is worth a thousand words. Talk is cheap, show me the real effect.

![preview](./preview.gif)

> This demo use [this screen recorder tool](https://github.com/faressoft/terminalizer) to record.


## Features

- [x] flexible `has_illustration` and `divide_volume` option for epub output
- [x] support download a certain volume of a novel
- [x] built-in http request retry mechanism to improve network fault tolerance
- [x] built-in random browser user_agent through fake_useragent library
- [x] built-in strict integrity check about image download
- [x] built-in mechanism for saving temporary book data by pickle library
- [x] use multi-process to download images
- [x] support add custom css style to epub

## Supported  Websites (plan)

| 序号 | 网站名称             | 语言                 | 爬虫难度            | 支持进度 | 备注                 |
| ---- | -------------------- | -------- | -------------------- | ---- | ---- |
| 1    | [哔哩轻小说（Mobile）](https://w.linovelib.com/) | 简/繁 | 中😰 | :ok:     | 默认选项。 |
| 2    | [哔哩轻小说（Web）](https://www.linovelib.com/) | 简/繁 | 中😰 | 🚫        | 资源同Mobile，没必要。 |
| 3    | [轻之国度](https://www.lightnovel.us/) | 简/繁 | 高🤣👿 | 🚫 | 需要登录，轻币门槛，导航分类混乱。 |
| 4 | [无限轻小说](https://www.8novel.com/) | 繁 | 中😰 | ？ | 不用登录。一章多页。 |
| 5 | [轻小说文库](https://www.wenku8.net/) | 简/繁 | 中😰 | ？ | 需要登录。一章一页。 |
| 6 | [轻小说百科](https://lnovel.org/ ) | 简/繁 | 低😆 | ？ | 不用登录，一章一页。遗憾的是插图清晰度低。 |
| 7 | [真白萌](https://masiro.me/admin/novels ) | 简/繁 | 中😰 | ？ | 需要登录，一章一页。 |

> 爬虫友好度有两个重要指标：
> - 1.访问门槛。是否需要登陆以及积分。
> - 2.页面结构。一个章节多页渲染的视为中等难度。

如果你发现其他的很好轻小说目标源，资源丰富，更新及时，插图清晰，并且爬虫门槛合理的，可以在issue发起补充。

代码实现中对其他轻小说源的支持，关键是继承并重写这个 `BaseNovelWebsiteSpider` 类。
- 其他参考：https://github.com/ilusrdbb/lightnovel-pydownloader

## Usage

### install from source
1. clone this repo
```bash
git clone https://github.com/lightnovel-center/linovelib2epub.git
```
2. set up a clean local python venv
> See also: [creating-virtual-environments](https://docs.python.org/3/library/venv.html#creating-virtual-environments)

replace `py` with your real python command if needed. e.g. `python` or `python3`.

```bash
# new a venv
py -m venv venv

# activate venv
.\venv\Scripts\activate

# install dependencies
py -m pip install -r requirements.txt

# install this package in local
# under project root folder: linovelib2epub/
python -m pip install -e .
```

3. Now you can use this package as a pypi remote package.
```python
from linovelib2epub.linovel import Linovelib2Epub

# warning!: must run within __main__ module guard due to process spawn issue.
if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=3279)
    linovelib_epub.run()
```

### install from pypi
1. Install this package from pypi:
```
pip install linovelib2epub
```
2. create a python file and edit the content as follows:
```python
from linovelib2epub.linovel import Linovelib2Epub

# warning!: must run within __main__ module guard due to process spawn issue.
if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=3279)
    linovelib_epub.run()
```
If it finished without errors, you can see the epub file is under the folder where your python file is located.



## Options

| Parameters            | type    | required | default                         | description                                                 |
| --------------------- | ------- | -------- | ------------------------------- | ----------------------------------------------------------- |
| book_id               | number  | YES      | None                            | 书籍ID。                                                    |
| base_url              | string  | NO       | 'https://w.linovelib.com/novel' | 哔哩轻小说主页URL                                           |
| divide_volume         | boolean | NO       | False                           | 是否分卷                                                    |
| select_volume_mode     | boolean | NO       | False                           | 选择卷模式，它为True时 divide_volume 强制为True。                                                   |
| has_illustration      | boolean | NO       | True                            | 是否下载插图                                                |
| image_download_folder | string  | NO       | "images"                        | 图片下载临时文件夹. 不允许以相对路径../开头。               |
| pickle_temp_folder    | string  | NO       | "pickle"                        | pickle临时数据保存的文件夹。                                |
| http_timeout          | number  | NO       | 10                              | 一个HTTP请求的超时等待时间(秒)。代表connect和read timeout。 |
| http_retries          | number  | NO       | 5                               | 当一个HTTP请求失败后，重试的最大次数。                      |
| http_cookie           | string  | NO       | ''                              | 自定义HTTP cookie。                                         |
| custom_style_cover    | string  | NO       | ''               | 自定义cover.xhtml的样式                                     |
| custom_style_nav      | string  | NO       | ''               | 自定义nav.xhtml的样式                                       |
| custom_style_chapter  | string  | NO       | ''              | 自定义每章(?.xhtml)的样式                                   |
|disable_proxy |boolean|NO| True| 是否禁用所在的代理环境，默认禁用|


## Todo

- [ ] quality: setup pytest and codecov
- [ ] quality: setup more formatter and linter for maintainability

## Contributors
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-4-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/GOUKOU007"><img src="https://avatars.githubusercontent.com/u/40916324?v=4?s=60" width="60px;" alt="GokouRuri"/><br /><sub><b>GokouRuri</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3AGOUKOU007" title="Bug reports">🐛</a> <a href="https://github.com/lightnovel-center/linovelib2epub/commits?author=GOUKOU007" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/xxxfhy"><img src="https://avatars.githubusercontent.com/u/40598925?v=4?s=60" width="60px;" alt="xxxfhy"/><br /><sub><b>xxxfhy</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Axxxfhy" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://foxlesbiao.github.io/"><img src="https://avatars.githubusercontent.com/u/41581909?v=4?s=60" width="60px;" alt="lesfox"/><br /><sub><b>lesfox</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Afoxlesbiao" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://dongliteahouse.wordpress.com"><img src="https://avatars.githubusercontent.com/u/56831381?v=4?s=60" width="60px;" alt="Holence"/><br /><sub><b>Holence</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/commits?author=Holence" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## Acknowledgements

- [biliNovel2Epub](https://github.com/fangxx3863/biliNovel2Epub)

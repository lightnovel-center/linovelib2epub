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

## Features

- [x] flexible `has_illustration` and `divide_volume` option for epub output
- [x] built-in http request retry mechanism to improve network fault tolerance
- [x] built-in random browser user_agent through fake_useragent library
- [x] built-in strict integrity check about image download
- [x] built-in mechanism for saving temporary book data by pickle library
- [x] use multi-process to download images
- [x] support add custom css style to epub


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

- [ ] (docs) add gif demo for preview
- [ ] (refactor) use multi-thread or asyncio coroutine to download images
- [ ] (refactor) refactor code to several abstract level(user-input/http/crawl/write ebook)
- [ ] (improvement) logging level info or succinct
- [ ] (feat) enable a download certain chapter of one book.
  - refer: playground/test_rich/rich_prompt.py
- [ ] (quality) setup pytests and codecov
- [ ] (chore) support more data provider：
  - lightnovel 轻之国度 
  - https://www.wenku8.net/ 轻小说文库 （简/繁) 【插图清晰度高】
  - https://lnovel.org/ 轻小说百科（简/繁）【插图清晰度低】
  - https://www.8novel.com/ 无限轻小说（繁）【插图清晰度高】

## Contributors
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/GOUKOU007"><img src="https://avatars.githubusercontent.com/u/40916324?v=4?s=100" width="100px;" alt="GokouRuri"/><br /><sub><b>GokouRuri</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3AGOUKOU007" title="Bug reports">🐛</a> <a href="https://github.com/lightnovel-center/linovelib2epub/commits?author=GOUKOU007" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/xxxfhy"><img src="https://avatars.githubusercontent.com/u/40598925?v=4?s=100" width="100px;" alt="xxxfhy"/><br /><sub><b>xxxfhy</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Axxxfhy" title="Bug reports">🐛</a></td>
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

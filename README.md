```diff
+ 🚀 真白萌小说站 https://masiro.me 已经得到支持 🚀
+ 🚩 轻小说文库 https://www.wenku8.net/login.php 已经得到支持 🚩
```

# linovelib2epub

Crawl light novel from some websites and convert it to epub.

| 指标分类             | 指标集                                                                                                                                                                                                                                                                                                                                                          |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Software Version | [![Python Version](https://img.shields.io/badge/python>=3.10-blue)]()[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg?style=flat)](https://github.com/pypa/hatch)                                                                                                                                                          |
| Code Style       | [![flake8](https://img.shields.io/badge/linter-flake8-brightgreen)](https://github.com/PyCQA/flake8)                                                                                                                                                                                                                                                         |
| Code Statistics  | ![Lines of code](https://www.aschey.tech/tokei/github/lightnovel-center/linovelib2epub) ![PyPI - Downloads](https://img.shields.io/pypi/dm/linovelib2epub?color=blue&label=PyPI%20Download)                                                                                                                                                                  |
| Code Activity    | [![Hits-of-Code](https://hitsofcode.com/github/lightnovel-center/linovelib2epub?branch=main)](https://hitsofcode.com/github/lightnovel-center/linovelib2epub/view?branch=main) ![GitHub commit activity](https://img.shields.io/github/commit-activity/y/lightnovel-center/linovelib2epub)                                                                   |
| Code Quality     | [![Maintainability](https://api.codeclimate.com/v1/badges/c1a9eb78a26e8ffb1fdf/maintainability)](https://codeclimate.com/github/lightnovel-center/linovelib2epub/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/c1a9eb78a26e8ffb1fdf/test_coverage)](https://codeclimate.com/github/lightnovel-center/linovelib2epub/test_coverage) |
| CI Status        | [![Build and Publish](https://github.com/lightnovel-center/linovelib2epub/actions/workflows/build-and-publish.yml/badge.svg?branch=main)](https://github.com/lightnovel-center/linovelib2epub/actions/workflows/build-and-publish.yml)                                                                                                                       |

！该项目可能会用到OCR引擎来识别网页上混淆的文本片段，但是目前市面上很多OCR引擎对python新版本的跟进非常滞后，因此推荐取下限而不是上限。
对于该项目，推荐锁定**python 3.10**版本。

## preview

> A picture is worth a thousand words. Talk is cheap, show me the real effect.

![preview](./preview.gif)

> This demo uses [this screen recorder tool](https://github.com/faressoft/terminalizer) to record.

## Features

- [x] flexible `has_illustration` and `divide_volume` option for epub output
- [x] support downloading a certain volume of a novel
- [x] built-in http request retry mechanism to improve network fault tolerance
- [x] built-in random browser user_agent through fake_useragent library
- [x] built-in strict integrity check about image download
- [x] built-in mechanism for saving temporary book data by pickle library
- [x] use asyncio/multiprocessing to download images
- [x] support adding custom css styles to epub

## 使用注意事项

在愉快的自动化爬虫之前，有必要进行声明。
网页 Web
端总会存在请求错误，请求延迟，还需要不断手动来点击【下一页】按钮来浏览阅读，这无疑打断了正常的阅读 [心流](https://zh.wikipedia.org/wiki/
心流理論 )。
此项目的初衷正是为了 ** 构造良好流畅、不间断的轻小说本地阅读体验 **。

但是，这不应该成为加重目标网站运行负载的理由。请正常使用本项目，请勿用于线性探测下载，或无限遍历下载。

免责声明：此项目不能保证它不会遭到滥用，对于有可能引发的不良后果，本项目概不负责。

## Supported  Websites (plan)

| 序号 | 网站名称                                         | 语言    | 爬虫难度 | 支持进度                                         | 备注                           | 技术难点                                                     |
|----|----------------------------------------------|-------|------|----------------------------------------------|------------------------------|----------------------------------------------------------|
| 1  | [哔哩轻小说（Mobile）](https://w.linovelib.com/)    | 简 / 繁 | 中😰  | <img src="./merrli.png" width="36">          | ` 不用登录 ` ` 一章多页 `            | `JS 文本混淆 ` `JS 文件随机 ` ` 章节链接破损 ` `Cloudflare 保护 ` ` 限流 ` |
| 2  | ~~[哔哩轻小说（Web）](https://www.linovelib.com/)~~ | 简 / 繁 | 中😰  | <img src="./tearlaments-ban.png" width="36"> | 资源同 Mobile，没必要。              | N/A                                                      |
| 3  | ~~[轻之国度](https://www.lightnovel.us/)~~       | 简 / 繁 | 高🤣  | <img src="./tearlaments-ban.png" width="36"> | ` 需要登录 `                     | ` 轻币门槛 ` ` 导航混乱 `                                        |
| 4  | ~~[无限轻小说](https://www.8novel.com/)~~         | 繁     | 中😰  | <img src="./tearlaments-ban.png" width="36"> | ` 不用登录 ` ` 一章多页 `            | N/A                                                      |
| 5  | [轻小说文库](https://www.wenku8.net/)             | 简 / 繁 | 低😆  | <img src="./merrli.png" width="36">          | ` 不用登录 ` ` 一章一页 `            | 无                                                        |
| 6  | ~~[轻小说百科](https://lnovel.org/)~~             | 简 / 繁 | 低😆  | <img src="./tearlaments-ban.png" width="36"> | ` 不用登录 ` ` 一章一页 ` ` 插图清晰度低 ` | N/A                                                      |
| 7  | [真白萌](https://masiro.me/admin/novels)        | 简 / 繁 | 中😰  | <img src="./merrli.png" width="36">          | ` 一章一页 `                     | ` 需要登录 ` ` 积分购买 ` ` 等级限制 ` `CF turnstile` ` 限流 `         |
| 8  | [百合会新站](https://www.yamibo.com/site/novel)   | 简 / 繁 | 中😰  | 搁置                                           | ` 可选 [登录]` ` 一章一页 `          | ` 付费章节需要登录 ` ` coin 购买 `                                 |

爬虫友好度有两个重要指标：

1. 访问门槛。是否需要登陆、积分 / 代币购买，等级限制。
2. 页面结构。一章多页，或者一章一页。

优质的轻小说目标源标准：资源丰富，更新迅速，插图清晰，爬虫门槛合理。可以在 issue 发起补充。

## Installation

### install from source

1. clone this repo

```bash
git clone https://github.com/lightnovel-center/linovelib2epub.git
```

2. set up a clean local python venv

> See also: [creating-virtual-environments](https://docs.python.org/3/library/venv.html#creating-virtual-environments)

replace `py` with your real python command if needed. e.g. `python` or `python3`.

```bash
# Make sure you are under this project root folder: linovelib2epub/
# The following instructions are based on Windows 10.
# If you use a different os, please adjust it according to the actual situation.

# new a venv
py -m venv .venv

# activate venv
.\.venv\Scripts\activate

# install dependencies
py -m pip install -r requirements.txt

# install this package in local
python -m pip install -e .
```

## Some issues you might encounter during installation

> Microsoft Visual C++ 14.0 or greater is required

See this
link: [Which Microsoft Visual C++ compiler to use with a specific Python version ?](https://wiki.python.org/moin/WindowsCompilers#Which_Microsoft_Visual_C.2B-.2B-_compiler_to_use_with_a_specific_Python_version_.3F)

| **Visual C++** | **CPython**          |
|----------------|----------------------|
| 14.x           | 3.5 - 3.12+          |
| 10.0           | 3.3 - 3.4            |
| 9.0            | 2.6 - 2.7, 3.0 - 3.2 |

The key point is:

- Install [Microsoft Build Tools for Visual Studio 2019](https://visualstudio.microsoft.com/vs/older-downloads/). The
  version greater than 2019 may also can work.
- In Build tools, install `C++ build tools` and ensure the latest versions of
  `MSVCv142 - VS 2019 C++ x64/x86 build tools` and `Windows 10 SDK` are checked.
- The `setuptools` Python package version must be at least 34.4.0.

---

> Could not find function xmlCheckVersion in library libxml2. Is libxml2 installed?

Rollback python version to 3.10.X can work. The exact root cause is unknown now.

## Usage

### Linovelib

> target site: https://w.linovelib.com

> 2024-3-19 Update: Now linovelib also has a cloudflare access protection and requests rate limit.
> In order to decrease the probability of being banned by Linovelib, it is highly recommended to set the delay
> parameters as follows.
> You can tune the delay parameters to fit your actual network environment.
>
> The Linovelib target requires OCR technique to recognize some paragraphs in html. You need
> to install [tesseract](https://github.com/UB-Mannheim/tesseract) on your local pc. Make sure the `tesseract` command
> works
> in your pc by appending its location to system/user variables.

LinovelibMobile has two language versions(`zh/zh-CN` or `zh-TW/zh-HK`)  and two UI version(PC or mobile).

So the target website has 2 x 2 = 4 choices.

| website version                    | visit method                                                      | support status | target_site                               |
|------------------------------------|-------------------------------------------------------------------|----------------|-------------------------------------------|
| [PC](www.linovelib.com)  简体        | browser set `zh/zh-CN` lang + click [简体化]                         | ✅(recommend)   | `TargetSite.LINOVELIB_PC`                 |
| [PC](www.linovelib.com)  繁体        | browser set `zh/zh-CN` lang + click [繁體化]                         | ✅              | `TargetSite.LINOVELIB_PC_TRADITIONAL`     |
| ~~[Mobile 简体](www.bilinovel.com)~~ | ~~browser set `zh/zh-CN` lang~~                                   | ❌              | `TargetSite.LINOVELIB_MOBILE`             |
| [Mobile](www.bilinovel.com)  繁体    | browser set `zh-TW/zh-HK` lang or not in Chinese Mainland network | ✅*(recommend)  | `TargetSite.LINOVELIB_MOBILE_TRADITIONAL` |

> 1.❌*: [2024-10-29]Now drission page library can only visit [mobile traditional version](www.bilinovel.com).
>
> 2.The Button "简体化" in mobile traditional version does not work. So `TargetSite.LINOVELIB_MOBILE` target doesn't
> work. No workaround now.

Create a python file(e.g. `usage_demo.py`) and edit the content as follows:

Example usages:

- Specify target_site:

The code below takes PC + `zh/zh-CN` version as an example, adjust as needed if your target version is different.

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=2356, target_site=TargetSite.LINOVELIB_PC)

    # linovelib_epub = Linovelib2Epub(book_id=2356,target_site=TargetSite.LINOVELIB_PC_TRADITIONAL)

    # linovelib_epub = Linovelib2Epub(book_id=2356,target_site=TargetSite.LINOVELIB_MOBILE_TRADITIONAL)
    linovelib_epub.run()
```

- Set delay-related parameters[**mandatory**]

```python
from linovelib2epub import Linovelib2Epub

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=2356, target_site=TargetSite.LINOVELIB_PC)
    linovelib_epub.run()
```

The default value of `chapter_crawl_delay` and `page_crawl_delay` are None. You MUST set them to reasonable values.

The example code is as follows to set the value of all delay parameters.

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=3721, target_site=TargetSite.LINOVELIB_PC,
                                    chapter_crawl_delay=5, page_crawl_delay=5)
    linovelib_epub.run()
```

- download only selected volume(s)[**optional**]

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == "__main__":
    linovelib_epub = Linovelib2Epub(book_id=2356, target_site=TargetSite.LINOVELIB_PC,
                                    select_volume_mode=True
                                    )
    linovelib_epub.run()
```

- disable network proxy[**optional**]

This project will disable any proxy settings when crawling. So you should manually activate it by `disable_proxy=False`
if you want to use your local proxy.

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == "__main__":
    linovelib_epub = Linovelib2Epub(book_id=2356, target_site=TargetSite.LINOVELIB_PC,
                                    disable_proxy=False,
                                    )
    linovelib_epub.run()
```

- view more details about crawling[**optional**]

Due to time sensitivity or environmental differences, web crawlers are very prone to failure. You can view more of the
underlying details if turn on debug mode.

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == "__main__":
    linovelib_epub = Linovelib2Epub(book_id=2356, target_site=TargetSite.LINOVELIB_PC,
                                    log_level="DEBUG",
                                    )
    linovelib_epub.run()
```

For more options, see the `Options` chapter below.

---

The following is a common crawler configuration that can be used as a reference.

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == "__main__":
    linovelib_epub = Linovelib2Epub(book_id=2356, target_site=TargetSite.LINOVELIB_PC,
                                    chapter_crawl_delay=5, page_crawl_delay=5,
                                    select_volume_mode=True,
                                    # disable_proxy=False,
                                    # log_level="DEBUG",
                                    )
    linovelib_epub.run()
```

If it finished without errors, you can see the epub file is under the folder where your python file is located.

### Masiro

> target site: https://masiro.me

> 2024-02-22 Update: Now Masiro has a very strict cloudflare turnstile protection and requests rate limit. The code has
> been
> refactored to bypass the [cloudflare turnstile](https://www.cloudflare.com/zh-cn/products/turnstile/) using a python
> library called [DrissionPage](https://github.com/g1879/DrissionPage). DrissionPage will auto-detect and use Chrome
> browser.
> If you encounter a path error of Chrome browser, please set the `browser_path` parameter to `Linovelib2Epub()`.

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=1039, target_site=TargetSite.MASIRO)
    linovelib_epub.run()
```

Or specify browser path:

```python
from linovelib2epub import Linovelib2Epub, TargetSite

# Chromium-based browser is ok
browser_path = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=1039, target_site=TargetSite.MASIRO, browser_path=browser_path)
    linovelib_epub.run()
```

Masiro is not the default target site, so you MUST specify `target_site` parameter as above.

And Masiro website need user login credential to view novel. You also MUST to create a config file named `.secrets.toml`
beside your python file `usage_demo.py`. For better explanation, Here's a reasonable directory organization:

```
linovelib2epub/
  ......
  .secrets.toml
  usage_demo.py
```

Then edit your `.secrets.toml` file:

```
MASIRO_LOGIN_USERNAME = '<your-masiro-username>'
MASIRO_LOGIN_PASSWORD = '<your-masiro-password>'
```

🚨 Don't leak your private account info!!! Be careful.

> Masiro 某些小说存在用户等级限制，程序执行会发生什么？

程序会给出提示，并直接退出。

> Masiro 某些小说的章节需要积分购买才能查看，程序会如何处理？

登陆后，程序会记住你的当前积分余额：

- 如果当前挑选的所有章节都是免费积分，或者你之前已经全部购买过，那么程序会直接往下执行。
- 如果当前挑选的所有章节存在需要积分购买的情况，程序会再次提示，要求做出选择，此时可以选择退出或者选择继续。

### Wenku8

> target site: https://www.wenku8.net

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=2961, target_site=TargetSite.WENKU8)
    linovelib_epub.run()
```

Don't need login, no threshold.

## Options

| Parameters                | type    | required | default        | description                                                                                                  |
|---------------------------|---------|----------|----------------|--------------------------------------------------------------------------------------------------------------|
| book_id                   | number  | YES      | None           | 书籍 ID。                                                                                                       |
| target_site               | Enum    | YES      | None           | 参阅 TargetSite python 枚举类以及使用文档。                                                                              |
| chapter_crawl_delay       | number  | YES*     | None           | 爬取每个章的延迟秒数 (s)。合理设置此参数可以降低被限流系统限制的频率。目标是 linovelib 时必须设置此参数。                                                 |
| page_crawl_delay          | number  | YES*     | None           | 对于特定章，爬取每个页面的延迟秒数 (s)。合理设置此参数可以降低被限流系统限制的频率。目标是 linovelib 时必须设置此参数 。                                         |
| divide_volume             | boolean | NO       | False          | 是否分卷                                                                                                         |
| select_volume_mode        | boolean | NO       | False          | 选择卷模式，它为 True 时 divide_volume 强制为 True。                                                                      |
| has_illustration          | boolean | NO       | True           | 是否下载插图                                                                                                       |
| image_download_folder     | string  | NO       | "novel_images" | 图片下载临时文件夹. 不允许以相对路径../ 开头。                                                                                   |
| pickle_temp_folder        | string  | NO       | "pickle"       | pickle 临时数据保存的文件夹。                                                                                           |
| clean_artifacts           | boolean | NO       | True           | 是否删除临时数据 / 工件，指的是 pickle 和下载的图片文件。                                                                           |
| crawling_contentid        | string  | NO       | None           | 用户自定义的正文内容的 id，用于快速响应网页结构变化，[如何获取?](docs/inspect-linovelib-contentid-as-a-regular-user.md)。目前仅适用于 linovelib。 |
| custom_style_cover        | string  | NO       | ''             | 自定义 cover.xhtml 的样式                                                                                          |
| custom_style_nav          | string  | NO       | ''             | 自定义 nav.xhtml 的样式                                                                                            |
| custom_style_chapter      | string  | NO       | ''             | 自定义每章 (?.xhtml) 的样式                                                                                          |
| disable_proxy             | boolean | NO       | True           | 是否禁用所在的代理环境，默认禁用。如果你在本地使用网络代理，请务必留意是否应该设置该参数。                                                                |
| image_download_strategy   | string  | NO       | 'ASYNCIO'      | 枚举值："ASYNCIO"、"MULTIPROCESSING"、"MULTITHREADING"（未实现）                                                        |
| image_download_max_epochs | number  | NO       | 10             | 图片下载的最大尝试轮数。超过这个值则认为是网络中断或者源图片缺失，自动放弃。                                                                       |
| browser_path              | string  | NO       | None           | 浏览器的本地绝对路径。                                                                                                  |
| headless                  | boolean | NO       | False          | 是否显示浏览器窗口，默认为 False，即默认显示。目前仅哔哩轻小说支持该参数。                                                                     |
| http_timeout              | number  | NO       | 10             | 一个 HTTP 请求的超时等待时间 (秒)。代表 connect 和 read timeout。目前仅应用于 linovelib 页面。                                         |
| http_retries              | number  | NO       | 10             | 当一个 HTTP 请求失败后，重试的最大次数。 目前仅应用于 linovelib 页面。                                                                 |

## Todo

- [] feat: add GOT-OCR2.0 engine alternative for linovelib site, support disable ocr(keep encrypted text.)
- [] feat: [option]add epubcheck for output files.
  see https://epubcheck.readthedocs.io/en/latest/readme.html#using-epubcheck-as-a-python-library
- [ ] quality: setup pytest and codecov
- [ ] quality: setup more formatter and linter for maintainability

## Under the hood

Here are some description about internal mechanism of this project.

| Target Site          | pages downloading | page success condition | challenge CloudFlare when page downloading | images downloading | use browser? |
|----------------------|-------------------|------------------------|--------------------------------------------|--------------------|--------------|
| Bilinovel(linovelib) | serial[^1]        | desired tag found      | No[^2]                                     | parallel           | DrissionPage |
| Masiro               | parallel[^3]      | desired tag found      | Yes                                        | parallel           | DrissionPage |
| Wenku8               | parallel          | simple status `200`    | N/A                                        | parallel           | aiohttp      |

[^1]: Bilinovel pages downloading is serial because its some chapter urls are broken, and we need to fix them.

[^2]: Bilinovel doesn't challenge CF when downloading one page, maybe it will stagnate into a endless loop.

[^3]: Masiro pages downloading is parallel but the actual effect is equal to serial because its strict requests rate
limit.

## Contributors

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-11-orange.svg?style=flat-square)](#contributors-)
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
      <td align="center" valign="top" width="14.28%"><a href="http://en.blog.nyaame.moe"><img src="https://avatars.githubusercontent.com/u/135048882?v=4?s=60" width="60px;" alt="Nikaidou Haruki"/><br /><sub><b>Nikaidou Haruki</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Aharuki-nikaidou" title="Bug reports">🐛</a> <a href="https://github.com/lightnovel-center/linovelib2epub/commits?author=haruki-nikaidou" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://hitorinbc.com/"><img src="https://avatars.githubusercontent.com/u/33192552?v=4?s=60" width="60px;" alt="kaho"/><br /><sub><b>kaho</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Akahosan" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Papersman"><img src="https://avatars.githubusercontent.com/u/58485012?v=4?s=60" width="60px;" alt="Papersman"/><br /><sub><b>Papersman</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3APapersman" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/inkroom"><img src="https://avatars.githubusercontent.com/u/27911304?v=4?s=60" width="60px;" alt="inkroom"/><br /><sub><b>inkroom</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Ainkroom" title="Bug reports">🐛</a> <a href="https://github.com/lightnovel-center/linovelib2epub/commits?author=inkroom" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Kuan-Lun"><img src="https://avatars.githubusercontent.com/u/33048725?v=4?s=60" width="60px;" alt="Kuan-Lun"/><br /><sub><b>Kuan-Lun</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3AKuan-Lun" title="Bug reports">🐛</a> <a href="https://github.com/lightnovel-center/linovelib2epub/commits?author=GOUKOU007" title="Code">💻</a> </td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/CutyIMoDo"><img src="https://avatars.githubusercontent.com/u/59514546?v=4?s=60" width="60px;" alt="CutyIMoDo"/><br /><sub><b>CutyIMoDo</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3ACutyIMoDo" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/sweetnotice"><img src="https://avatars.githubusercontent.com/u/106159757?v=4?s=60" width="60px;" alt="Neco_arc"/><br /><sub><b>Neco_arc</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Asweetnotice" title="Bug reports">🐛</a></td>
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

- [biliNovel2Epub](https://github.com/fangxx3863/biliNovel2Epub) => 哔哩轻小说参考。
- [lightnovel-pydownloader](https://github.com/ilusrdbb/lightnovel-pydownloader) => 真白萌 / 轻之国度 / 百合会旧站参考。
- [bili_novel_packer](https://github.com/Montaro2017/bili_novel_packer) => 哔哩轻小说 /wenku8 参考。

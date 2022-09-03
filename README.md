# linovelib2epub
Craw light novel from [哔哩轻小说(linovelib)](https://w.linovelib.com/) and convert to epub.

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg?style=flat)](https://github.com/pypa/hatch)
[![flake8](https://img.shields.io/badge/linter-flake8-brightgreen)](https://github.com/PyCQA/flake8)
[![Build and Publish](https://github.com/lightnovel-center/linovelib2epub/actions/workflows/build-and-publish.yml/badge.svg?branch=main)](https://github.com/lightnovel-center/linovelib2epub/actions/workflows/build-and-publish.yml)



## Features

- [x] flexible `has_illustration` and `divide_volume` option for epub output
- [x] built-in http request retry mechanism to improve network fault tolerance
- [x] built-in random browser user_agent through fake_useragent library
- [x] built-in strict integrity check about image download
- [x] built-in mechanism for saving temporary book data by pickle library
- [x] use multi-thread to download images



## Usage

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



## Todo

- [ ] (feat) utilize sigil to debug CSS rules for book style beautification
- [ ] (improvement) logging level: info or succinct
- [ ] (feat) enable a download certain chapter of one book.
- [ ] (docs) add more badges() on readme.
   - GitHub commit activity/codecov/tests/lines of code/PyPI - Downloads/PYPI version
  

## Known issues

See `docs/` folder.
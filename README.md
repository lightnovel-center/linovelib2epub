# linovelib2epub
Craw light novel from [哔哩轻小说(linovelib)](https://w.linovelib.com/) and convert to epub.

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)


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

3. For more options. 
> TODO

## Todo

- [ ] (feat) utilize sigil to debug CSS rules for book style beautification
- [ ] (devops) publish this library to PYPI not TestPyPI
- [ ] logging level: info or succinct

## Known issues

See `docs/` folder.
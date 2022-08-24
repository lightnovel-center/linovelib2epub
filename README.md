# linovelib2epub
Craw light novel from [哔哩轻小说(linovelib)](https://w.linovelib.com/) and convert to epub.

## Features

- [x] flexible `has_illustration` and `divide_volume` option for epub output
- [x] built-in http request retry mechanism to improve network fault tolerance
- [x] built-in random browser user_agent through fake_useragent library
- [x] built-in strict integrity check about image download
- [x] built-in mechanism for saving temporary book data by pickle library
- [x] use multi-thread to download images

## Usage
Install dependencies:
```
pip install -r requirement.txt
```
Install dependencies with proxy(For example, clash 7890 port):
```
pip install -r requirement.txt --proxy=http://127.0.0.1:7890
```

## todo

- [ ] (feat) utilize sigil to debug CSS rules for book style beautification
- [ ] (devops) publish this library to pip

## known issues

See `docs/` folder.
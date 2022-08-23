# linovelib2epub
Craw light novel from [哔哩轻小说(linovelib)](https://w.linovelib.com/) and convert to epub.

## Features

- [x] flexible `has_illustration` and `divide_volume` option for epub output
- [x] built-in http request retry mechanism to improve network fault tolerance
- [x] built-in random browser user_agent through fake_useragent library
- [x] built-in strict integrity check about image download
- [x] built-in mechanism for saving temporary book data by pickle library

## Usage
Install dependencies with proxy(optional)
```
pip install -r requirement.txt --proxy=http://127.0.0.1:7890
```

## todo

- [ ] (feat) enable to set custom cookie
- [ ] (docs) write tech and user guide
- [ ] (devops) publish this library to pip
- [ ] (feature) download a certain chapter of a book
- [ ] (chore) Investigate the release of Helloworld library

## known issues

See `docs/` folder.
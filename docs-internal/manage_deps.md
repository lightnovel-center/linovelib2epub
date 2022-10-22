# collect project dependencies
1. use pip
```bash
pip list
```
it will output too many dependencies(includes indirect and outside deps)
```
D:\Code\PycharmProjects\biliNovel2Epub>pip list
Package             Version
------------------- -----------
beautifulsoup4      4.11.1
bs4                 0.0.1
certifi             2022.6.15
cffi                1.15.1
charset-normalizer  2.1.0
commonmark          0.9.1
cryptography        37.0.4
cycler              0.11.0
EbookLib            0.17.1
idna                3.3
kiwisolver          1.4.4
lxml                4.9.1
markdown-word-count 0.0.1
matplotlib          3.4.3
numpy               1.21.6
Pillow              9.2.0
pip                 22.2.1
proxy-tools         0.1.0
pycparser           2.21
Pygments            2.12.0
pyOpenSSL           22.0.0
pyparsing           3.0.9
python-dateutil     2.8.2
pythonnet           2.5.2
PyUserInput         0.1.10
pywebview           3.5
requests            2.28.1
rich                12.5.1
setuptools          40.8.0
six                 1.16.0
soupsieve           2.3.2.post1
typing_extensions   4.3.0
urllib3             1.25.11
uuid                1.30
``` 
When use this command below to collect deps;
```bash
pip freeze > requirement_version.txt
```
output:
```bash
beautifulsoup4==4.11.1
bs4==0.0.1
certifi==2022.6.15
cffi==1.15.1
charset-normalizer==2.1.0
...
```
It can work. But now I want to collect only direct deps, I don't want to
collect indirect deps. What can we do next?

2. use other tools

- use `pipdeptree` to collect direct deps
- use `pip-autoremove` to purge needless deps

```
pip install pipdeptree
```
```
D:\Code\PycharmProjects\biliNovel2Epub>pipdeptree
bs4==0.0.1
  - beautifulsoup4 [required: Any, installed: 4.11.1]
    - soupsieve [required: >1.2, installed: 2.3.2.post1]
EbookLib==0.17.1
  - lxml [required: Any, installed: 4.9.1]
  - six [required: Any, installed: 1.16.0]
markdown-word-count==0.0.1
matplotlib==3.4.3
  - cycler [required: >=0.10, installed: 0.11.0]
  - kiwisolver [required: >=1.0.1, installed: 1.4.4]
    - typing-extensions [required: Any, installed: 4.3.0]
  - numpy [required: >=1.16, installed: 1.21.6]
  - pillow [required: >=6.2.0, installed: 9.2.0]
  - pyparsing [required: >=2.2.1, installed: 3.0.9]
  - python-dateutil [required: >=2.7, installed: 2.8.2]
    - six [required: >=1.5, installed: 1.16.0]
pipdeptree==2.2.1
  - pip [required: >=6.0.0, installed: 22.2.1]
pyOpenSSL==22.0.0
  - cryptography [required: >=35.0, installed: 37.0.4]
    - cffi [required: >=1.12, installed: 1.15.1]
      - pycparser [required: Any, installed: 2.21]
PyUserInput==0.1.10
pywebview==3.5
  - proxy-tools [required: Any, installed: 0.1.0]
  - pythonnet [required: Any, installed: 2.5.2]
    - pycparser [required: Any, installed: 2.21]
requests==2.28.1
  - certifi [required: >=2017.4.17, installed: 2022.6.15]
  - charset-normalizer [required: >=2,<3, installed: 2.1.0]
  - idna [required: >=2.5,<4, installed: 3.3]
  - urllib3 [required: >=1.21.1,<1.27, installed: 1.25.11]
rich==12.5.1
  - commonmark [required: >=0.9.0,<0.10.0, installed: 0.9.1]
  - pygments [required: >=2.6.0,<3.0.0, installed: 2.12.0]
  - typing-extensions [required: >=4.0.0,<5.0, installed: 4.3.0]
setuptools==40.8.0
uuid==1.30
```
If you want to purge a certain dep, type 
```
pip install pip-autoremove
pip-autoremove [certain-dep] -y
```

## Using pipdeptree to write requirements.txt file 
```bash
pipdeptree -f --warn silence | grep -E '^[a-zA-Z0-9\-]+' > requirements.txt
```
> If you are on windows (powershell) you can run pipdeptree --warn silence | Select-String -Pattern '^\w+' instead of grep
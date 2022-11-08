# 安装本地包
```bash
python -m pip install -e <path>
```
输出示例：
```bash
D:\Code\PycharmProjects\linovelib2epub>python -m pip install -e .
Looking in indexes: http://mirrors.aliyun.com/pypi/simple/
Obtaining file:///D:/Code/PycharmProjects/linovelib2epub
  Installing build dependencies ... done
  Checking if build backend supports build_editable ... done
  Getting requirements to build editable ... done
  Preparing editable metadata (pyproject.toml) ... done
Requirement already satisfied: fake-useragent>=0.1.11 in c:\python\python37\lib\site-packages (from linovelib2epub==0.0.9) (0.1.11)
Requirement already satisfied: bs4>=0.0.1 in c:\python\python37\lib\site-packages (from linovelib2epub==0.0.9) (0.0.1)
Requirement already satisfied: rich>=12.5.1 in c:\python\python37\lib\site-packages (from linovelib2epub==0.0.9) (12.5.1)
Requirement already satisfied: ebooklib>=0.17.1 in c:\python\python37\lib\site-packages (from linovelib2epub==0.0.9) (0.17.1)
Requirement already satisfied: demjson>=2.2.4 in c:\python\python37\lib\site-packages (from linovelib2epub==0.0.9) (2.2.4)
Requirement already satisfied: requests>=2.28.1 in c:\python\python37\lib\site-packages (from linovelib2epub==0.0.9) (2.28.1)
Requirement already satisfied: uuid>=1.30 in c:\python\python37\lib\site-packages (from linovelib2epub==0.0.9) (1.30)
Requirement already satisfied: beautifulsoup4 in c:\python\python37\lib\site-packages (from bs4>=0.0.1->linovelib2epub==0.0.9) (4.11.1)
Requirement already satisfied: lxml in c:\python\python37\lib\site-packages (from ebooklib>=0.17.1->linovelib2epub==0.0.9) (4.9.1)
Requirement already satisfied: six in c:\python\python37\lib\site-packages (from ebooklib>=0.17.1->linovelib2epub==0.0.9) (1.16.0)
Requirement already satisfied: urllib3<1.27,>=1.21.1 in c:\python\python37\lib\site-packages (from requests>=2.28.1->linovelib2epub==0.0.9) (1.26.12)
Requirement already satisfied: certifi>=2017.4.17 in c:\python\python37\lib\site-packages (from requests>=2.28.1->linovelib2epub==0.0.9) (2022.6.15)
Requirement already satisfied: idna<4,>=2.5 in c:\python\python37\lib\site-packages (from requests>=2.28.1->linovelib2epub==0.0.9) (3.3)
Requirement already satisfied: charset-normalizer<3,>=2 in c:\python\python37\lib\site-packages (from requests>=2.28.1->linovelib2epub==0.0.9) (2.1.0)
Requirement already satisfied: commonmark<0.10.0,>=0.9.0 in c:\python\python37\lib\site-packages (from rich>=12.5.1->linovelib2epub==0.0.9) (0.9.1)
Requirement already satisfied: typing-extensions<5.0,>=4.0.0 in c:\python\python37\lib\site-packages (from rich>=12.5.1->linovelib2epub==0.0.9) (4.3.0)
Requirement already satisfied: pygments<3.0.0,>=2.6.0 in c:\python\python37\lib\site-packages (from rich>=12.5.1->linovelib2epub==0.0.9) (2.12.0)
Requirement already satisfied: soupsieve>1.2 in c:\python\python37\lib\site-packages (from beautifulsoup4->bs4>=0.0.1->linovelib2epub==0.0.9) (2.3.2.post1)
Building wheels for collected packages: linovelib2epub
  Building editable for linovelib2epub (pyproject.toml) ... done
  Created wheel for linovelib2epub: filename=linovelib2epub-0.0.9-py3-none-any.whl size=15173 sha256=0c2607e9fe105ea9b3c66bc1ffacca152489641222f40b0f1ac4a0cda63946
44
  Stored in directory: C:\Users\wdpm\AppData\Local\Temp\pip-ephem-wheel-cache-rgguch0q\wheels\fd\85\e8\f92ff5a27aa82cd772a19c7d1d604f6461fdac0b9571c83216
Successfully built linovelib2epub
Installing collected packages: linovelib2epub
  Attempting uninstall: linovelib2epub
    Found existing installation: linovelib2epub 0.0.6
    Uninstalling linovelib2epub-0.0.6:
      Successfully uninstalled linovelib2epub-0.0.6
Successfully installed linovelib2epub-0.0.9

```

确认正常工作：

![image-20220905221837056](assets/image-20220905221837056.png)
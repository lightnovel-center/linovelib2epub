# 软件架构决策

由于项目逐步成长，最开始的一个主py文件 `linovel.py` 的代码行已经接近1000行，因此需要重构，以提高代码的可读性、可维护性、易测试性。

## 梳理项目的整个执行过程

```
1.[user_input] ---> 2.[crawl novel data] ---> 3.[write epub]
```

1. [user_input] - 处理用户输入的参数，合并配置。这一步生成爬虫的配置。
2. [crawl novel data] - 根据爬虫的配置，制定对应的爬虫策略，例如分卷/下载插图，进行爬虫。这一步得到一个LightNovel模型的数据。
3. [write epub] - 利用epub相关工具库，结合爬虫配置，输入epub文件。

## 用户设置
根据用户设置的不同：
- 选择模式，分卷(Y/N)。=>这部分设置影响正文内容的范围。
  - 分卷(N) => 【默认选项】。下载整本，输出一个整体的epub文件。
  - 分卷(Y) => 下载整本，输出文件时会单卷单个文件保存，输出一个或多个epub文件。
  - 选择模式 => 选择模式一定是卷分离模式（单卷单个文件），可以单选或者多选，输出一个或多个epub文件。
- 下载插图(Y/N)。
  - Y。下载插图。【默认选项】。
  - N。不下载插图。epub中对于插图的位置一般会显示为[Image]标注。
 
>设计1：下载插图的时机在哪个阶段？ 

如果用户设置需要插图，那么下载插图应该在爬虫阶段，还是写epub阶段？

## 定义LightNovel数据模型类
这个类用于表示爬虫得到的轻小说的数据。按层级来分，为 book -> volumes -> chapters -> pages。

也就是一本书有多个卷，每一卷有多个章节，每个章节有多个html 页面（也可以为一个html页面，不同网站的实现不同）。
- 哔哩轻小说为了减少一个章节的阅读压力，将一个章节切分为多个子页面，这样一个页面的数据就相对小一点。
- 而[无限轻小说](https://www.8novel.com/) 则是一个章节一个页面，这样对于爬虫很友好，但是对于常规阅读可以会发现页面滚动范围很长。

### Book
我们从最简单的代码开始思考：
```python
class LightNovel:
    # 省略书籍的其他元信息...
    bid = None
  
    class Volume:
        pass

    volumes: []
```
一本书至少需要一个book_id，这个book_id对于特定的网站而言，是唯一的。

### Volumes

这里volumes是一个array，里面的每一个元素，都是一个特定的卷volume，也就是Volume类的实例。

我们继续思考 Volume 中最为核心的数据结构是什么。一个volume应当有：

- volume id: 卷的id，唯一即可。一般可以选择自增。如果对应的爬虫网站有设计这个字段，可以采用原网站的设计。
- volume title：卷标题。
- volume chapters：对应这一卷的所有章节。每个章节都是class Chapter的实例。

```python
class Chapter:
    pass

class Volume:
    vid: None
    title: str
    chapters: []
```
现在我们来到了Chapter的内部设计阶段。

### Chapters

一个Chapter表示一个特定的章节。
- chapter id: 唯一。
- chapter index page title: 该章节的第一个页面的标题。
- chapter index page url: 该章节的第一个页面的url。
- chapter pages: 表示章节的页。

对于特定章节单页的网站：chapter pages 数组只有一个元素。
对于特定章节多页的网站：chapter pages 数组含有多个元素。

因此，现在可以给出Chapter的初步设计。

```python
class Chapter:
    cid: None
    index_page_title: str
    index_page_url: str
    pages: []
```

### Pages

最后，是Page的设计了。 每个page应该包含：
- page id
- page title
- page url
- page content
```python
class Page:
   pid: None
   title: str
   url: str
   content: str
```


## 爬虫关键的设计点

由于每个novel website的页面结构不同，应该抽象出一个抽象类，例如 NovelWebsite。 不同的网站，例如website-a,website-b应该继承自这个
基类，然后重写对应的方法实现。

BaseNovelWebsiteSpider 应该拥有以下的抽象方法：
- __init__ logger实例，爬虫配置（外部可以使用单例，因为这个配置一旦初始化就不可变）。
- @abstractmethod fetch()。爬取novel data的主方法。子类必须覆盖这个方法。
- default sanitize_html() implementation 默认的html消毒方法，例如剥离js脚本，转义部分字符等等。

不同的轻小说来源网站就是 BaseNovelWebsiteSpider 的子类。

但是此时会导致不同的用户调用时需要手动引入不同的子类，然后初始化。
为了让API更加简洁。可以使用facade模式，将API统一起来，内部委托到相应的spider。可以使用依赖注入将对应spider传入。

将普适的方法抽象泛化（上移）到基类 BaseNovelWebsiteSpider ，具体的方法实现特化（下移）在具体的实现类 LinovelibSpider。
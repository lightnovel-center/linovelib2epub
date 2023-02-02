# 测试用例

选定一个含有多卷的小说，卷数不适过大，3~5卷合适。

以这个例子来测试，含有三卷。
- BASE_URL = 'https://w.linovelib.com/novel'
- BOOK_ID = 1068

## 基本用例
divide_volume x has_illustration
```
linovelib_epub = Linovelib2Epub(book_id=1068, divide_volume=False,has_illustration=True)
linovelib_epub = Linovelib2Epub(book_id=1068, divide_volume=False,has_illustration=False)
linovelib_epub = Linovelib2Epub(book_id=1068, divide_volume=True,has_illustration=True)
linovelib_epub = Linovelib2Epub(book_id=1068, divide_volume=True,has_illustration=False)
```

## 选择卷模式
```
linovelib_epub = Linovelib2Epub(book_id=1068, has_illustration=False,select_volume_mode=True)
linovelib_epub = Linovelib2Epub(book_id=1068, has_illustration=True,select_volume_mode=True)
```
注意select_volume_mode启用时，divide_volume=True 必定为True。

## 清除缓存
这里缓存指的是：书籍的pickle数据，和本地保存的图片。由 CLEAN_ARTIFACTS 指定。
```
CLEAN_ARTIFACTS = True # 应该在输入epub后进行删除清理
CLEAN_ARTIFACTS = False #在输入epub后对应文件夹应该存在残留
```

## strip html js
```python
import re

text1 = """<body>before <script src="http://path/to"></script> some text</body>"""
text2 = """<body>before <script>zation();</script>asdf</body>"""

new_text_1 = re.sub(r'<script.+?</script>', '', text1, flags=re.DOTALL)
new_text_2 = re.sub(r'<script.+?</script>', '', text2, flags=re.DOTALL)
print(new_text_1)
print(new_text_2)
```

## set cookie

WIP

## disable proxy

WIP



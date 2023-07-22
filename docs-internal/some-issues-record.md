# 问题记录

## 1.图片下载超时误报
问题复现的步骤：
```python
linovelib_epub = Linovelib2Epub(book_id=3728, clean_artifacts=False)
```
错误记录：
![](./assets/Snipaste_2023-07-22_18-21-48.png)

极小概率会出现这种逻辑似乎不一致的情况。 暂时无法定位本质原因，这里仅是记录。
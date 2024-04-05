---
name: Bug report
about: Create a report to help us improve
title: "[BUG] 一句话描述这个BUG是什么"
labels: bug
assignees: ''

---

**Describe the bug（描述这个BUG）**
A clear and concise description of what the bug is.

**To Reproduce（复现步骤）**
复现的代码以及操作（例如分支选择、卷选择等等）

注意：请务必打开**DEBUG logging** 模式。示例代码：
```python
from linovelib2epub import Linovelib2Epub

if __name__ == '__main__':
    # /path/to/chromedriver
    browser_driver_path = r'C:\path\to\chromedriver.exe'
    linovelib_epub = Linovelib2Epub(book_id=8, chapter_crawl_delay=3, page_crawl_delay=2, select_volume_mode=True,
                                    browser_driver_path=browser_driver_path,
                                    log_level='DEBUG')
    linovelib_epub.run()
```
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior（期望的行为）**
A clear and concise description of what you expected to happen.

**Screenshots or Video（截图或者视频录制）**
If applicable, add screenshots to help explain your problem.

**Environment（软件环境）**
 - 网络环境: 代码是在地球的哪一个区域运行的？这个会影响到网站的自动重定向。
 - OS Verison:  例如：Windows 10 专业版10.0.19045
 - Python Version: `python --version`
 - Pip Version: `pip --version`
 - Python packages: `pip list`

**Additional context（补充信息[可选]）**
Add any other context about the problem here.

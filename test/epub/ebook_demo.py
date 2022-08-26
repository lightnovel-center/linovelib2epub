from ebooklib import epub
from PIL import Image  # you need pip install Pillow
import io

book = epub.EpubBook()

# For more detail, visit http://docs.sourcefabric.org/projects/ebooklib/en/latest/tutorial.html#introduction

# basic spine
book.spine = ['nav', ]

# create chapter
c1 = epub.EpubHtml(title='Intro', file_name='chap_01.xhtml', lang='zh')
c1.content = """
<h1>Intro heading</h1>
<p>☆</p>
<p>呦☆</p>
<p>☆呦</p>
<p>呦☆呦</p>
<p> when ☆ is not surrounded by certain characters, it can't show properly.<p/>
<p>围绕♪者你总算可以显示了吧，好家伙</p>
<p>「Hello—♪闪亮登场，翻车，去掉Hello</p>
<p>「♪闪亮登场</p>
"""
# <p><img alt="image1" src="images/image1.jpeg"/><br/></p>

# add chapter
book.add_item(c1)

# add CSS file
style = 'body { font-family: LXGW WenKai Screen, Times, Times New Roman, serif; }'
nav_css = epub.EpubItem(uid="style_nav",
                        file_name="style/nav.css",
                        media_type="text/css",
                        content=style)
book.add_item(nav_css)

# load Image file
img1 = Image.open('images/image1.jpeg')  # 'image1.jpeg' should locate in current directory for this example
b = io.BytesIO()
img1.save(b, 'jpeg')
b_image1 = b.getvalue()

# define Image file path in .epub
image1_item = epub.EpubItem(uid='image_1', file_name='images/image1.jpeg', media_type='image/jpeg', content=b_image1)

# add Image file
book.add_item(image1_item)

# toc
book.toc.append([epub.Section('volume 1'), []])
book.toc[0][1].append(c1)
book.spine.append(c1)

book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

epub.write_epub('demo_novel.epub', book)

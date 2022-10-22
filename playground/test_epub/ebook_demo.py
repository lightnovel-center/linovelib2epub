import io

from PIL import Image  # you need pip install Pillow
from ebooklib import epub

book = epub.EpubBook()

# For more detail, visit http://docs.sourcefabric.org/projects/ebooklib/en/latest/tutorial.html#introduction

# basic spine
book.spine = ['nav', ]

chapter_style = '''
body { 
  background-color: #e1e1e1;
}
'''
chapter_css = epub.EpubItem(uid="style_chapter",
                            file_name="style/chapter.css",
                            media_type="text/css",
                            content=chapter_style)

# create chapter
c1 = epub.EpubHtml(title='Intro', file_name='chap_01.xhtml', lang='zh')

# title tag in head will be hardcoded to Intro, because title in head in meaningless.
c1.content = """
<body>
<h2>Chapter 1</h2>
<p> chapter 1 content</p>
</body>
"""
# https://github.com/aerkalov/ebooklib/issues/221#issuecomment-783769782
# EDIT: Nevermind, there is a way, calling add_item() on the EpubHtml instance
# -- still a bit unintuitive. I also hope to see this fixed!
c1.add_item(chapter_css)
book.add_item(chapter_css)

# add chapter
book.add_item(c1)

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

# add CSS file
nav_style = '''
body { 
  font-family: LXGW WenKai Screen, Times, Times New Roman, serif;
  background-color: grey;
}
'''
nav_css = epub.EpubItem(uid="style_nav",
                        file_name="style/nav.css",
                        media_type="text/css",
                        content=nav_style)

nav_html = book.get_item_with_id('nav')
nav_html.add_item(nav_css)
book.add_item(nav_css)


# print(book.get_item_with_id('nav').get_content())

epub.write_epub('demo_novel.epub', book)

from ebooklib import epub
from PIL import Image  # you need pip install Pillow
import io

book = epub.EpubBook()

# create chapter
c1 = epub.EpubHtml(title='Intro', file_name='chap_01.xhtml', lang='hr')
c1.content = u'<h1>Intro heading</h1><p>Zaba je skocila u baru.</p><p><img alt="image1" src="images/image1.jpeg"/><br/></p>'

# add chapter
book.add_item(c1)

# add CSS file
# book.add_item(nav_css)

# load Image file
img1 = Image.open('images/image1.jpeg')  # 'image1.jpeg' should locate in current directory for this example
b = io.BytesIO()
img1.save(b, 'jpeg')
b_image1 = b.getvalue()

# define Image file path in .epub
image1_item = epub.EpubItem(uid='image_1', file_name='images/image1.jpeg', media_type='image/jpeg', content=b_image1)

# add Image file
book.add_item(image1_item)

# basic spine
book.spine = ['nav', c1]

epub.write_epub('demo_novel.epub', book)

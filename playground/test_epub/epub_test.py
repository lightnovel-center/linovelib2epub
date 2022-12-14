# coding=utf-8

from ebooklib import epub

if __name__ == '__main__':
    book = epub.EpubBook()

    # add metadata
    book.set_identifier('sample123456')
    book.set_title('Sample book')
    book.set_language('en')

    book.add_author('Aleksandar Erkalovic')

    # add cover image -> cover.xhtml
    book.set_cover("image.gif", open('images/13-28.gif', 'rb').read())

    intro_style = """
      @font-face {
         font-family: "LXGWWenKai-Regular";
         font-weight: normal;
         font-style: normal;
         src: url("../Fonts/LXGWWenKai-Regular.ttf");
      }
    
      body {
        font-family: "LXGWWenKai-Regular",sans-serif;
        }
    """


    # intro chapter
    c1 = epub.EpubHtml(title='Introduction', file_name='intro.xhtml', lang='hr')
    c1.content = f"""
            <h1>Introduction</h1>
            <p>Introduction paragraph where i explain what is happening.</p>
        """
    intro_css = epub.EpubItem(uid="style_intro", file_name="style/intro.css", media_type="text/css",
                              content=intro_style)
    c1.add_item(intro_css)
    book.add_item(intro_css)

    # about chapter
    c2 = epub.EpubHtml(title='About this book', file_name='about.xhtml')
    c2.content = '<h1>About this book</h1><p>Helou, this is my book! There are many books, but this one is mine.</p>'

    # add chapters to the book
    book.add_item(c1)
    book.add_item(c2)

    # create table of contents
    # - add manual link
    # - add section
    # - add auto created links to chapters

    # -> nav.xhtml
    book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'),
                (epub.Section('Languages'),
                 (c1, c2))
                )



    # add font item
    with open('Fonts/LXGWWenKai-Regular.ttf', 'rb') as f:
        font_content = f.read()

    # font-sfnt
    font_item = epub.EpubItem(uid='LXGWWenKai-Regular', file_name='Fonts/LXGWWenKai-Regular.ttf',
                              media_type='application/font-sfnt', content=font_content)
    book.add_item(font_item)

    # create spin, add cover page as first page
    book.spine = ['cover', 'nav', c1, c2]

    # add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # add cover css
    cover_style = 'body { background-color: #e1e1e1;}'
    cover_css = epub.EpubItem(uid="style_cover", file_name="style/cover.css", media_type="text/css", content=cover_style)
    cover_html = book.get_item_with_id('cover')
    cover_html.add_item(cover_css)
    book.add_item(cover_css)

    # add nav css
    nav_style = '''
            @namespace epub "http://www.idpf.org/2007/ops";
            body {
                font-family: Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
            }
            h2 {
                 text-align: left;
                 text-transform: uppercase;
                 font-weight: 200;
            }
            ol {
                  list-style-type: none;
                  color: red;
            }
            ol > li:first-child {
                    margin-top: 0.3em;
            }
            nav[epub|type~='toc'] > ol > li > ol  {
                list-style-type:square;
            }
            nav[epub|type~='toc'] > ol > li > ol > li {
                    margin-top: 0.3em;
            }
            '''
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=nav_style)
    nav_html = book.get_item_with_id('nav')
    nav_html.add_item(nav_css)
    book.add_item(nav_css)

    # create epub file
    epub.write_epub('test.epub', book, {})

# import linovelib2epub
from linovelib2epub.linovel import Linovelib2Epub


def test_set_custom_style():
    custom_style_cover = '''
    img[alt=Cover] {
       max-width: 80%;
    }
    '''
    custom_style_nav = '''
    ol > li > ol > li > a {
       background-color: pink;
    }
    '''
    custom_style_chapter = '''
    p {
      background-color: #e1e1e1;
    }
    '''
    linovelib_epub = Linovelib2Epub(book_id=3279, clean_artifacts=False,
                                    custom_style_cover=custom_style_cover,
                                    custom_style_nav=custom_style_nav,
                                    custom_style_chapter=custom_style_chapter)
    linovelib_epub.run()


def test_basic_run():
    # linovelib_epub = Linovelib2Epub(book_id=3593, clean_artifacts=False)
    # linovelib_epub = Linovelib2Epub(book_id=3593, divide_volume=False, clean_artifacts=False)
    # linovelib_epub = Linovelib2Epub(book_id=2380, select_volume_mode=True, clean_artifacts=False)
    # linovelib_epub = Linovelib2Epub(book_id=3610)
    # linovelib_epub = Linovelib2Epub(book_id=3610, clean_artifacts=False)

    # linovelib_epub = Linovelib2Epub(book_id=3610, clean_artifacts=False,
    #                                 image_download_strategy=linovel.MULTIPROCESSING)

    # linovelib_epub = Linovelib2Epub(book_id=18, clean_artifacts=False)
    linovelib_epub = Linovelib2Epub(book_id=3279)
    # linovelib_epub = Linovelib2Epub(book_id=3728, divide_volume=True, clean_artifacts=False)
    linovelib_epub.run()


# warning!: must run within __main__ module guard due to process spawn issue.
if __name__ == '__main__':
    test_basic_run()
    # test_set_custom_style()

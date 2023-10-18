from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=875, target_site=TargetSite.MASIRO)
    linovelib_epub.run()

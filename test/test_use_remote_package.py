from linovelib2epub.linovel import Linovelib2Epub

# warning!: must run within __main__ module guard due to process spawn issue.
if __name__ == '__main__':
    print(__file__)
    linovelib_epub = Linovelib2Epub(book_id=3279, clean_artifacts=False)
    linovelib_epub.run()

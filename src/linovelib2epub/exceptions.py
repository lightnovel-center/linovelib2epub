class LinovelibException(Exception):
    """
    Base exception class for Linovelib2epub library.
    """
    pass

class PageContentIllegalException(LinovelibException):
    def __init__(self, message="Page content is illegal."):
        self.message = message
        super().__init__(self.message)
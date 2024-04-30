class LinovelibException(Exception):
    """
    Base exception class for Linovelib2epub library.
    """
    pass

class PageContentAbnormalException(LinovelibException):
    def __init__(self, message="Page content is abnormal."):
        self.message = message
        super().__init__(self.message)

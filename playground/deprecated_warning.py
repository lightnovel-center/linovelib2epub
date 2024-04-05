import sys
import warnings

def foo():
    func_name = sys._getframe().f_code.co_name
    warnings.warn(f'{func_name}函数过时，后续将会删除', DeprecationWarning)

if __name__ == '__main__':
    foo()
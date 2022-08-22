# download_images('https://w.linovelib.com/files/article/image/3/3211/3211s.jpg')
from src.crawl_step_1 import download_images

download_images('https://img.linovelib.com/3/3211/163938/193293.jpg')

# RuntimeError:
#         An attempt has been made to start a new process before the
#         current process has finished its bootstrapping phase.
#
#         This probably means that you are not using fork to start your
#         child processes and you have forgotten to use the proper idiom
#         in the main module:
#
#             if __name__ == '__main__':
#                 freeze_support()
#                 ...
#
#         The "freeze_support()" line can be omitted if the program
#         is not going to be frozen to produce an executable.
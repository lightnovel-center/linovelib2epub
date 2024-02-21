# -----------DEFAULT USER SETTINGS---------------------

DEFAULT_TARGET_SITE = 'LINOVELIB_MOBILE'

# 主页URL
BASE_URL = 'https://w.linovelib.com'

# 书籍ID: must be provided by user
# BOOK_ID = 3211

# 选择卷模式。
# 当 SELECT_VOLUME_MODE 为True时，
# - 忽略用户DIVIDE_VOLUME的设置值，将其强制为True。因为合订本会很诡异。例如，1卷，7卷的合订本。
SELECT_VOLUME_MODE = False

# 是否分卷：分卷(True), 不分卷(False)
DIVIDE_VOLUME = False

# 是否下载插图：下载插图(True), 不下载插图(False)
HAS_ILLUSTRATION = True

# 图片下载临时文件夹. 不允许以相对路径../开头。一般不建议修改。
IMAGE_DOWNLOAD_FOLDER = 'novel_images'

# pickle临时数据保存的文件夹。一般不建议修改。
PICKLE_TEMP_FOLDER = 'pickle'

# 一个HTTP请求的超时等待时间(秒)。
HTTP_TIMEOUT = 10

# 当一个HTTP请求失败后，重试的最大次数。
HTTP_RETRIES = 10

# 自定义HTTP cookie
HTTP_COOKIE = ''

# 删除临时数据/工件，这里指的是pickles和下载的图片文件
# True表示会在epub输出后删除缓存。
CLEAN_ARTIFACTS = True

# disable http requests proxy
DISABLE_PROXY = True

# ----------------------------------------------
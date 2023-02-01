# -----------DEFAULT USER SETTINGS---------------------

# 主页URL
BASE_URL = 'https://w.linovelib.com/novel'

# 书籍ID: must be provided by user
# BOOK_ID = 3211

# 选择卷模式。
# 当 SELECT_VOLUME_MODE 为True时，
# - 忽略用户DIVIDE_VOLUME的设置值，将其强制为True。因为合订本会很诡异。例如，1卷，7卷的合订本。
# - 不使用任何已存在的pickle缓存。例如上一次选择了1,7卷。这一次选择2,6卷。为避免过渡设计，选择卷模式一律忽略缓存。
SELECT_VOLUME_MODE = False

# 是否分卷：分卷(True), 不分卷(False)
DIVIDE_VOLUME = False

# 是否下载插图：下载插图(True), 不下载插图(False)
HAS_ILLUSTRATION = True

# 图片下载临时文件夹. 不允许以相对路径../开头。一般不建议修改。
IMAGE_DOWNLOAD_FOLDER = 'images'

# pickle临时数据保存的文件夹。一般不建议修改。
# 注意：缓存模式需要指定显式CLEAN_ARTIFACTS = False，并且不能使用上面的选择卷模式。
PICKLE_TEMP_FOLDER = 'pickle'

# 一个HTTP请求的超时等待时间(秒)。
HTTP_TIMEOUT = 10

# 当一个HTTP请求失败后，重试的最大次数。
HTTP_RETRIES = 5

# 自定义HTTP cookie
HTTP_COOKIE = ''

# 删除临时数据/工件，这里指的是pickles和下载的图片文件
CLEAN_ARTIFACTS = True

# disable http requests proxy
DISABLE_PROXY = True

# ----------------------------------------------

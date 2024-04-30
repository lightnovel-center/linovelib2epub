# https://zhuanlan.zhihu.com/p/675706901
# selenium use proxy 无密码、以及需要密码验证的proxy

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# 设置代理IP
proxy_ip = "127.0.0.1"
proxy_port = "7890"

# proxy_ip = "202.101.213.167"
# proxy_port = "18258"

# 配置浏览器选项
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=http://{}:{}'.format(proxy_ip, proxy_port))

# 启动浏览器
chrome_service = Service()
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# 访问百度官网
driver.get('https://ip111.cn/')

# 提示用户手动关闭浏览器
input("请手动关闭浏览器，按 Enter 键进行关闭...")

# 关闭浏览器
driver.quit()

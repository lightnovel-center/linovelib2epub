from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# 设置代理IP
proxy_ip = "127.0.0.1"
proxy_port = "7890"

# 配置浏览器选项
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('--proxy-server=http://{}:{}'.format(proxy_ip, proxy_port))
# chrome_options.add_argument("--headless")
ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
chrome_options.add_argument(f"--user-agent={ua}")

chrome_service = Service()
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)


# 打开网页
# url = "https://www.linovelib.com/"
# # url2= 'https://www.bilinovel.com/cdn-cgi/challenge-platform/scripts/jsd/main.js'
# driver.get(url)

# 获取页面源代码
# html = driver.page_source
# print(html)

# 刷新页面
# driver.refresh()

# 获取刷新后的页面源代码
# refreshed_html = driver.page_source
# print(refreshed_html)

def _fetch_page(url) -> str:
    driver.set_page_load_timeout(10)
    try:
        # 最多等待10秒，但如果条件提前满足则立即返回
        driver.get(url)
    except Exception as e:
        print('Need retry.')
        pass

    html = driver.page_source
    return html


url3 = 'https://www.bilinovel.com/novel/119/15180.html'
html = _fetch_page(url3)
# print(html)

# 在这里可以对页面源代码进行解析和提取需要的信息

# 提示用户手动关闭浏览器
input("请手动关闭浏览器，然后按 Enter 键继续...")

# 关闭浏览器
driver.quit()

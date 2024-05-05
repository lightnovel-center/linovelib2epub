from DrissionPage import ChromiumOptions, SessionOptions
from DrissionPage._pages.web_page import WebPage

path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
co = ChromiumOptions()
co.set_browser_path(path).save()

mobile_ua = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36'
so = SessionOptions()
headers = {
    'user-agent': mobile_ua
}
so.set_headers(headers=headers)

# page = ChromiumPage()
page = WebPage(chromium_options=None, session_or_options=None)

url = 'https://www.bilinovel.com/novel/1030/42006.html'
resp = page.get(url)

# 问题:电脑端访问手机端网页会跳转到PC版本的网页。
print(resp)

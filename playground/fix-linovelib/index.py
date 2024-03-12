import requests

s = requests.Session()


def request_headers(referer: str = '', random_ua: bool = True):
    # default_mobile_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/120.0.0.0'
    default_mobile_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    default_referer = 'https://www.bilinovel.com'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Referer': referer if referer else default_referer,
        # use random mobile phone header later
        # 'User-Agent': self.spider_settings['random_useragent'] if random_ua else default_ua
        'User-Agent': default_mobile_ua
    }
    return headers


headers = request_headers()

url = 'https://www.bilinovel.com/novel/3721/190988.html'
r = s.get(url, headers=headers)

print(r.request.headers)
print(r.text)

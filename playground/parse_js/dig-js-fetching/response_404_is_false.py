import requests

url = "https://tw.linovelib.com/themes/zhmb/js/hm.js"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "cache-control": "max-age=0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
}
# len()

response = requests.get(url, headers=headers, timeout=20)

# response.__bool__() -> response.ok

# response.ok
# Returns True if :attr:`status_code` is less than 400, False if not.

# 404 -> False

if response:
    print('1')
else:
    print('2')

# 2
import os

import requests

os.environ['HTTP_PROXY'] = os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['NO_PROXY'] = os.environ['no_proxy'] = '127.0.0.1,localhost,.local,https://httpbin.org/cookies'

s = requests.Session()

headers = {'my-header': 'ok'}
cookies = {'my-cookie': 'cat'}

r = s.get('https://httpbin.org/cookies', headers=headers, cookies=cookies)

print(r.request.headers)
# {'User-Agent': 'python-requests/2.28.1', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive', 'my-header': 'ok', 'Cookie': 'my-cookie=cat'}

print(r.text)
# {
#   "cookies": {
#     "my-cookie": "cat"
#   }
# }

print(r.headers)
# {'Date': 'Sun, 11 Sep 2022 05:13:45 GMT', 'Content-Type': 'application/json', 'Content-Length': '46', 'Connection': 'keep-alive', 'Server': 'gunicorn/19.9.0', 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Credentials': 'true'}

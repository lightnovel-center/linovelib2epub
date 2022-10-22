from http.cookies import SimpleCookie

import requests

s = requests.Session()
s.trust_env = False

# if value contains many key-value pairs, must be encoded before loading.
# DONT expose real cookie, use ENV VARIABLES instead
rawdata_encode = ''
cookie = SimpleCookie()
cookie.load(rawdata_encode)

cookie_dict = {k: v.value for k, v in cookie.items()}
cookiejar = requests.utils.cookiejar_from_dict(cookie_dict)
s.cookies = cookiejar

r = s.get('https://w.linovelib.com')
print(r.request.headers)

print(r.status_code)
# 登录时，页面上可以找到我的书架
# 没有登陆时，显示“登陆去书架”

print(r.headers)

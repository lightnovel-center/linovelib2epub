# https://docs.python.org/3/library/http.cookies.html
from http.cookies import SimpleCookie

rawdata = 'chips=ahoy; vienna=finger'
cookie = SimpleCookie()
cookie.load(rawdata)
print(cookie)

# Even though SimpleCookie is dictionary-like, it internally uses a Morsel object
# which is incompatible with requests. Manually construct a dictionary instead.
cookies = {k: v.value for k, v in cookie.items()}
print(cookies)
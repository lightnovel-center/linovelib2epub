import requests
from urllib3.exceptions import MaxRetryError, ProxyError

s = requests.session()
url = "http://img.linovelib.com"
resp = s.get(url, headers={}, timeout=5)
print(resp.status_code)

# use requests.exceptions.ProxyError

# requests.exceptions.ProxyError: HTTPSConnectionPool(host='img.linovelib.com', port=443):
# Max retries exceeded with url: / (Caused by ProxyError('Cannot connect to proxy.', OSError(0, 'Error')))

import requests

url = 'http://www.httpbin.org/ip'

proxy = {
    'http': '127.0.0.1:7890'
}

resp_1 = requests.get(url, timeout=5)
print(resp_1.text)  # 真实IP

resp_2 = requests.get(url, proxies=proxy, timeout=5)
print(resp_2.text)  # 如果proxy可用，应该为proxy设置的IP

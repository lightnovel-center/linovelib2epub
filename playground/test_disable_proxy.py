import os

import requests


def disable_proxy_m2():
    # sometimes work sometimes not on windows + clash for windows env
    # https://stackoverflow.com/a/60352993
    os.environ['HTTP_PROXY'] = os.environ['http_proxy'] = 'http://127.0.0.1:7890'
    os.environ['HTTPS_PROXY'] = os.environ['https_proxy'] = 'http://127.0.0.1:7890'  # note: is http NOT https
    os.environ['NO_PROXY'] = os.environ['no_proxy'] = '127.0.0.1,localhost,.local,https://w.linovelib.com'
    r = requests.get('https://w.linovelib.com')  # , verify=False
    print(r)


disable_proxy_m2()


def disable_proxy_m1():
    # https://stackoverflow.com/a/28521696
    session = requests.Session()
    # disabling proxies
    session.trust_env = False  # work
    response = session.get('https://w.linovelib.com')
    print(response)


# disable_proxy_m1()


def disable_proxy_m3():
    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'https://127.0.0.1:7890'
    }
    no_proxy = {
        'http': None,
        'https': None
    }
    r = requests.get('https://w.linovelib.com', proxies=no_proxy)
    print(r)

# disable_proxy_m3()

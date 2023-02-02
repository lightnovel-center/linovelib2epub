import os
import re
import time
from http.cookies import SimpleCookie

import pkg_resources
from fake_useragent import UserAgent


def cookiedict_from_str(str=''):
    cookie = SimpleCookie()
    cookie.load(str)
    cookie_dict = {k: v.value for k, v in cookie.items()}
    return cookie_dict


def random_useragent():
    try:
        return UserAgent().random
    except (Exception,):
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'


def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def request_with_retry(client, url, headers=None, retry_max=5, timeout=10, logger=None):
    if headers is None:
        headers = {}

    current_num_of_request = 0

    while current_num_of_request <= retry_max:
        try:
            response = client.get(url, headers=headers, timeout=timeout)
            if response:
                return response
            else:
                if logger:
                     logger.warn(f'Request {url} succeed but data is empty.')
                time.sleep(1)
        except (Exception,) as e:
            if logger:
                logger.error(f'Request {url} failed.', e)
            time.sleep(1)

        current_num_of_request += 1
        if logger:
            logger.warn('current_num_of_request: ', current_num_of_request)

    return None


def is_valid_image_url(url):
    """
    Example image link: https://img.linovelib.com/3/3211/163938/193293.jpg
    Refer: https://www.ietf.org/rfc/rfc2396.txt, https://stackoverflow.com/a/169631

    ^https?://(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpe?g|gif|png|webp|bmp|svg)$    # noqa
             |-------- domain -----------|--- path ------|--------- --extension -----|
    """
    image_pattern = r"^https?://(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpe?g|gif|png|webp|bmp|svg)$"
    return bool(re.match(image_pattern, url))


def check_image_integrity(resp):
    # check file integrity by comparing HTTP header content-length and real request tell()
    expected_length = resp.headers and resp.headers.get('Content-Length')
    actual_length = resp.raw.tell()  # len(resp.content)
    if expected_length and actual_length:
        # expected_length: 31949; actual_length: 31949
        if int(actual_length) < int(expected_length):
            raise IOError(
                'incomplete read ({} bytes get, {} bytes expected)'.format(actual_length, expected_length)
            )


# Replace invalid character for file/folder name
def sanitize_pathname(pathname):
    # '/ \ : * ? " < > |'
    return re.sub(r"[\/\\\:\*\?\"\<\>\|]", "_", pathname)


def read_pkg_resource(file_path=''):
    # file_path example: "./styles/chapter.css"
    return pkg_resources.resource_string(__name__, file_path)

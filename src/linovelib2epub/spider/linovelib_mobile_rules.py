import re
from typing import Dict

import requests
import json

from linovelib2epub.utils import request_with_retry


class ParsedRuleResult:
    def __init__(self,
                 mapping_dict: Dict,
                 content_id: str,
                 ):
        self.mapping_dict = mapping_dict
        self.content_id = content_id


def generate_mapping_result():
    js_text = _fetch_js_text()
    result_set = _parse_mapping(js_text)
    return result_set


def _parse_mapping_rules_legacy(js_text) -> dict:
    """
    Don't use this method anymore.

    :param js_text:
    :return:
    """
    # extract needed string
    js_pattern = r'\(null,\s*"(.*?)"\['
    matches = re.findall(js_pattern, js_text)
    long_string = matches[0]

    # parse to js
    code_tokens = re.split(r'[a-zA-Z]+', long_string)
    js_code = ''.join(chr(int(token)) for token in code_tokens)
    # print(js_code)

    # find mapping
    pattern = r"RegExp\([\"|\']([^\"]+?)[\"|\'],\s*\"gi\"\),\s*\"([^\"]+?)\"\)"
    matches = re.findall(pattern, js_code)

    # generate mapping rules
    replace_rules = {}
    for match in matches:
        # 在python中不需要可以转义\
        key = match[0]
        value = match[1]
        replace_rules[key] = value

    return replace_rules


def _parse_mapping(js_text) -> ParsedRuleResult:
    decoded_s = js_text.encode('utf-8').decode('unicode_escape')

    # resolve content_id
    pattern_content_id = r"window\[\"document\"\]\[\'getElementById']\(\'(.+?)\'\)"
    match = re.search(pattern_content_id, decoded_s)

    content_id = ""
    if match:
        content_id = match[1]

    assert content_id, "content_id can't be empty string, please submit this bug to github issue."

    # resolve mapping rule
    pattern = r"\"RegExp\"]\([\'|\"]([^\"]+?)[\"|\'],\s*[\'|\"]gi[\'|\"]\),\s*[\'|\"]([^\"]+?)[\"|\']"
    matches = re.findall(pattern, decoded_s)
    replace_rules = {match[0]: match[1] for match in matches}

    # merge result
    parsed_rule_result = ParsedRuleResult(mapping_dict=replace_rules, content_id=content_id)

    return parsed_rule_result


def write_rules(rules):
    """
    For debug only.
    :param rules:
    :return:
    """
    file_path = "anti_obfuscation.json"

    # 为了表示Unicode字符 \u201c，在JSON字符串中，需要写成 \\u201c，其中第一个反斜杠用于转义，第二个反斜杠才是实际字符 \。
    def escape_unicode(char):
        return '\\u{:04x}'.format(ord(char))

    escaped_rules = {escape_unicode(k): v for k, v in rules.items()}

    # Write the JSON data to the file
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(escaped_rules, json_file, ensure_ascii=False, indent=2)


def _fetch_js_text():
    url = "https://w.linovelib.com/themes/zhmb/js/hm.js"
    # should handle network retry
    session = requests.session()
    resp = request_with_retry(session, url)
    return resp.text

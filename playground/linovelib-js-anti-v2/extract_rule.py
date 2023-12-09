# import os
import re
import requests
import json


def generate_mapping_rules():
    js_text = _fetch_js_text()
    mapping_rules = _parse_mapping_rules(js_text)
    write_rules(mapping_rules)
    return mapping_rules

def _parse_mapping_rules(js_text):
    # extract needed string
    js_pattern = r'\(null,\s*"(.*?)"\['
    matches = re.findall(js_pattern, js_text)
    long_string = matches[0]

    # parse to js
    code_tokens = re.split(r'[a-zA-Z]+', long_string)
    js_code = ''.join(chr(int(token)) for token in code_tokens)
    # print(js_code)

    # resolve content_id
    pattern_content_id = r"document.getElementById\(\'(.+?)\'\).innerHTML"
    match = re.search(pattern_content_id, js_code)
    content_id = ""
    if match:
        content_id = match[1]
    assert content_id, "[_parse_mapping_v2]: content_id can't be empty string, please submit this bug to github issue."

    # print(content_id)

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


def write_rules(rules):
    file_path = "anti_obfuscation.json"

    # 为了表示Unicode字符 \u201c，在JSON字符串中，需要写成 \\u201c，其中第一个反斜杠用于转义，第二个反斜杠才是实际字符 \。
    def escape_unicode(char):
        return '\\u{:04x}'.format(ord(char))

    escaped_rules = {escape_unicode(k): v for k, v in rules.items()}

    # Write the JSON data to the file
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(escaped_rules, json_file, ensure_ascii=False, indent=2)


def _fetch_js_text():
    url = "https://w.linovelib.com/themes/zhmb/js/readtools.js"
    # should handle network retry
    resp = requests.get(url)
    return resp.text

if __name__ == '__main__':
    generate_mapping_rules()
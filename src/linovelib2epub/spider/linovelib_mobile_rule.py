import asyncio
import json
import re
from logging import Logger as LoggerAlias
from typing import Dict, Any, Tuple

import esprima
import requests

from linovelib2epub.utils import requests_get_with_retry


class ParsedRuleResultMobile:
    def __init__(self,
                 mapping_dict: Dict[str, Any],
                 content_id: str,
                 ):
        self.mapping_dict = mapping_dict
        self.content_id = content_id


class LinovelibMobileRuleParser:

    def __init__(self, logger: LoggerAlias = None,
                 traditional: bool = False,
                 disable_proxy: bool = True):
        self.logger = logger
        self.traditional = traditional
        self.trust_env = not disable_proxy

    def generate_mapping_result(self):
        url, js_text = self._fetch_js_text()
        if js_text:
            self.logger.info(f'[Text Mapping]Use the file of url({url}) to parse mapping ruleset.')
            result_set = self._parse_mapping(js_text)
            return result_set
        else:
            self.logger.info(f'[Text Mapping]Use the fallback mapping ruleset.')
            rule = ParsedRuleResultMobile(mapping_dict={}, content_id='acontent1')
            return rule

    def _parse_mapping(self, js_text) -> ParsedRuleResultMobile:
        if not self.traditional:
            # content_id, replace_rules = self._parse_mapping_v2_zh(js_text)
            content_id, replace_rules = self._parse_mapping_v2_zh_tw(js_text)
        else:
            content_id, replace_rules = self._parse_mapping_v2_zh_tw(js_text)
        parsed_rule_result = ParsedRuleResultMobile(mapping_dict=replace_rules, content_id=content_id)
        return parsed_rule_result

    def _parse_mapping_v1(js_text) -> tuple:
        # 第一代：在 js 中使用硬编码的 RegExp 进行 text 替换，很好解析，一切明文。这里留一个空实现，仅为记录历史。
        pass

    @staticmethod
    def _parse_mapping_v2_zh(js_text) -> tuple:
        """
        简体版网站
        第二代：使用 A110B90V45 这种长字符串，将字符串按字母切割得到 ascii codes，拼接对应字符得到 js 明文。

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

        # resolve content_id
        # zh => GOAL: document.getElementById('acontentz').innerHTML => acontentz
        pattern_content_id = r"document.getElementById\(\'(.+?)\'\).innerHTML"
        match = re.search(pattern_content_id, js_code)
        content_id = ""
        if match:
            content_id = match[1]
        assert content_id, "[_parse_mapping_v2]: content_id can't be an empty string, please submit this bug to github issue."

        # find mapping
        pattern = r"RegExp\([\"|\']([^\"]+?)[\"|\'],\s*\"gi\"\),\s*\"([^\"]+?)\"\)"
        matches = re.findall(pattern, js_code)

        # generate mapping rules
        replace_rules = {}
        for match in matches:
            # 在 python 中不需要可以转义 \
            key = match[0]
            value = match[1]
            replace_rules[key] = value

        return content_id, replace_rules

    @staticmethod
    def _parse_mapping_v2_zh_tw(js_text) -> tuple:
        """
        繁体版网站
        :param js_text:
        :return:
        """

        def remove_comments(js_code):
            # 使用正则表达式匹配和替换注释
            pattern = r"/\*[\s\S]*?\*/|//.*?$"
            cleaned_code = re.sub(pattern, "", js_code, flags=re.MULTILINE)
            return cleaned_code

        def extract_contentid(ast) -> str:
            try:
                properties = ast.body[0].declarations[0].init.properties
                iterator = filter(lambda x: x.key.name == 'contentid', properties)
                list = [item for item in iterator]
                contentid_val = list[0].value.value
                return contentid_val
            except:
                # fallback
                return 'acontent1'

        cleaned_js = remove_comments(js_text)
        ast = esprima.parse(cleaned_js)
        content_id = extract_contentid(ast)

        # generate mapping rules
        # 目前繁体网站没有对正文进行 js 混淆，直接空对象即可
        replace_rules = {}

        return content_id, replace_rules

    @staticmethod
    def _parse_mapping_v3(js_text) -> tuple:
        # 第三代: 对 js 明文进行一次 unicode 解码，然后类似 v2，只不过正则表达式有所区别，必须调整。
        decoded_s = js_text.encode('utf-8').decode('unicode_escape')

        # resolve content_id
        pattern_content_id = r"window\[\"document\"\]\[\'getElementById']\(\'(.+?)\'\)"
        match = re.search(pattern_content_id, decoded_s)
        content_id = ""
        if match:
            content_id = match[1]
        assert content_id, "[_parse_mapping_v3]: content_id can't be empty string, please submit this bug to github issue."

        # resolve mapping rule
        pattern = r"\"RegExp\"]\([\'|\"]([^\"]+?)[\"|\'],\s*[\'|\"]gi[\'|\"]\),\s*[\'|\"]([^\"]+?)[\"|\']"
        matches = re.findall(pattern, decoded_s)
        replace_rules = {match[0]: match[1] for match in matches}

        return content_id, replace_rules

    @staticmethod
    def write_rules(rules: Dict[str, Any]):
        """
        For debug only.
        :param rules:
        :return:
        """
        file_path = "anti_obfuscation.json"

        # 为了表示 Unicode 字符 \u201c，在 JSON 字符串中，需要写成 \\u201c，其中第一个反斜杠用于转义，第二个反斜杠才是实际字符 \。
        def escape_unicode(char):
            return '\\u{:04x}'.format(ord(char))

        escaped_rules = {escape_unicode(k): v for k, v in rules.items()}

        # Write the JSON data to the file
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(escaped_rules, json_file, ensure_ascii=False, indent=2)

    def _fetch_js_text(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "max-age=0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
        }

        url1 = "https://tw.linovelib.com/themes/zhmb/js/hm.js"
        url2 = "https://tw.linovelib.com/themes/zhmb/js/readtool.js"
        urls = [url1, url2]

        file_racer = WebFileRacer(urls=urls, headers=headers)
        url, text = asyncio.run(file_racer.fetch_file())
        return url, text


class WebFileRacer:
    def __init__(self, urls, headers):
        self.urls = urls
        self.headers = headers

    def _fetch_with_retry(self, url) -> Tuple[str, str | None]:
        resp = requests_get_with_retry(requests, url, headers=self.headers)
        if resp:
            return url, resp.text

        return url, None

    @staticmethod
    async def _fetch_async(url, fetch_func):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, fetch_func, url)

    async def fetch_file(self):
        tasks = [asyncio.create_task(self._fetch_async(url, self._fetch_with_retry)) for url in self.urls]
        completed, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

        for task in completed:
            url, resp_text = task.result()
            if resp_text:
                return url, resp_text

        # 没有任何一个 url 能返回文本
        return None, None

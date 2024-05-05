from logging import Logger as LoggerAlias
from typing import Dict, Any


class ParsedRuleResultPC:
    def __init__(self,
                 mapping_dict: Dict[str, Any],
                 content_id: str,
                 ):
        self.mapping_dict = mapping_dict
        self.content_id = content_id


class LinovelibPCRuleParser:
    def __init__(self, logger: LoggerAlias = None,
                 traditional: bool = False,
                 disable_proxy: bool = True):
        self.logger = logger
        self.traditional = traditional
        self.trust_env = not disable_proxy

    def generate_mapping_result(self) -> ParsedRuleResultPC:
        content_id = 'TextContent'
        return ParsedRuleResultPC(mapping_dict={}, content_id=content_id)

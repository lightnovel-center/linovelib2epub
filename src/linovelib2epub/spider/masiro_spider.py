import asyncio
from dataclasses import dataclass
from typing import Dict, Any

import aiohttp
from lxml import html

from linovelib2epub.logger import Logger
from linovelib2epub.models import LightNovel
from linovelib2epub.spider import BaseNovelWebsiteSpider
from linovelib2epub.utils import aiohttp_get_with_retry, aiohttp_post_with_retry
from .config import env_settings
from ..exceptions import LinovelibException

@dataclass
class MasiroLoginInfo:
    login_url: str = 'https://masiro.me/admin/auth/login'
    username: str = ''
    password: str = ''
    token: str = ''


class MasiroSpider(BaseNovelWebsiteSpider):

    def __init__(self, spider_settings: Dict[str, Any]):
        super().__init__(spider_settings)
        self.logger = Logger(logger_name=type(self).__name__,
                             log_filename=self.spider_settings["log_filename"]).get_logger()

        # read user secrets
        self._masiro_username = env_settings.get("MASIRO_LOGIN_USERNAME")
        self._masiro_password = env_settings.get("MASIRO_LOGIN_PASSWORD")
        if (not self._masiro_username) or (not self._masiro_password):
            raise LinovelibException("masiro account not found.")

    def fetch(self) -> LightNovel:
        res = asyncio.run(self._fetch())
        return None

    async def _fetch(self) -> Any:
        jar = aiohttp.CookieJar(unsafe=True)
        conn = aiohttp.TCPConnector(ssl=False)
        trust_env = False if self.spider_settings["disable_proxy"] else True
        async with aiohttp.ClientSession(connector=conn, trust_env=trust_env, cookie_jar=jar) as session:
            login_info = MasiroLoginInfo()
            login_info.username = self._masiro_username
            login_info.password = self._masiro_password

            # 1. get csrf token
            await self._masiro_get_token(login_info, session)

            login_param = self._build_login_param(login_info)
            login_headers = self._build_login_headers(login_info)

            # 2. do login
            result = await aiohttp_post_with_retry(session, login_info.login_url, params=login_param,
                                                   headers=login_headers)
            print(result)

            # https://masiro.me/admin/novelView?novel_id=875
            # => can get basic info and toc

            book_url = f"https://masiro.me/admin/novelView?novel_id={self.spider_settings['book_id']}"

            # 3. get basic info and catalog
            book_basic_info = await self._crawl_book_basic_info_with_catalog(book_url, session)
            if not book_basic_info:
                raise LinovelibException(f'Fetch book_basic_info(+catalog) of {self.spider_settings["book_id"]} failed.')

        return 123

    async def _crawl_book_basic_info_with_catalog(self,
                                            url: str,
                                            session: aiohttp.ClientSession):

        html_text = await aiohttp_get_with_retry(session, url, self.request_headers())

        page_body = html.fromstring(html_text)

        # title √
        # author √
        # cover √
        # translator
        # status
        # tags √
        # recent_update
        # popularity
        # word_count_text
        # original
        # brief_introduction √

        XPATH_TITLE = '//div[@class="novel-title"]/text()'
        XPATH_AUTHOR = '//div[@class="author"]/a/text()'
        XPATH_TAG = '//div[@class="tags"]//a/span/text()'
        XPATH_INTRODUCTION = '//div[@class="brief"]/text() | //div[@class="brief"]/*/text()'
        XPATH_COVER = '//img[@class="img img-thumbnail"]/@src'

        title = page_body.xpath(XPATH_TITLE)[0] if page_body.xpath(XPATH_TITLE) else ''
        author = page_body.xpath(XPATH_AUTHOR)[0] if page_body.xpath(XPATH_AUTHOR) else ''
        tags = page_body.xpath(XPATH_TAG) if page_body.xpath(XPATH_TAG) else ''
        introduction = page_body.xpath(XPATH_INTRODUCTION) if page_body.xpath(XPATH_INTRODUCTION) else ''
        cover_src = page_body.xpath(XPATH_COVER)[0] if page_body.xpath(XPATH_COVER) else ''

        print(title)
        print(author)
        print(tags)
        print(introduction)
        print(cover_src)

        #             # 获取章节
        #         chapter_url_list = page_body.xpath(config.read('xpath_config')[login_info.site]['chapter'])
        #         if chapter_url_list:
        #             book_data.chapter = []
        #             order = 1
        #             for chapter_url in chapter_url_list:
        #                 if login_info.site == 'masiro':
        #                     chapter_url = 'https://masiro.me' + chapter_url
        #                 chapter_data = chapter.Chapter(None, chapter_url, None, None, order, None)
        #                 # 抓取章节
        #                 await chapter.build_chapter(login_info, book_data, chapter_data, session)
        #                 book_data.chapter.append(chapter_data)
        #                 order += 1

    @staticmethod
    def _build_login_param(login_info: MasiroLoginInfo):
        # network tab 负载区域可以找到表单字段列表
        return {
            'username': login_info.username,
            'password': login_info.password,
            'remember': '1',
            '_token': login_info.token
        }

    def _build_login_headers(self, login_info: MasiroLoginInfo):
        # network tab 标头区域可以审查
        headers = self.request_headers()
        headers['x-csrf-token'] = login_info.token
        headers['x-requested-with'] = 'XMLHttpRequest'
        return headers

    def request_headers(self) -> Dict[str, Any]:
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46'
        }

    def get_image_filename(self, url: str) -> str:
        # TODO
        return super().get_image_filename(url)

    async def _masiro_get_token(self, login_info: MasiroLoginInfo, session):
        res = await aiohttp_get_with_retry(session, login_info.login_url, self.request_headers(), logger=self.logger)

        page_body = html.fromstring(res)
        token = str(page_body.xpath('//input[@class=\'csrf\']/@value')[0])
        self.logger.info(f'token: {token}')

        login_info.token = token

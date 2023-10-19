import asyncio
import re
from dataclasses import dataclass
from typing import Dict, Any, Union, List, Awaitable
from urllib.parse import urljoin

import aiohttp
import inquirer
from bs4 import BeautifulSoup
from lxml import html

from linovelib2epub.logger import Logger
from linovelib2epub.models import LightNovel, LightNovelVolume, LightNovelChapter
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
        timeout = aiohttp.ClientTimeout(total=30, connect=15)

        async with aiohttp.ClientSession(connector=conn, trust_env=trust_env, cookie_jar=jar,
                                         timeout=timeout) as session:
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

            # https://masiro.me/admin/novelView?novel_id=875
            # => can get basic info and toc

            book_url = f"https://masiro.me/admin/novelView?novel_id={self.spider_settings['book_id']}"

            # 3. get basic info and catalog
            book_basic_info = await self._crawl_book_basic_info_with_catalog(book_url, session)
            if not book_basic_info:
                raise LinovelibException(
                    f'Fetch book_basic_info(+catalog) of {self.spider_settings["book_id"]} failed.')

        return 123

    async def _crawl_book_basic_info_with_catalog(self,
                                                  url: str,
                                                  session: aiohttp.ClientSession):

        html_text = await aiohttp_get_with_retry(session, url, self.request_headers())

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

        soup = BeautifulSoup(html_text, 'lxml')

        title = soup.find('div', {'class': 'novel-title'}).text
        author = soup.find('div', {'class': 'author'}).find('a').text
        _tag_spans = soup.find('div', class_='tags').find_all('a')
        tags = [tag.find('span').text for tag in _tag_spans]
        brief_introduction = soup.find('div', {'class': 'brief'}).text
        cover_src = soup.find('img', {'class': 'img img-thumbnail'})['src'].split("?")[0]

        catalog_list = self._convert_to_catalog_list(html_text)

        # select_volume_mode
        if self.spider_settings['select_volume_mode']:
            catalog_list = self._handle_select_volume(catalog_list)

        # todo pre-buy chapters before downloading

        page_url_set = {chapter[1] for volume_dict in catalog_list for chapter in volume_dict['chapters']}
        url_to_page = await self.download_page_urls(session, page_url_set)
        print(url_to_page)

        new_novel = LightNovel()
        illustration_dict: Dict[Union[int, str], List[str]] = dict()

        volume_id = 0
        for volume_dict in catalog_list:
            volume_id += 1

            new_volume = LightNovelVolume(vid=volume_id)
            new_volume.title = volume_dict['volume_title']

            # self.logger.info(f'volume: {volume_dict["volume_title"]}')

            illustration_dict.setdefault(volume_dict['vid'], [])

            chapter_id = -1
            chapter_list = []  # store chapter for removing duplicate images in the first chapter
            for chapter in volume_dict['chapters']:
                chapter_id += 1
                chapter_content = ''
                chapter_title = chapter[0]

                new_chapter = LightNovelChapter(cid=chapter_id)
                new_chapter.title = chapter_title
                # new_chapter.content = 'UNSOLVED'

                # self.logger.info(f'chapter : {chapter_title}')

                # one page per chapter
                page_link = chapter_url = chapter[1]

    async def download_page_urls(self, session, page_url_set: set):
        self.logger.info(f'page url set = {len(page_url_set)}')

        url_to_page = {url: 'NOT_DOWNLOAD_READY' for url in page_url_set}

        async with session:
            tasks = {asyncio.create_task(self._download_page(session, url), name=url) for url in page_url_set}
            pending: set = tasks
            succeed_count = 0

            while pending:
                done, pending = await asyncio.wait(pending, return_when=asyncio.ALL_COMPLETED)
                # Note: This does not raise TimeoutError! Futures that aren't done when the timeout occurs
                # are returned in the second set

                # 1. succeed => normal result in done(# HAPPY CASE)
                # 2. Timeout => No TimeoutError, put timeout tasks in pending(SAD CASE(need retry))
                # 3  Other Exception before timeout => (SAD CASE(need retry)

                for done_task in done:
                    exception = done_task.exception()
                    task_url = done_task.get_name()

                    if exception is None:
                        url_to_page[task_url] = done_task.result()
                        succeed_count += 1
                    else:
                        # [TEST]make connect=.1 to reach this branch, should retry all the urls that entered this case
                        self.logger.info(f'Exception: {type(exception)}')
                        self.logger.info(f'FAIL: {task_url}; should retry this url.')
                        pending.add(asyncio.create_task(self._download_page(session, task_url), name=task_url))

                self.logger.info(f'SUCCEED_COUNT: {succeed_count}')
                self.logger.info(f'[NEXT TURN]Pending task count: {len(pending)}')

        return url_to_page

    async def _download_page(self, session, url) -> str | None:
        timeout = aiohttp.ClientTimeout(total=30, connect=15)  # per request timeout
        async with session.get(url, headers=self.request_headers(), timeout=timeout) as resp:
            if resp.status == 200:
                self.logger.info(f'fetch page: {url} ok.')
                return await resp.text()
            else:
                # maybe 404 etc. Now ignore it, don't raise error to avoid retry dead loop
                # 404 is considered as success => don't retry
                # 429 too many requests => should retry
                # 503 Service Unavailable => should retry
                self.logger.error(f'what happen about: {url} ? http status: {resp.status}.')
                pass

    def _convert_to_catalog_list(self, html_text) -> list:
        """
        input example:

        <ul class="chapter-ul">

            <li id="1" class="chapter-box"><span class="sign minus">-</span><b>杂项1</b></li>
            <li>
              <ul data-enum="21" class="episode-ul">
                <a href="/admin/novelReading?cid=71343" data-id="71343"
                   data-cost="0" data-payed="0" data-uid="61162" class="to-read">

                    <li class="episode-box ">
                        <span>第1话 章节标题&nbsp;</span>
                        <small></small>
                        <span>
                            <span title="创建时间：2023-07-10 12:01:42；更新时间：2023-07-13 06:34:43">23-07-10 12:01</span>
                            &nbsp;
                            <small title="更新时间：2023-07-13 06:34:43">(<u>更新</u>)</small>
                        </span>
                    </li>
                </a>
                <a>...</a>
              </ul>
            </li>

            <li id="2" class="chapter-box"><span class="sign minus">-</span><b>杂项2</b></li>
            <li>
              <ul class=“episode-ul”>...</ul>
            </li>

            ...
        <li>

        :param catalog_html_lis:
        :return:
        """
        # return example:
        # [{vid:1,volume_title: "XX", chapters:[[chapter_title,chapter_url],[xx,yy],[...] ]},{},{}]
        catalog_list = []

        soup = BeautifulSoup(html_text, 'html.parser')
        ul_element = soup.find('ul', {'class': 'chapter-ul'})

        if ul_element:
            # 使用.find_all()方法并传递recursive=False参数，获取<ul>元素的直接子代<li>
            li_elements = ul_element.find_all('li', recursive=False)

            _current_volume = []
            _current_volume_text = ''
            _volume_index = 0

            for idx, li in enumerate(li_elements):

                class_value = li.get('class')
                if class_value and 'chapter-box' in class_value:
                    volume_name = li.find("b").text

                    _volume_index += 1
                    # reset current_* variables
                    _current_volume_text = volume_name
                    _current_volume = []

                    catalog_list.append({
                        'vid': _volume_index,
                        'volume_title': _current_volume_text,
                        'chapters': _current_volume
                    })
                else:
                    # handle li
                    chapter_link_items = li.select('a.to-read')

                    for idx, chapter_a_item in enumerate(chapter_link_items):
                        a_href = chapter_a_item['href']
                        whole_url = urljoin('https://masiro.me', a_href)

                        chapter_title = chapter_a_item.find('li').find('span').text
                        # remove `&nbsp;` and `\r\n`.
                        chapter_title = chapter_title.strip()
                        # todo fix remove \xa0
                        chapter_title = re.sub(r'&nbsp;', '', chapter_title)

                        # todo add chapter pricing field if exists
                        _current_volume.append([chapter_title, whole_url])

        return catalog_list

    def _handle_select_volume(self, catalog_list):
        def _reduce_catalog_by_selection(catalog_list, selection_array):
            return [volume for volume in catalog_list if volume['vid'] in selection_array]

        def _get_volume_choices(catalog_list):
            """
            [(volume_title,vid),(volume_title,vid),...]

            :param catalog_list:
            :return:
            """
            return [(volume['volume_title'], volume['vid']) for volume in catalog_list]

        # step 1: need to show UI for user to select one or more volumes,
        # step 2: then reduce the whole catalog_list to a reduced_catalog_list based on user selection
        # UI show
        question_name = 'Selecting volumes'
        question_description = "Which volumes you want to download?(select one or multiple volumes)"
        # [(volume_title,vid),(volume_title,vid),...]
        volume_choices = _get_volume_choices(catalog_list)
        questions = [
            inquirer.Checkbox(question_name,
                              message=question_description,
                              choices=volume_choices, ),
        ]
        # user input
        # answers: {'Selecting volumes': [3, 6]}
        answers = inquirer.prompt(questions)
        catalog_list = _reduce_catalog_by_selection(catalog_list, answers[question_name])
        return catalog_list

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
        # TODO design image path
        return super().get_image_filename(url)

    async def _masiro_get_token(self, login_info: MasiroLoginInfo, session):
        res = await aiohttp_get_with_retry(session, login_info.login_url, self.request_headers(), logger=self.logger)

        page_body = html.fromstring(res)
        token = str(page_body.xpath('//input[@class=\'csrf\']/@value')[0])
        self.logger.info(f'token: {token}')

        login_info.token = token

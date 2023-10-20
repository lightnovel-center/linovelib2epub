import asyncio
import json
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
        novel = asyncio.run(self._fetch())
        return novel

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
            novel = await self._crawl_book_basic_info_with_catalog(book_url, session)

        return novel

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

        new_novel = LightNovel()
        new_novel.book_id = self.spider_settings['book_id']
        new_novel.book_title = title
        new_novel.author = author
        new_novel.description = brief_introduction
        new_novel.book_cover = urljoin(self.spider_settings["base_url"],cover_src)
        new_novel.book_cover_local = self.get_image_filename(cover_src,
                                                             middle_folder_name=str(self.spider_settings["book_id"]))
        new_novel.mark_basic_info_ready()

        catalog_list = self._convert_to_catalog_list(html_text)

        # select_volume_mode
        if self.spider_settings['select_volume_mode']:
            catalog_list = self._handle_select_volume(catalog_list)

        #  todo pre-buy chapters before downloading

        page_url_set = {chapter[1] for volume_dict in catalog_list for chapter in volume_dict['chapters']}
        url_to_page = await self.download_page_urls(session, page_url_set)

        #  Main goals:
        #  1. extract body and update dict
        #  2. update image src to local file path in body content,
        #  3. generate illustration_dict.

        for url, page in url_to_page.items():
            url_to_page[url] = self._extract_body_content(page)

        illustration_dict: Dict[Union[int, str], List[str]] = dict()

        volume_id = 0
        for volume_dict in catalog_list:
            volume_id += 1
            middle_folder_name = f'{self.spider_settings["book_id"]}-{volume_id}'

            new_volume = LightNovelVolume(volume_id=volume_id)
            new_volume.title = volume_dict['volume_title']

            self.logger.info(f'volume: {volume_dict["volume_title"]}')

            illustration_dict.setdefault(volume_dict['vid'], [])

            chapter_id = -1
            chapter_list = []  # store chapter for removing duplicate images in the first chapter
            for chapter in volume_dict['chapters']:
                chapter_id += 1
                chapter_title = chapter[0]

                new_chapter = LightNovelChapter(chapter_id=chapter_id)
                new_chapter.title = chapter_title
                # new_chapter.content = 'UNSOLVED'
                self.logger.info(f'chapter : {chapter_title}')

                chapter_url = chapter[1]
                chapter_body = url_to_page[chapter_url]

                # one page per chapter
                images_soup = BeautifulSoup(chapter_body, 'lxml').find_all('img')
                for _, image in enumerate(images_soup):
                    # Images src analysis:
                    # https://i.ibb.co/1fRfdhs/6f9fbd2762d0f7039cfafb8d0bfa513d2797c5a0.jpg
                    # https://masiro.moe/data/attachment/forum/202103/07/173827oqkmqhcbylyytty9.jpg => 526 status code
                    # https://www.masiro.me/images/encode/fy-221114012533-99Qz.jpg

                    # 可能为站内链接，也可能是站外链接。因为url没有固定格式
                    # 这里我们需要自定义一个中间的文件夹名称，用于分割不同的爬虫实例。
                    # 为了让文件夹名称更加可读和具有语义，这里使用 bookid-volumeid 作为隔离。

                    # 举例，例如 bookid为 875，volume_id 取本地自增id(例如3)，那么 875-3 就是结果。
                    # 最后，将这个分隔符和图片原来的文件名拼接，得到 875-3/fy-221114012533-99Qz.jpg 这样格式的链接。
                    # 更加具体地，为 XXXX/masiro.me/875-3/fy-221114012533-99Qz.jpg

                    image_src = image.get("src")
                    src_value = re.search('(?<= src=").*?(?=")', str(image))
                    local_image_uri = self.get_image_filename(src_value.group(), middle_folder_name=middle_folder_name)

                    # local_image_uri is "[volume_img_folder]/[filename]"
                    # example: https://img.linovelib.com/0/682/117077/50675.jpg => [image_download_folder]/117077/50677.jpg
                    # 117077 is [volume_img_folder]
                    # 50677.jpg is the [filename]

                    replace_value = f'{self.spider_settings["image_download_folder"]}/' + local_image_uri
                    new_image = str(image).replace(str(src_value.group()), replace_value)

                    # replace all remote images src to local file path
                    chapter_body = chapter_body.replace(str(image), new_image)

                    illustration_dict[volume_dict['vid']].append(image_src)

                new_chapter.content = chapter_body
                chapter_list.append(new_chapter)

            for chapter in chapter_list:
                new_volume.add_chapter(cid=chapter.chapter_id, title=chapter.title, content=chapter.content)

            # store [volume_img_folders] and [volume_cover] in volume dict
            if illustration_dict[volume_dict['vid']]:
                volume_images = illustration_dict[volume_dict['vid']]
                if volume_images:
                    cover_image_url = volume_images[0]
                    path = self.get_image_filename(cover_image_url, middle_folder_name)
                    new_volume.volume_cover = path

                new_volume.volume_img_folders = {middle_folder_name}

            new_novel.add_volume(
                vid=new_volume.volume_id,
                title=new_volume.title,
                chapters=new_volume.chapters,
                volume_img_folders=new_volume.volume_img_folders,
                volume_cover=new_volume.volume_cover
            )

        new_novel.set_illustration_dict(illustration_dict)
        new_novel.mark_volumes_content_ready()

        return new_novel

    def _extract_body_content(self, page: str):
        """
        :param page:
        :return:
        """
        html_content = BeautifulSoup(page, 'lxml')
        body_content = html_content.find('div', {'class': 'nvl-content'}).text
        return body_content

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

        # make sure data is ok.
        for page_content in url_to_page.values():
            if page_content == "NOT_DOWNLOAD_READY":
                raise LinovelibException('如果这个断言被触发，那么证明代码逻辑有问题。青春猪头少年不会梦到奇奇怪怪的BUG。')

        return url_to_page

    async def _download_page(self, session, url) -> str | None:
        #  use semaphore to control concurrency
        max_concurrency = 2
        sem = asyncio.Semaphore(max_concurrency)

        async with sem:
            timeout = aiohttp.ClientTimeout(total=30, connect=15)  # per request timeout
            async with session.get(url, headers=self.request_headers(), timeout=timeout) as resp:
                if resp.status == 200:
                    self.logger.info(f'fetch page: {url} ok.')
                    return await resp.text()
                elif resp.status == 404:
                    # maybe 404 etc. Now ignore it, don't raise error to avoid retry dead loop
                    # 404 is considered as success => don't retry
                    self.logger.error(f'{url} 404. skip it')
                    pass
                else:
                    # 429 too many requests => should retry
                    # 503 Service Unavailable => should retry
                    # ...... => should retry
                    self.logger.error(f'what happen about: {url} ? http status: {resp.status}.')
                    raise LinovelibException(f'fetch page url {url} failed with error status {resp.status}.')

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

    def get_image_filename(self, url: str, middle_folder_name: str | None = None) -> str:
        return middle_folder_name + "/" + url.rsplit('/', 1)[1]

    async def _masiro_get_token(self, login_info: MasiroLoginInfo, session):
        res = await aiohttp_get_with_retry(session, login_info.login_url, self.request_headers(), logger=self.logger)

        page_body = html.fromstring(res)
        token = str(page_body.xpath('//input[@class=\'csrf\']/@value')[0])
        self.logger.info(f'token: {token}')

        login_info.token = token

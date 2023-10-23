import asyncio
import re
from typing import Dict, Any, List

import aiohttp
import inquirer
from bs4 import BeautifulSoup

from linovelib2epub.logger import Logger
from linovelib2epub.models import LightNovel, LightNovelImage, CatalogBaseVolume, CatalogBaseChapter
from linovelib2epub.spider import BaseNovelWebsiteSpider
from linovelib2epub.utils import aiohttp_get_with_retry


class Wenku8Spider(BaseNovelWebsiteSpider):

    def __init__(self, spider_settings: Dict[str, Any]):
        super().__init__(spider_settings)
        self.logger = Logger(logger_name=type(self).__name__,
                             log_filename=self.spider_settings["log_filename"]).get_logger()
        self._catalog_url = ""

    def request_headers(self) -> Dict[str, Any]:
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.57'
        }

    def fetch(self) -> LightNovel:
        novel = asyncio.run(self._fetch())
        return novel

    async def _fetch(self) -> LightNovel:
        jar = aiohttp.CookieJar(unsafe=True)
        conn = aiohttp.TCPConnector(ssl=False)
        trust_env = False if self.spider_settings["disable_proxy"] else True
        timeout = aiohttp.ClientTimeout(total=30, connect=15)

        async with aiohttp.ClientSession(connector=conn, trust_env=trust_env, cookie_jar=jar,
                                         timeout=timeout) as session:
            novel = await self._fetch_basic_info(session)
            await self._fetch_catalog_content(session, novel)
            return novel

    async def _fetch_basic_info(self, session) -> LightNovel:
        # index url
        # https://www.wenku8.net/book/2961.htm
        book_id = self.spider_settings["book_id"]
        book_index_url = f"https://www.wenku8.net/book/{book_id}.htm"
        page_text = await aiohttp_get_with_retry(session, book_index_url, headers=self.request_headers())

        soup = BeautifulSoup(page_text, 'lxml')
        title = soup.select_one("#content table:nth-child(1) span b").text
        cover_src = soup.select_one("#content table img")['src']
        # 说作者：一色一凛
        author_text = soup.select_one("#content table:nth-child(1) tr:nth-child(2) td:nth-child(2)").text
        author = re.sub(r"小说作者：\s*", "", author_text)
        # desc
        # nth-of-type 不会选择内层的table，区别于nth-of-child()
        desc = soup.select("#content table:nth-of-type(2) td:nth-child(2) span")[-1].text

        # catalog url example https://www.wenku8.net/novel/2/2961/index.htm
        catalog_url = soup.select_one("legend + div > a")['href']
        self._catalog_url = catalog_url

        new_novel = LightNovel()
        new_novel.book_id = self.spider_settings["book_id"]
        new_novel.author = author
        new_novel.book_title = title
        new_novel.book_cover = LightNovelImage(site_base_url=self.spider_settings["base_url"],
                                               related_page_url=book_index_url,
                                               remote_src=cover_src,
                                               book_id=self.spider_settings["book_id"],
                                               is_book_cover=True)
        new_novel.description = desc
        new_novel.mark_basic_info_ready()

        return new_novel

    async def _fetch_catalog_content(self, session, novel):
        catalog_url = self._catalog_url
        catalog_html = await aiohttp_get_with_retry(session, catalog_url, self.request_headers())

        catalog_list: List[CatalogBaseVolume] = self._convert_to_catalog_list(catalog_html)
        if self.spider_settings['select_volume_mode']:
            catalog_list = self._handle_select_volume(catalog_list)

        await self.fetch_chapters(session, catalog_list, novel)

    def _convert_to_catalog_list(self, catalog_html) -> List[CatalogBaseVolume]:
        # => volume title
        # <td class="vcss" colspan="4" vid="119695">第一卷</td>

        # => chapter title
        # <td class="ccss"><a href="119696.htm">第1话 无用之才</a></td>
        # <td class="ccss"><a href="119697.htm">第2话 蠢蠢欲动的暴食技能</a></td>
        # ......
        # <td class="ccss"><a href="119722.htm">后记</a></td>
        # <td class="ccss"><a href="119723.htm">插图</a></td>  ---> move this chapter to first index in this volume array

        # => volume title
        # <td class="vcss" colspan="4" vid="146004">第二卷</td>

        soup = BeautifulSoup(catalog_html, 'lxml')
        catalog_items = soup.find('table').find_all('td')

        catalog_list: List[CatalogBaseVolume] = []

        _current_chapters: List[CatalogBaseChapter] = []
        _current_volume_title = ""
        _volume_index = 0

        for idx, catalog_item in enumerate(catalog_items):
            catalog_item_text = catalog_item.text
            item_css_class = catalog_item['class']

            # is volume title
            if 'vcss' in item_css_class:
                _volume_index += 1

                # reset current_* variables
                _current_volume_title = catalog_item_text
                _current_chapters: List[CatalogBaseChapter] = []

                new_volume = CatalogBaseVolume(
                    vid=_volume_index,
                    volume_title=_current_volume_title,
                    chapters=_current_chapters
                )

                catalog_list.append(new_volume)
            # is chapter
            elif 'ccss' in item_css_class:
                # bug case : https://www.wenku8.net/novel/3/3500/index.htm
                if catalog_item.find("a") and catalog_item.find("a")['href']:
                    href = catalog_item.find("a")["href"]
                    # https://www.wenku8.net/novel/2/2961/index.htm + 146006.htm => https://www.wenku8.net/novel/2/2961/146006.htm
                    chapter_url = f'{self._catalog_url.rsplit("/", 1)[0]}/{href}'

                    new_chapter: CatalogBaseChapter = CatalogBaseChapter(
                        chapter_title=catalog_item_text,
                        chapter_url=chapter_url
                    )

                    if catalog_item_text == '插图':
                        _current_chapters.insert(0, new_chapter)
                    else:
                        _current_chapters.append(new_chapter)
            else:
                pass

        return catalog_list

    @staticmethod
    def _handle_select_volume(catalog_list: List[CatalogBaseVolume]):
        def _reduce_catalog_by_selection(catalog_list: List[CatalogBaseVolume], selection_array):
            return [volume for volume in catalog_list if volume.vid in selection_array]

        def _get_volume_choices(catalog_list: List[CatalogBaseVolume]):
            return [(volume.volume_title, volume.vid) for volume in catalog_list]

        # step 1: need to show UI for user to select one or more volumes,
        # step 2: then reduce the whole catalog_list to a reduced_catalog_list based on user selection
        # UI show
        question_name = 'Selecting volumes'
        question_description = "Which volumes you want to download?(select one or multiple volumes)"
        volume_choices = _get_volume_choices(catalog_list)
        questions = [
            inquirer.Checkbox(question_name,
                              message=question_description,
                              choices=volume_choices, ),
        ]
        # user input
        # answers: {'Selecting volumes': [3, 6]}
        answers: Dict[str, List[int]] = inquirer.prompt(questions)
        catalog_list = _reduce_catalog_by_selection(catalog_list, answers[question_name])
        return catalog_list

    def extract_body_content(self, page: str):
        """
        :param page:
        :return:
        """
        html_content = BeautifulSoup(page, 'lxml')
        content_body = html_content.select_one('#content')

        # remove all contentdp div
        contentdps = content_body.select("#contentdp")
        for element in contentdps:
            element.decompose()

        # &nbsp;&nbsp;&nbsp;&nbsp;我一回到王都圣法特，就为了换取打倒魔物的赏金来到兑换所。<br/>
        # <br/>
        # &nbsp;&nbsp;&nbsp;&nbsp;只见壮硕的武人们你推我挤，偶尔还听见怒骂声传来。似乎是为了交换的条件和柜台人员起了争执。<br/>
        # <br/>

        # maybe we should remove nbsp and br, re-wrap it with a `p` container

        return content_body.prettify()

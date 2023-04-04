import re
import time
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

import demjson3
import inquirer
import requests
from bs4 import BeautifulSoup

from ..exceptions import LinovelibException
from ..models import LightNovel, LightNovelChapter, LightNovelVolume
from ..utils import (cookiedict_from_str, create_folder_if_not_exists,
                     request_with_retry)
from . import BaseNovelWebsiteSpider


class LinovelibMobileSpider(BaseNovelWebsiteSpider):

    def __init__(self, spider_settings: Optional[Dict] = None):
        super().__init__(spider_settings)
        self._init_http_client()

    def dump_settings(self):
        self.logger.info(self.spider_settings)

    def request_headers(self, referer: str = '', random_ua: bool = True):
        default_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
        default_referer = 'https://w.linovelib.com'
        headers = {
            'referer': referer if referer else default_referer,
            'user-agent': self.spider_settings['random_useragent'] if random_ua else default_ua
        }
        return headers

    def fetch(self) -> LightNovel:
        start = time.perf_counter()
        novel_whole = self._fetch()
        self.logger.info('(Perf metrics) Fetch Book took: {} seconds'.format(time.perf_counter() - start))

        return novel_whole

    def get_image_filename(self, url):
        return '-'.join(url.split("/")[-4:])

    def _init_http_client(self):
        self.session = requests.Session()

        if self.spider_settings["disable_proxy"]:
            self.session.trust_env = False

        # cookie example: PHPSESSID=...; night=0; jieqiUserInfo=...; jieqiVisitInfo=...
        if self.spider_settings["http_cookie"]:
            cookie_dict = cookiedict_from_str(self.spider_settings["http_cookie"])
            cookiejar = requests.utils.cookiejar_from_dict(cookie_dict)
            self.session.cookies = cookiejar

    def _crawl_book_basic_info(self, url):
        result = request_with_retry(self.session,
                                    url,
                                    headers=self.request_headers(),
                                    retry_max=self.spider_settings['http_retries'],
                                    timeout=self.spider_settings["http_timeout"],
                                    logger=self.logger)

        if result and result.status_code == 200:
            self.logger.info(f'Succeed to get the novel of book_id: {self.spider_settings["book_id"]}')

            # pass html text to beautiful soup parser
            soup = BeautifulSoup(result.text, 'lxml')
            try:
                book_title = soup.find('h2', {'class': 'book-title'}).text
                author = soup.find('div', {'class': 'book-rand-a'}).text[:-2]
                book_summary = soup.find('section', id="bookSummary").text
                # see issue #10, strip invalid suffix characters after ? from cover url
                book_cover_url = soup.find('img', {'class': 'book-cover'})['src'].split("?")[0]
                return book_title, author, book_summary, book_cover_url

            except (Exception,):
                self.logger.error(f'Failed to parse basic info of book_id: {self.spider_settings["book_id"]}')

        return None

    def _crawl_book_content(self, catalog_url):
        book_catalog_rs = None
        try:
            book_catalog_rs = request_with_retry(self.session,
                                                 catalog_url,
                                                 headers=self.request_headers(),
                                                 retry_max=self.spider_settings['http_retries'],
                                                 timeout=self.spider_settings["http_timeout"],
                                                 logger=self.logger)
        except (Exception,):
            self.logger.error(f'Failed to get normal response of {catalog_url}. It may be a network issue.')

        if book_catalog_rs and book_catalog_rs.status_code == 200:
            self.logger.info(f'Succeed to get the catalog of book_id: {self.spider_settings["book_id"]}')

            # parse catalog data
            soup_catalog = BeautifulSoup(book_catalog_rs.text, 'lxml')
            # chapter_count = soup_catalog.find('h4', {'class': 'chapter-sub-title'}).find('output').text
            catalog_wrapper = soup_catalog.find('ol', {'id': 'volumes'})
            catalog_lis = catalog_wrapper.find_all('li')

            # catalog_lis is an array: [li, li, li, ...]
            # example format:
            # <li class="chapter-bar chapter-li">第一卷 夏娃在黎明时微笑</li>
            # <li class="chapter-li jsChapter"><a href="/novel/682/117077.html" class="chapter-li-a "><span class="chapter-index ">插图</span></a></li>
            # <li class="chapter-li jsChapter"><a href="/novel/682/32683.html" class="chapter-li-a "><span class="chapter-index ">「彩虹与夜色的交会──远在起始之前──」</span></a></li>

            catalog_list = self._convert_to_catalog_list(catalog_lis)
            if self.spider_settings['select_volume_mode']:
                catalog_list = self._handle_select_volume(catalog_list)

            new_novel = LightNovel()
            illustration_dict: Dict[Union[int, str], List[str]] = dict()
            url_next = ''

            volume_id = 0
            for volume in catalog_list:
                volume_id += 1

                new_volume = LightNovelVolume(vid=volume_id)
                new_volume.title = volume['volume_title']

                self.logger.info(f'volume: {volume["volume_title"]}')

                illustration_dict.setdefault(volume['vid'], [])

                chapter_id = -1
                for chapter in volume['chapters']:
                    chapter_content = ''
                    chapter_title = chapter[0]
                    chapter_id += 1

                    new_chapter = LightNovelChapter(cid=chapter_id)
                    new_chapter.title = chapter_title
                    # new_chapter.content = 'UNSOLVED'

                    self.logger.info(f'chapter : {chapter_title}')

                    # fix broken links in place(catalog_lis) if exits
                    # - if chapter[1] is valid link, assign it to url_next
                    # - if chapter[1] is not a valid link,e.g. "javascript:cid(0)" etc. use url_next
                    if not self._is_valid_chapter_link(chapter[1]):
                        # now the url_next value is the correct link of of chapter[1].
                        chapter[1] = url_next
                    else:
                        url_next = chapter[1]

                    # goal: solve all page links of a certain chapter
                    while True:
                        resp = request_with_retry(self.session, url_next, logger=None)
                        if resp:
                            soup = BeautifulSoup(resp.text, 'lxml')
                        else:
                            raise Exception(f'[ERROR]: request {url_next} failed.')

                        first_script = soup.find("body", {"id": "aread"}).find("script")
                        first_script_text = first_script.text
                        # alternative: use split(':')[-1] to get read_params_text
                        read_params_text = first_script_text[len('var ReadParams='):]
                        read_params_json = demjson3.decode(read_params_text)
                        url_next = urljoin(self.spider_settings["base_url"], read_params_json['url_next'])

                        if '_' in url_next:
                            chapter.append(url_next)
                        else:
                            break

                    # THINK: after solving all page links of catalog. It's possible to utilize multi-thread tech
                    # to fetch page content?

                    # handle page content(text and img)
                    for page_link in chapter[1:]:
                        page_resp = request_with_retry(self.session, page_link,
                                                       retry_max=self.spider_settings['http_retries'],
                                                       timeout=self.spider_settings["http_timeout"],
                                                       logger=self.logger)
                        if page_resp:
                            soup = BeautifulSoup(page_resp.text, 'lxml')
                        else:
                            raise Exception(f'[ERROR]: request {page_link} failed.')

                        images = soup.find_all('img')
                        article = str(soup.find(id="acontent"))

                        for _, image in enumerate(images):
                            # img tag format: <img src="https://img.linovelib.com/0/682/117078/50677.jpg" border="0" class="imagecontent">
                            image_src = image['src']
                            illustration_dict[volume['vid']].append(image_src)
                            src_value = re.search(r"(?<=src=\").*?(?=\")", str(image))

                            # example: https://img.linovelib.com/0/682/117077/50675.jpg => [folder]/0-682-117078-50677.jpg
                            # here we convert its path `0/682/117078/50677.jpg` to `0-682-117078-50677.jpg` as filename.
                            local_image_uri = self.get_image_filename(src_value.group())
                            replace_value = f'{self.spider_settings["image_download_folder"]}/' + local_image_uri
                            # replace all remote images src to local file path
                            article = article.replace(str(src_value.group()), str(replace_value))

                        article = self._sanitize_html(article)
                        chapter_content += article

                        self.logger.info(f'Processing page... {page_link}')

                    # Here, current chapter's content has been solved
                    new_chapter.content = chapter_content
                    new_volume.add_chapter(cid=new_chapter.cid,
                                           title=new_chapter.title,
                                           content=new_chapter.content)

                new_novel.add_volume(vid=new_volume.vid,
                                     title=new_volume.title,
                                     chapters=new_volume.chapters)

            new_novel.set_illustration_dict(illustration_dict)

            return new_novel

        else:
            self.logger.error(f'Failed to get the catalog of book_id: {self.spider_settings["book_id"]}')

        return None

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
    def _sanitize_html(html):
        """
        strip useless script on body tag by reg or soup method.

        e.g. <script>zation();</script>

        :param html:
        :return:
        """
        return re.sub(r'<script.+?</script>', '', html, flags=re.DOTALL)

    def _convert_to_catalog_list(self, catalog_html_lis):
        # return example:
        # [{vid:1,volume_title: "XX", chapters:[[xxx,u1,u2,u3],[xx,u1,u2],[...] ]},{},{}]

        catalog_list = []
        current_volume = []
        current_volume_text = catalog_html_lis[0].text
        volume_index = 0

        for index, catalog_li in enumerate(catalog_html_lis):
            catalog_li_text = catalog_li.text

            # is volume name
            if 'chapter-bar' in catalog_li['class']:
                volume_index += 1
                # reset current_* variables
                current_volume_text = catalog_li_text
                current_volume = []

                catalog_list.append({
                    'vid': volume_index,
                    'volume_title': current_volume_text,
                    'chapters': current_volume
                })
            # is normal chapter
            else:
                href = catalog_li.find("a")["href"]
                whole_url = urljoin(self.spider_settings['base_url'], href)
                current_volume.append([catalog_li_text, whole_url])

        return catalog_list

    @staticmethod
    def _is_valid_chapter_link(href: str):
        # normal link example: https://w.linovelib.com/novel/682/117077.html
        # broken link example: javascript: cid(0)
        # use https://regex101.com/ to debug regular expression
        reg = r"\S+/novel/\d+/\S+\.html"
        re_match = bool(re.match(reg, href))
        return re_match

    @staticmethod
    def _extract_image_list(image_dict=None):
        image_url_list = []
        for volume_images in image_dict.values():
            for index in range(0, len(volume_images)):
                image_url_list.append(volume_images[index])

        return image_url_list

    def _fetch(self):
        book_url = f'{self.spider_settings["base_url"]}/{self.spider_settings["book_id"]}.html'
        book_catalog_url = f'{self.spider_settings["base_url"]}/{self.spider_settings["book_id"]}/catalog'
        create_folder_if_not_exists(self.spider_settings['pickle_temp_folder'])

        book_basic_info = self._crawl_book_basic_info(book_url)
        if not book_basic_info:
            raise LinovelibException(f'Fetch book_basic_info of {self.spider_settings["book_id"]} failed.')

        new_novel_with_content = self._crawl_book_content(book_catalog_url)
        if not new_novel_with_content:
            raise LinovelibException(f'Fetch book_content of {self.spider_settings["book_id"]} failed.')

        # do better: use named tuple or class like NovelBasicInfoGroup
        book_title, author, book_summary, book_cover = book_basic_info
        novel_whole = new_novel_with_content
        novel_whole.mark_volumes_content_ready()

        # set book basic info
        novel_whole.bid = self.spider_settings['book_id']
        novel_whole.book_title = book_title
        novel_whole.author = author
        novel_whole.description = book_summary
        novel_whole.book_cover = book_cover
        novel_whole.book_cover_local = self.get_image_filename(book_cover)
        novel_whole.mark_basic_info_ready()

        return novel_whole
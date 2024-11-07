import html as builtin_html_lib
import io
import random
import re
import sys
import textwrap
import time
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urljoin

import demjson3
import inquirer
import pytesseract
import requests
from DrissionPage import ChromiumOptions, WebPage
from PIL import Image
from bs4 import (BeautifulSoup, PageElement)

from . import BaseNovelWebsiteSpider
from .linovelib_mobile_rule import LinovelibMobileRuleParser
from .linovelib_pc_rule import LinovelibPCRuleParser
from ..exceptions import LinovelibException, PageContentAbnormalException, EmptyTitleError, NotIntactTextError, \
    EmptyArticleError
from ..models import LightNovel, LightNovelChapter, LightNovelVolume, LightNovelImage, CatalogLinovelibChapter, \
    CatalogLinovelibVolume
from ..utils import (cookiedict_from_str, create_folder_if_not_exists,
                     requests_get_with_retry)


class BaseLinovelibSpider(BaseNovelWebsiteSpider):

    def __init__(self, spider_settings: Optional[Dict] = None):
        super().__init__(spider_settings)
        self._debug_mode = self.spider_settings['log_level'].lower() == 'debug' or False
        self._init_http_client()

        traditional = self.spider_settings['traditional']
        mobile = self.spider_settings['mobile']
        # rule parsing. maybe need to refactor these codes
        if mobile:
            rule_parser = LinovelibMobileRuleParser(logger=self.logger,
                                                    traditional=traditional,
                                                    disable_proxy=self.spider_settings["disable_proxy"])
            mapping_result = rule_parser.generate_mapping_result()
        else:
            rule_parser = LinovelibPCRuleParser(logger=self.logger,
                                                traditional=traditional,
                                                disable_proxy=self.spider_settings["disable_proxy"])
            mapping_result = rule_parser.generate_mapping_result()

        self._html_content_id = mapping_result.content_id
        self.logger.info(f'_html_content_id={self._html_content_id}')
        self._mapping_dict = mapping_result.mapping_dict
        self.logger.info(f'len(_mapping_dict)={len(self._mapping_dict.keys())}')

        self.FETCH_CHAPTER_CONCURRENCY_LEVEL = 1

        self._is_driver_initialized = False
        self._driver = None

    def request_headers(self, referer: str = '', random_ua: bool = True):
        """
        TODO 不要过度设计，这个方法可以置空，将实现推迟到子类。只有子类才知道该如何构造特定的 headers 来应对特定的场合（图片，或者页面文本）
        :param referer:
        :param random_ua:
        :return:
        """
        default_mobile_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'
        default_referer = 'https://www.bilinovel.com'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Referer': referer if referer else default_referer,
            'User-Agent': default_mobile_ua
        }
        return headers

    # 名存实亡，没有被调用，而是直接调用子类的同名方法
    def fetch(self) -> LightNovel:
        start = time.perf_counter()
        if self.spider_settings['mobile']:
            novel_whole = LinovelibSpiderMobile().fetch()
        else:
            novel_whole = LinovelibSpiderPC().fetch()
        self.logger.info('(Perf metrics) Fetch Book took: {} seconds'.format(time.perf_counter() - start))

        return novel_whole

    def _init_http_client(self):
        """
        Tunes http session as needed.

        Guideline: Don't move many concrete init logics to super class __init__()
        """
        self._session = requests.Session()

        if self.spider_settings["disable_proxy"]:
            self._session.trust_env = False


    def _fetch_catalog(self, url: str, max_retries: int = 5) -> str | None:
        """
        这个是专门用于处理目录页的爬取。因为这一页的元素检测和爬取正文页不太一致。
        :param url:
        :param max_retries:
        :return:
        """
        driver: WebPage = self._driver
        driver.set.load_mode.eager()

        def _check_failed_pattern(html, url):
            # Determine whether the content of the page has the following tags(failed case):
            failed_patterns = ['You are being rate limited', ' 抱歉，章节内容不支持该浏览器显示 ']
            for pattern in failed_patterns:
                match = re.search(pattern, html)
                if match:
                    raise PageContentAbnormalException(f'The page content of {url} is not desired. Reason: {pattern}')

        def _check_page_content_mobile(html, url):
            pass

        def _check_page_content_pc(html, url):
            pass

        request_count = 0
        # total requests num = self(1) + max_retries
        # if max_retries= 5, then the max try count is 0,1,2,3,4,5 = 6 times
        while request_count <= max_retries:
            try:
                is_url_available = driver.get(url, retry=0, interval=5, timeout=10)
                loaded = driver.wait.doc_loaded()
                html = driver.html

                if html:
                    _check_failed_pattern(html, url)
                    # TODO handle cloudflare turnstile. => CAN copy masiro logic
                    if self.spider_settings['mobile']:
                        _check_page_content_mobile(html, url)
                    else:
                        _check_page_content_pc(html, url)

                    self.logger.info(f'page {url} => ok.')
                    return html
                else:
                    # ...... => should retry
                    self.logger.error(f'page {url} => should retry.')
                    raise LinovelibException(f'fetch page url {url} failed with error status ?.')
            except PageContentAbnormalException as e:
                self.logger.warn(f"{e}")
            except Exception as e:
                self.logger.warn(f"{url} encountered {e.__class__.__name__}.")

            request_count += 1
            n = request_count
            random_number_seconds = round(random.uniform(0, 1), 2)  # 0.01-0.99s
            maximum_backoff = 10
            retry_interval = min(round(((2 ** (n - 1)) + random_number_seconds), 2), maximum_backoff)

            self.logger.warning(
                f'Retrying {url}...({request_count}/{max_retries}); retry_interval: {retry_interval}(s)')
            time.sleep(retry_interval)

        return None

    def _fetch_page(self, url: str, max_retries: int = 5) -> str | None:
        if not self._is_driver_initialized:
            self._init_drissionpage_driver(url)

        driver: WebPage = self._driver
        # speedup 1s to 0.3s per page averagely
        driver.set.load_mode.eager()

        def _check_failed_pattern(html, url):
            # Determine whether the content of the page has the following tags(failed case):
            failed_patterns = ['You are being rate limited', ' 抱歉，章节内容不支持该浏览器显示 ']
            for pattern in failed_patterns:
                match = re.search(pattern, html)
                if match:
                    raise PageContentAbnormalException(f'The page content of {url} is not desired. Reason: {pattern}')

        def _check_page_content_mobile(html, url):
            # check whether the html string has correct text
            html_content = BeautifulSoup(html, 'lxml')
            new_title = html_content.find(id='atitle')
            if not new_title:
                msg = f"page {url} => doesn't have the desired tag, maybe caught by cloudflare. Need retry."
                self.logger.warning(msg)
                # better: 检测是否遇到 CF 挑战. 如果遇到，必须在这里解决这次 CF。
                # 抛异常，将当前这个 url 的抓取任务延迟到下一轮尝试
                raise PageContentAbnormalException(msg)

        def _check_page_content_pc(html, url):
            # check whether the html string has correct text
            html_content = BeautifulSoup(html, 'lxml')
            main_text = html_content.find(id='mlfy_main_text')
            if not (main_text and main_text.select_one('h1') and main_text.select_one('#TextContent')):
                msg = f"page {url} => doesn't have the desired tag, maybe caught by cloudflare. Need retry."
                self.logger.warning(msg)
                # better: 检测是否遇到 CF 挑战. 如果遇到，必须在这里解决这次 CF。
                # 抛异常，将当前这个 url 的抓取任务延迟到下一轮尝试
                raise PageContentAbnormalException(msg)

        def _patch_font_obfuscation(page, url):
            js_check = """
            const last_p = document.querySelector('#TextContent p:last-of-type')
            const p_style = window.getComputedStyle(last_p)
            const p_font_style = p_style.getPropertyValue('font-family')
            if (p_font_style && p_font_style.includes('read')) {
                return true;
            }
            return false;
            """
            try:
                if not self.spider_settings['mobile']:
                    has_font_obfuscation = page.run_js(js_check)
                    if has_font_obfuscation:
                        self.logger.debug(f'The page of {url} has font obfuscation.')
                        last_p = page.ele('css:#TextContent p:last-of-type')
                        last_p_utf16 = last_p.text.encode('unicode-escape')
                        self.logger.debug(f'Font obfuscation UTF-16: {last_p_utf16}')

                        # save artifacts if in debug mode
                        # '诲。'
                        # last_p.get_screenshot()
                        # refer doc: https://www.drissionpage.cn/ChromiumPage/screen/#%EF%B8%8F%EF%B8%8F-%EF%B8%8F%EF%B8%8F-%E5%85%83%E7%B4%A0%E6%88%AA%E5%9B%BE
                        bytes_str = last_p.get_screenshot(as_bytes='png')  # 返回截图二进制文本 `
                        image = Image.open(io.BytesIO(bytes_str))
                        text = pytesseract.image_to_string(image, lang='chi_sim+eng')

                        # remove all white-spaces and line-break on each side
                        new_text = text.replace(" ", "").strip()
                        self.logger.debug(f'The text of this patch is: {new_text}')
                        # https://www.drissionpage.cn/ChromiumPage/ele_operation/#%EF%B8%8F%EF%B8%8F-%E4%BF%AE%E6%94%B9%E5%85%83%E7%B4%A0
                        # if new_text is None,then keep original text
                        # Case: https://www.linovelib.com/novel/2356/83534_2.html 「…………」 => ''
                        if new_text:
                            # 转义 HTML
                            cleaned_html = re.sub(r'[\r\n]+', '<br>', new_text)
                            # 转义 HTML 特殊字符
                            escaped_html = builtin_html_lib.escape(cleaned_html)

                            self.logger.debug(f'{escaped_html=}')
                            # 这个 set 这一步有可能引发 browser 的 js execution error
                            last_p.set.innerHTML(escaped_html)

                        # 为了测量 OCR 的准确率，在 DEBUG 模式下，将【url，段落截图，OCR 识别结果，消毒 + 转义的结果】保存到相应的临时文件夹中。
                        # 后续可能需要采用策略模式，更换不同的 OCR 引擎。
                        if self._debug_mode:
                            # create an image contains all these infos
                            # url,screenshot,ocr_text,final_text
                            pass
            except Exception as e:
                # maybe js execution error
                self.logger.error(f'Error occurred in _patch_font_obfuscation(): {e}')
                pass

        request_count = 0
        # total requests num = self(1) + max_retries
        # if max_retries= 5, then total is 1+5=6
        while request_count <= max_retries:
            try:
                # 参阅 dp 源码： DrissionPage._pages.session_page.SessionPage._make_response 函数
                # 它这个重试机制是固定时间间隔的实现，比较粗糙。如果想要自定义指数退避算法，应该自行实现重试
                # interval=5 是重试间隔。这里因为 retry=0 因此也不关心网络请求的重试间隔
                is_url_available = driver.get(url, retry=0, interval=5, timeout=10)
                loaded = driver.wait.doc_loaded()
                _patch_font_obfuscation(driver, url)
                html = driver.html

                if html:
                    _check_failed_pattern(html, url)
                    if self.spider_settings['mobile']:
                        _check_page_content_mobile(html, url)
                    else:
                        _check_page_content_pc(html, url)

                    self.logger.info(f'page {url} => ok.')
                    return html
                else:
                    # ...... => should retry
                    self.logger.error(f'page {url} => should retry.')
                    raise LinovelibException(f'fetch page url {url} failed with error status ?.')
            except PageContentAbnormalException as e:
                self.logger.warn(f"{e}")
            except Exception as e:
                self.logger.warn(f"{url} encountered {e.__class__.__name__}.")

            request_count += 1
            n = request_count
            random_number_seconds = round(random.uniform(0, 1), 2)  # 0.01-0.99s
            maximum_backoff = 10
            retry_interval = min(round(((2 ** (n - 1)) + random_number_seconds), 2), maximum_backoff)

            self.logger.warning(
                f'Retrying {url}...({request_count}/{max_retries}); retry_interval: {retry_interval}(s)')
            time.sleep(retry_interval)

        return None

    def _init_drissionpage_driver(self, warm_up_url: str):
        co = ChromiumOptions()
        if self.spider_settings['browser_path']:
            # path = r'D:\Chrome\Chrome.exe'
            path = self.spider_settings['browser_path']
            co.set_browser_path(path).save()

        #  basic arguments
        arguments = [
            "-no-first-run",
            "-force-color-profile=srgb",
            "-metrics-recording-only",
            "-use-mock-keychain",
            "-export-tagged-pdf",
            "-no-default-browser-check",
            "-disable-background-mode",
            "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
            "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
            "-deny-permission-prompts",
            "-disable-gpu"
        ]
        for argument in arguments:
            co.set_argument(argument)

        # user arguments
        if self.spider_settings["headless"]:
            co.set_argument("--headless")

        # UA
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'
        co.set_argument(f"--user-agent={ua}")

        # SSL related
        # co.set_argument('--ignore-certificate-errors-spki-list')

        # suppress logging < FATAL
        # co.set_argument("log-level=3")

        page = WebPage(chromium_options=co)

        # 'zh-CN' 中文简体
        # 'zh' 中文
        # 'zh-TW' 中文（繁体）
        # 'zh-HK' 中文（中国香港特别行政区）
        navigator_language = page.run_js(script="return navigator.language.toLowerCase();")
        self.logger.info(f'Browser language ={navigator_language}')

        # try requesting a page to detect if it's ok
        page.get(warm_up_url)
        page.refresh()

        self._driver = page
        self._is_driver_initialized = True
        self.logger.info(' 初始化 Driver 完毕...')

    def _apply_crawl_delay(self, delay_name):
        crawl_delay = self.spider_settings.get(delay_name, None)
        if crawl_delay:
            time.sleep(crawl_delay)
            self.logger.debug(f'Apply {delay_name}(s): {crawl_delay}')

    def _remove_duplicate_images_in_html(self, chapter_list):
        # removing duplicate images in the first chapter
        # chapter_list[0] 表示这一卷的第 1 个章节，在 bilinovel 中是插图页，这个页面部分插图会重复，会出现在这一卷的后续章节中。
        # chapter_list[1:] 表示这一卷的第 2 个章节开始的所有章节，也就是正文章节。

        # 这个函数的作用就是将某一卷的第 1 个章节（插图章节）HTML 的所有重复图片 img 元素，全部去掉。

        def _filter_duplicate_images(match, img_src_list):
            img = match.group()
            img_src = re.search('(?<= src=").*?(?=")', img).group()
            if img_src in img_src_list:
                self.logger.info(f'Remove duplicate image in the first chapter... {img_src}')
                return ""
            else:
                return img

        img_src_list = []

        for chapter in chapter_list[1:]:
            img_src_list.extend(
                [re.search('(?<= src=").*?(?=")', i).group() for i in re.findall('<img.*?/>', chapter.content)]
            )
        chapter_list[0].content = re.sub('<img.*?/>',
                                         lambda match: _filter_duplicate_images(match, img_src_list),
                                         chapter_list[0].content)

    @staticmethod
    def _handle_select_volume(catalog_list: List[CatalogLinovelibVolume]) -> List[Any]:
        def _reduce_catalog_by_selection(catalog_list: List[CatalogLinovelibVolume], selection_array):
            return [volume for volume in catalog_list if volume.vid in selection_array]

        def _get_volume_choices(catalog_list: List[CatalogLinovelibVolume]):
            return [(volume.volume_title, volume.vid) for volume in catalog_list]

        # step 1: need to show UI for user to select one or more volumes,
        # step 2: then reduce the whole catalog_list to a reduced_catalog_list based on user selection
        # UI show
        question_name = 'Selecting volumes'
        question_description = "Which volumes you want to download?(use SPACE to select one or multiple volumes)"
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



class LinovelibSpiderMobile(BaseLinovelibSpider):

    def fetch(self):
        if not self._is_driver_initialized:
            warm_up_url = 'https://www.bilinovel.com/'
            self._init_drissionpage_driver(warm_up_url)

        book_url = f'{self.spider_settings["base_url"]}/novel/{self.spider_settings["book_id"]}.html'
        book_catalog_url = f'{self.spider_settings["base_url"]}/novel/{self.spider_settings["book_id"]}/catalog'
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
        novel_whole.book_id = self.spider_settings['book_id']
        novel_whole.book_title = book_title
        novel_whole.author = author
        novel_whole.description = book_summary
        novel_whole.book_cover = LightNovelImage(related_page_url=book_url,
                                                 remote_src=book_cover,
                                                 book_id=self.spider_settings["book_id"],
                                                 is_book_cover=True)
        novel_whole.mark_basic_info_ready()

        return novel_whole

    def _crawl_book_basic_info(self, url) -> Tuple | None:
        result = requests_get_with_retry(self._session,
                                         url,
                                         headers=self.request_headers(),
                                         retry_max=self.spider_settings['http_retries'],
                                         timeout=self.spider_settings["http_timeout"],
                                         logger=self.logger)

        if result and result.status_code == 200:
            self.logger.info(f'Succeed to get the novel of book_id: {self.spider_settings["book_id"]}')
            soup = BeautifulSoup(result.text, 'lxml')

            try:
                book_title = soup.find('h1', {'class': 'book-title'}).text
                author = soup.find('div', {'class': 'book-rand-a'}).text[:-2]
                book_summary = soup.find('section', id="bookSummary").text
                # see issue #10, strip invalid suffix characters after ? from cover url
                book_cover_url = soup.find('img', {'class': 'book-cover'})['src'].split("?")[0]

                self.logger.info(f'book name:《{book_title}》')
                return book_title, author, book_summary, book_cover_url
            except (Exception,):
                self.logger.error(f'Failed to parse basic info of book_id: {self.spider_settings["book_id"]}')

        return None

    def _crawl_book_content(self, catalog_url) -> Optional[LightNovel]:
        # 不要提取这类工具函数到上一层，因为 mobile 和 pc 的网页版本往往不一样，没法重用，不要过度设计。
        def _anti_js_obfuscation(html):
            """
            recover original text of the novel content.

            :param html:
            :return: html after anti-js obfuscation
            """
            table = str.maketrans(self._mapping_dict)
            res = html.translate(table)
            return res

        def _sanitize_html(html: PageElement) -> str:
            """
            Strip useless script on body tag by reg or soup library method.
            e.g. <script>zation();</script>

            And remove all the content not needed.

            :param html:
            :return:
            """
            html_copy = BeautifulSoup(str(html), 'lxml')

            # remove <p class="ca1"> 去掉一些公告声明
            anouncements = html_copy.select(".ca1")
            for anouncement in anouncements:
                anouncement.decompose()

            return re.sub(r'<script.+?</script>', '', str(html_copy), flags=re.DOTALL)

        def _require_not_empty_article(soup, page_link):
            article_soup = soup.find(id=self._html_content_id)
            if article_soup is None:
                hints = """
                                This can happen for the following reasons:
                                - The html structure of bilinovel website has changed. => You can submit a github issue to remind the maintainer.
                                - You are on a network outside of Chinese mainland, and want to request the traditional Chinese version of the website
                                 without specifying the target_site parameter. => Refer README document and set the target_site parameter.
                                """
                dedent_hints = textwrap.dedent(hints)
                self.logger.fatal(
                    f'The content of {page_link} is Empty and content_id ={self._html_content_id}.'
                    f'{dedent_hints}')

                raise EmptyArticleError()

        def _require_not_empty_title(soup: BeautifulSoup):
            new_title = soup.find(id='atitle')
            if new_title is None:
                raise EmptyTitleError()

            return new_title

        def _require_intact_text_content(soup: BeautifulSoup):
            article_page_element = soup.find(id=self._html_content_id)
            article_text = article_page_element.text
            error_keywords = [
                "內容加載失敗",
                "請重載",
                "更換瀏覽器",
                "相容性問題",
                "不支持電腦端閱讀",
                "請使用手機閱讀"
            ]

            threshold = 2
            error_count = sum(1 for keyword in error_keywords if keyword in article_text)
            if error_count >= threshold:
                raise NotIntactTextError()

            return article_page_element

        book_catalog_rs = None
        try:
            book_catalog_rs = self._fetch_catalog(catalog_url, max_retries=self.spider_settings['http_retries'])
        except (Exception,):
            self.logger.error(f'Failed to get normal response of {catalog_url}. It may be a network issue.')

        if book_catalog_rs:
            self.logger.info(f'Succeed to get the catalog of book_id: {self.spider_settings["book_id"]}')
            catalog_html = book_catalog_rs
            catalog_list: List[CatalogLinovelibVolume] = self._convert_to_catalog_list(catalog_html)
            if self.spider_settings['select_volume_mode']:
                catalog_list = self._handle_select_volume(catalog_list)

            new_novel = LightNovel()
            url_next = ''

            volume_id = -1
            for catalog_volume in catalog_list:
                volume_id += 1

                new_volume = LightNovelVolume(volume_id=volume_id)
                new_volume.title = catalog_volume.volume_title
                self.logger.info(f'volume: {catalog_volume.volume_title}')

                chapter_id = -1
                chapter_list: List[LightNovelChapter] = []  # store all chapters of one volume
                for catalog_chapter in catalog_volume.chapters:
                    self._apply_crawl_delay('chapter_crawl_delay')

                    chapter_content = ''
                    chapter_title = catalog_chapter.chapter_title
                    chapter_id += 1

                    light_novel_chapter = LightNovelChapter(chapter_id=chapter_id)
                    light_novel_chapter.title = chapter_title
                    chapter_illustrations: List[LightNovelImage] = []
                    self.logger.info(f'chapter : {chapter_title}')

                    # 这个函数是含有状态的，必须及时覆盖 url_next 变量，否则状态机会失败。
                    # 注意：由于这里并不关心页面内容是否正常，只收集页面链接，因此这里暂时不需要应用请求间隔延迟。
                    url_next = self._expand_paginated_chapter_links(catalog_chapter, url_next)
                    for page_link in catalog_chapter.chapter_urls:
                        self._apply_crawl_delay('page_crawl_delay')

                        soup = None
                        new_title = None
                        article_page_element = None
                        while True:
                            try:
                                page_resp = self._fetch_page(page_link,
                                                             max_retries=self.spider_settings['http_retries'])

                                page_resp = page_resp or ''
                                soup = BeautifulSoup(page_resp, 'lxml')

                                new_title = _require_not_empty_title(soup)
                                _require_not_empty_article(soup, page_link)
                                article_page_element = _require_intact_text_content(soup)

                                # happy path
                                break
                            except (EmptyTitleError, NotIntactTextError) as ex:
                                self.logger.error(f'url: {page_link}; {ex}')
                                continue
                            except EmptyArticleError as ex:
                                self.logger.error(f'url: {page_link}; {ex}; Exit eagerly.')
                                # very sad path
                                sys.exit(-1)
                            except (Exception,) as ex:
                                self.logger.error(f'url: {page_link}; {ex}')
                                continue

                        # 分页判断过滤
                        if not new_title.text.startswith(light_novel_chapter.title):
                            # 目录：第二章 可爱如花的 N 孩
                            # 文章页：第二章 可爱如花的女孩，第二章 可爱如花的女孩（2/3），......
                            # 目录页部分文字会被隐藏，所以用文章中的标题代替 new_title。由于 new_title 可能带有分页信息，所以不能 ==
                            self.logger.info(
                                f'chapter : [{light_novel_chapter.title}] New Title= [{new_title.text}]')
                            light_novel_chapter.title = new_title.text

                        images = soup.find_all('img')
                        article = _sanitize_html(article_page_element)
                        for _, image in enumerate(images):
                            # <img class="imagecontent lazyload" data-src="https://img1.readpai.com/0/28/109869/146248.jpg" src="/images/photon.svg"/>
                            # <img border="0" class="imagecontent" src="https://img1.readpai.com/0/28/109869/146254.jpg"/>
                            html_image_src = re.search('(?<= src=").*?(?=")', str(image))
                            image_lazyload_src = image.get("data-src")

                            if image_lazyload_src:
                                remote_src = re.search('(?<= data-src=").*?(?=")', str(image)).group()
                            else:
                                remote_src = image.get("src")

                            light_novel_image = LightNovelImage(related_page_url=page_link, remote_src=remote_src,
                                                                chapter_id=chapter_id, volume_id=volume_id,
                                                                book_id=self.spider_settings["book_id"])

                            image_local_src = f'{self.spider_settings["image_download_folder"]}/{light_novel_image.local_relative_path}'
                            local_image = str(image).replace(str(html_image_src.group()), image_local_src)
                            article = article.replace(str(image), local_image)
                            chapter_illustrations.append(light_novel_image)

                        article = _anti_js_obfuscation(article)
                        chapter_content += article

                        self.logger.info(f'Processing page... {page_link}')

                    light_novel_chapter.content = chapter_content
                    light_novel_chapter.illustrations = chapter_illustrations
                    chapter_list.append(light_novel_chapter)

                self._remove_duplicate_images_in_html(chapter_list)

                for chapter in chapter_list:
                    new_volume.add_chapter(cid=chapter.chapter_id, title=chapter.title, content=chapter.content,
                                           illustrations=chapter.illustrations)

                new_novel.add_volume(vid=new_volume.volume_id, title=new_volume.title, chapters=new_volume.chapters)

            return new_novel

        else:
            self.logger.error(f'Failed to get the catalog of book_id: {self.spider_settings["book_id"]}')

        return None

    def _convert_to_catalog_list(self, catalog_html) -> List[CatalogLinovelibVolume]:
        soup_catalog = BeautifulSoup(catalog_html, 'lxml')
        catalog_wrapper = soup_catalog.find('div', {'id': 'volumes'})
        catalog_volumes = catalog_wrapper.find_all('div', {'class': 'catalog-volume'})

        # catalog html structure:
        #     <div class="catalog-volume">
        #         <ul class="volume-chapters">
        #             <li class="chapter-bar chapter-li"><h3> 第一章『卡利娅·巴德尼克篇』</h3></li>
        #             <li class="volume-cover chapter-li">...</li>
        #             <li class="chapter-li jsChapter">
        #               <a href="/novel/3087/153701.html" class="chapter-li-a "><span class="chapter-index "> 作品相关 </span></a>
        #             </li>

        catalog_list: List[CatalogLinovelibVolume] = []

        _current_chapters: List[CatalogLinovelibChapter] = []
        _current_volume_title = ""
        _volume_index = 0

        for catalog_volume in catalog_volumes:
            volume_chapters = catalog_volume.find("ul", {'class': 'volume-chapters'})
            volume_chapter_items = volume_chapters.find_all('li')

            for volume_chapter_item in volume_chapter_items:
                # is volume name
                if volume_chapter_item.name == 'li' and 'chapter-bar' in volume_chapter_item['class']:
                    _volume_index += 1
                    _current_volume_title = volume_chapter_item.get_text()
                    _current_chapters: List[CatalogLinovelibChapter] = []
                    new_volume = CatalogLinovelibVolume(
                        vid=_volume_index,
                        volume_title=_current_volume_title,
                        chapters=_current_chapters
                    )
                    catalog_list.append(new_volume)
                # is normal chapter
                elif volume_chapter_item.name == 'li' and 'jsChapter' in volume_chapter_item['class']:
                    href = volume_chapter_item.find("a")["href"]
                    chapter_url = urljoin(f'{self.spider_settings["base_url"]}/novel', href)
                    new_chapter: CatalogLinovelibChapter = CatalogLinovelibChapter(
                        chapter_title=volume_chapter_item.get_text(),
                        chapter_url=chapter_url
                    )
                    _current_chapters.append(new_chapter)

        # sanitize catalog_list => remove volume that has empty chapters
        # https://w.linovelib.com/novel/3847/catalog
        # {'vid': 3, 'volume_title': ' 第四卷 ', 'chapters': []}
        catalog_list = [catalog_volume for catalog_volume in catalog_list if catalog_volume.chapters]
        return catalog_list

    def _expand_paginated_chapter_links(self, chapter: CatalogLinovelibChapter, url_next):
        # fix broken links in place(catalog_lis) if exits
        # - if chapter[1] is valid link, assign it to url_next
        # - if chapter[1] is not a valid link,e.g. "javascript:cid(0)" etc. use url_next
        if not self._is_valid_chapter_link(chapter.chapter_url):
            # now the url_next value is the correct link of of chapter[1].
            chapter.chapter_url = url_next
        else:
            url_next = chapter.chapter_url

        # goal: solve all page links of a certain chapter
        while True:
            resp = requests_get_with_retry(self._session, url_next,
                                           headers=self.request_headers(),
                                           retry_max=self.spider_settings['http_retries'],
                                           timeout=self.spider_settings["http_timeout"],
                                           logger=self.logger)
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')
            else:
                raise Exception(f'[ERROR]: request {url_next} failed.')

            first_script = soup.find("body", {"id": "aread"}).find("script")
            first_script_text = first_script.text
            # alternative: use split(':')[-1] to get read_params_text
            read_params_text = first_script_text[len('var ReadParams='):]
            read_params_json = demjson3.decode(read_params_text)
            url_next = urljoin(f'{self.spider_settings["base_url"]}/novel', read_params_json['url_next'])

            if '_' in url_next:
                chapter.add_expand_paginated_chapter_url(url_next)
            else:
                break

        return url_next


class LinovelibSpiderPC(BaseLinovelibSpider):

    def fetch(self):
        if not self._is_driver_initialized:
            warm_up_url = 'https://www.linovelib.com/'
            self._init_drissionpage_driver(warm_up_url)

        book_url = f'{self.spider_settings["base_url"]}/novel/{self.spider_settings["book_id"]}.html'
        book_catalog_url = f'{self.spider_settings["base_url"]}/novel/{self.spider_settings["book_id"]}/catalog'

        self._convert_page_language(book_url)
        create_folder_if_not_exists(self.spider_settings['pickle_temp_folder'])

        book_basic_info = self._crawl_book_basic_info(book_url)
        if not book_basic_info:
            raise LinovelibException(f'Fetch book_basic_info of {self.spider_settings["book_id"]} failed.')

        # do better: use named tuple or class like NovelBasicInfoGroup
        book_title, author, book_summary, book_cover = book_basic_info
        # print(book_title, author, book_summary, book_cover)

        new_novel_with_content = self._crawl_book_content(book_catalog_url)
        if not new_novel_with_content:
            raise LinovelibException(f'Fetch book_content of {self.spider_settings["book_id"]} failed.')

        novel_whole = new_novel_with_content
        novel_whole.mark_volumes_content_ready()

        # set book basic info
        novel_whole.book_id = self.spider_settings['book_id']
        novel_whole.book_title = book_title
        novel_whole.author = author
        novel_whole.description = book_summary
        novel_whole.book_cover = LightNovelImage(related_page_url=book_url,
                                                 remote_src=book_cover,
                                                 book_id=self.spider_settings["book_id"],
                                                 is_book_cover=True)
        novel_whole.mark_basic_info_ready()

        return novel_whole

    def _crawl_book_basic_info(self, url) -> Tuple | None:
        result = requests_get_with_retry(self._session,
                                         url,
                                         headers=self.request_headers(),
                                         retry_max=self.spider_settings['http_retries'],
                                         timeout=self.spider_settings["http_timeout"],
                                         logger=self.logger)

        if result and result.status_code == 200:
            self.logger.info(f'Succeed to get the novel of book_id: {self.spider_settings["book_id"]}')
            soup = BeautifulSoup(result.text, 'lxml')

            try:
                book_title = soup.find('h1', {'class': 'book-name'}).text
                author = soup.find('div', {'class': 'au-name'}).text.strip()
                book_summary = soup.find('div', {'class': 'book-dec'}).find('p').text
                # see issue #10, strip invalid suffix characters after ? from cover url
                book_cover_url = soup.find('div', {'class': 'book-img'}).find('img')['src'].split("?")[0]

                self.logger.info(f'book name:《{book_title}》')
                return book_title, author, book_summary, book_cover_url
            except (Exception,):
                self.logger.error(f'Failed to parse basic info of book_id: {self.spider_settings["book_id"]}')

        return None

    def _crawl_book_content(self, catalog_url):
        def _anti_js_obfuscation(html):
            """
            recover original text of the novel content.

            :param html:
            :return: html after anti-js obfuscation
            """
            # see https://github.com/lightnovel-center/linovelib2epub/issues/46#issuecomment-2080431115
            # take https://www.linovelib.com/novel/2356/83546_2.html as a case to analyze
            table = str.maketrans(self._mapping_dict)
            res = html.translate(table)
            return res

        def _sanitize_html(html: BeautifulSoup) -> str:
            """
            Strip useless script on body tag by reg or soup library method.
            e.g. <div class="dag">...</div>

            And remove all the content not needed.

            :param html:
            :return:
            """
            html_copy = BeautifulSoup(str(html), 'lxml')

            # remove <div class="dag">...</div>
            anouncements = html_copy.select("div.dag")
            for anouncement in anouncements:
                anouncement.decompose()

            res = re.sub(r'<script.+?</script>', '', str(html_copy), flags=re.DOTALL)
            return res

        book_catalog_rs = None
        try:
            book_catalog_rs = self._fetch_catalog(catalog_url, max_retries=self.spider_settings['http_retries'])
        except (Exception,):
            self.logger.error(f'Failed to get normal response of {catalog_url}. It may be a network issue.')

        if book_catalog_rs:
            self.logger.info(f'Succeed to get the catalog of book_id: {self.spider_settings["book_id"]}')

            catalog_html = book_catalog_rs
            catalog_list: List[CatalogLinovelibVolume] = self._convert_to_catalog_list(catalog_html)
            if self.spider_settings['select_volume_mode']:
                catalog_list = self._handle_select_volume(catalog_list)

            new_novel = LightNovel()
            url_next = ''

            volume_id = -1
            for catalog_volume in catalog_list:
                volume_id += 1

                new_volume = LightNovelVolume(volume_id=volume_id)
                new_volume.title = catalog_volume.volume_title
                new_volume.explicit_volume_cover = catalog_volume.volume_cover
                self.logger.info(f'volume: {catalog_volume.volume_title}')

                chapter_id = -1
                chapter_list: List[LightNovelChapter] = []  # store all chapters of one volume
                for catalog_chapter in catalog_volume.chapters:
                    self._apply_crawl_delay('chapter_crawl_delay')

                    chapter_content = ''
                    chapter_title = catalog_chapter.chapter_title
                    chapter_id += 1

                    light_novel_chapter = LightNovelChapter(chapter_id=chapter_id)
                    light_novel_chapter.title = chapter_title
                    chapter_illustrations: List[LightNovelImage] = []
                    self.logger.info(f'chapter : {chapter_title}')

                    # 这个函数是含有状态的，必须及时覆盖 url_next 变量，否则状态机会失败。
                    # 注意：由于这里并不关心页面内容是否正常，只收集页面链接，因此这里暂时不需要应用请求间隔延迟。
                    url_next = self._expand_paginated_chapter_links(catalog_chapter, url_next)

                    # for loop [chapter_index_url]+[all paginated chapters] links of one chapter
                    for page_link in catalog_chapter.chapter_urls:
                        self._apply_crawl_delay('page_crawl_delay')

                        while True:
                            try:
                                html_resp = self._fetch_page(page_link,
                                                             max_retries=self.spider_settings['http_retries'])
                            except (Exception,):
                                continue

                            # # double check if the title exists
                            html_resp = html_resp or ''
                            soup = BeautifulSoup(html_resp, 'lxml')
                            main_text = soup.find(id='mlfy_main_text')
                            if main_text and main_text.select_one('h1') and main_text.select_one('#TextContent'):
                                new_title = main_text.select_one('h1').text
                                self.logger.debug(f'page({page_link}) size={len(html_resp)}')
                                break

                        # 分页判断过滤
                        if not new_title.startswith(light_novel_chapter.title):
                            # 目录：第二章 可爱如花的 N 孩
                            # 文章页：第二章 可爱如花的女孩，第二章 可爱如花的女孩（2/3），......
                            # 目录页部分文字会被隐藏，所以用文章中的标题代替 new_title。由于 new_title 可能带有分页信息，所以不能 ==
                            self.logger.info(f'chapter : [{light_novel_chapter.title}] New Title= [{new_title}]')
                            light_novel_chapter.title = new_title

                        images = soup.find_all('img')
                        article_soup = soup.find(id=self._html_content_id)
                        if not article_soup:
                            hints = """
                                This can happen for the following reasons:
                                - The html structure of bilinovel website has changed. => You can submit a github issue to remind the maintainer.
                                - You are on a network outside of Chinese mainland, and want to request the traditional Chinese version of the website
                                 without specifying the target_site parameter. => Refer README document and set the target_site parameter.
                                """
                            dedent_hints = textwrap.dedent(hints)
                            self.logger.fatal(
                                f'The content of {page_link} is Empty and content_id ={self._html_content_id}.'
                                f'{dedent_hints}')
                            sys.exit(1)

                        article = _sanitize_html(article_soup)
                        for _, image in enumerate(images):
                            # <img class="imagecontent lazyload" data-src="https://img1.readpai.com/0/28/109869/146248.jpg" src="/images/photon.svg"/>
                            # <img border="0" class="imagecontent" src="https://img1.readpai.com/0/28/109869/146254.jpg"/>
                            html_image_src = re.search('(?<= src=").*?(?=")', str(image))
                            image_lazyload_src = image.get("data-src")

                            if image_lazyload_src:
                                remote_src = re.search('(?<= data-src=").*?(?=")', str(image)).group()
                            else:
                                remote_src = image.get("src")

                            light_novel_image = LightNovelImage(related_page_url=page_link, remote_src=remote_src,
                                                                chapter_id=chapter_id, volume_id=volume_id,
                                                                book_id=self.spider_settings["book_id"])

                            image_local_src = f'{self.spider_settings["image_download_folder"]}/{light_novel_image.local_relative_path}'
                            local_image = str(image).replace(str(html_image_src.group()), image_local_src)
                            article = article.replace(str(image), local_image)
                            chapter_illustrations.append(light_novel_image)

                        article = _anti_js_obfuscation(article)
                        chapter_content += article

                        self.logger.info(f'Processing page... {page_link}')

                    light_novel_chapter.content = chapter_content
                    light_novel_chapter.illustrations = chapter_illustrations
                    chapter_list.append(light_novel_chapter)

                self._remove_duplicate_images_in_html(chapter_list)

                for chapter in chapter_list:
                    new_volume.add_chapter(cid=chapter.chapter_id, title=chapter.title, content=chapter.content,
                                           illustrations=chapter.illustrations)

                new_novel.add_volume(vid=new_volume.volume_id, title=new_volume.title, chapters=new_volume.chapters)

            return new_novel

        else:
            self.logger.error(f'Failed to get the catalog of book_id: {self.spider_settings["book_id"]}')

        return None

    def _convert_to_catalog_list(self, catalog_html) -> List[CatalogLinovelibVolume]:
        soup = BeautifulSoup(catalog_html, 'lxml')
        volume_list_div = soup.select_one('#volume-list')
        volumes = volume_list_div.select('.volume')

        catalog_list: List[CatalogLinovelibVolume] = []

        for idx, item in enumerate(volumes):
            # 这里可以获取到明确的封面，应该明确写入对应 CatalogXXXVolume 的 cover 属性
            cover_src = item.select_one('a.volume-cover > img').get('src')
            volume_title = item.select_one('.volume-info > .v-line').text
            chapters = item.select_one('.chapter-list').select('li a')

            _current_chapters: List[CatalogLinovelibChapter] = []
            new_volume = CatalogLinovelibVolume(
                vid=idx + 1,
                volume_title=volume_title,
                chapters=_current_chapters,
                volume_cover=cover_src
            )
            catalog_list.append(new_volume)
            for chapter in chapters:
                chapter_href = chapter.get('href')
                chapter_title = chapter.text
                chapter_url = urljoin(f'{self.spider_settings["base_url"]}/novel', chapter_href)
                new_chapter: CatalogLinovelibChapter = CatalogLinovelibChapter(
                    chapter_title=chapter_title,
                    chapter_url=chapter_url
                )
                _current_chapters.append(new_chapter)

        # filter None chapter
        catalog_list = [catalog_volume for catalog_volume in catalog_list if catalog_volume.chapters]
        return catalog_list

    def _expand_paginated_chapter_links(self, chapter: CatalogLinovelibChapter, url_next):
        if not self._is_valid_chapter_link(chapter.chapter_url):
            chapter.chapter_url = url_next
        else:
            url_next = chapter.chapter_url

        # goal: solve all page links of a certain chapter
        while True:
            resp = requests_get_with_retry(self._session, url_next,
                                           headers=self.request_headers(),
                                           retry_max=self.spider_settings['http_retries'],
                                           timeout=self.spider_settings["http_timeout"],
                                           logger=self.logger)
            if resp:
                soup = BeautifulSoup(resp.text, 'lxml')
            else:
                raise Exception(f'[ERROR]: request {url_next} failed.')

            paging = soup.select_one('.mlfy_page')
            links = paging.select('a')
            links_has_href = [link for link in links if link.has_attr('href')]
            url_next_href = links_has_href[-1].get('href')
            url_next = urljoin(f'{self.spider_settings["base_url"]}/novel', url_next_href)

            if '_' in url_next:
                chapter.add_expand_paginated_chapter_url(url_next)
            else:
                break

        return url_next

    def _convert_page_language(self, book_url):
        page = self._driver
        page.get(book_url)
        translate_btn = page.ele('#GB_BIG')
        # 显示【繁體化】，则当前页面是简体文本
        # 显示【简体化】，则当前页面是繁体文本
        current_text = translate_btn.text

        # 定义繁为 True，简为 False
        # 一共四种可能：
        # 1 当前简体 (0)，请求简体 (0) => 跳过
        # 2 当前繁体 (1)，请求繁体 (1) => 跳过
        # 3 当前简体 (0)，请求繁体 (1) => 点击转化
        # 4 当前繁体 (1)，请求简体 (0) => 点击转化
        # 使用 XOR（异或操作）即可简化处理, 仅当 xor=1 时进行转化

        current_lang = True if '简体'.strip() in current_text else False
        require_lang = self.spider_settings['traditional']
        current_lang_repr = "繁体".strip() if current_lang else "简体".strip()
        require_lang_repr = "繁体".strip() if require_lang else "简体".strip()
        self.logger.info(f'[LANGUAGE]current_lang={current_lang_repr},require_lang={require_lang_repr}.')

        xor_result = require_lang ^ current_lang
        if xor_result:
            result = translate_btn.click()
            # do better: wait util see expected language text flag before leaving.
            self.logger.info(f'[LANGUAGE]Execute conversion: {current_lang_repr} => {require_lang_repr}.')
        else:
            self.logger.info(f'[LANGUAGE]No conversion is required: {current_lang_repr} => {require_lang_repr}.')

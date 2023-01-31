import io
import os
import re
import shutil
# from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool
from pathlib import Path
from typing import List, Optional, Union, Dict
from urllib.parse import urljoin

import demjson3
import requests
import uuid
from PIL import Image
from bs4 import BeautifulSoup
from ebooklib import epub
from linovelib2epub.utils import cookiedict_from_str, random_useragent, create_folder_if_not_exists, \
    request_with_retry, is_valid_image_url, check_image_integrity
from requests.exceptions import ProxyError
from rich.prompt import Confirm


class LightNovelChapter:
    def __init__(self,
                 cid: Optional[Union[int, str]] = None,
                 title: str = '',
                 url: str = '',
                 content: str = '') -> None:
        self.cid = cid
        self.title = title
        self.url = url
        self.content = content


class LightNovelVolume:
    def __init__(self,
                 vid: Optional[Union[int, str]] = None,
                 title: str = '',
                 chapters: Optional[List[LightNovelChapter]] = None) -> None:
        self.vid = vid
        self.title = title
        self.chapters = []

    def add_chapter(self, chapter: LightNovelChapter) -> None:
        self.chapters.append(chapter)
        return chapter

    def add_chapter(self, cid: Optional[Union[int, str]], title: str = '', url: str = '', content: str = ''):
        chapter = LightNovelChapter()
        chapter.cid = cid
        chapter.title = title
        chapter.content = content
        self.chapters.append(chapter)
        return chapter


class LightNovel:
    bid: Optional[Union[int, str]] = None
    book_title: str = ''
    author: str = ''
    description: str = ''
    book_cover: str = ''

    volumes: Optional[List[LightNovelVolume]] = None

    # map<volume_name, List[img_url]>
    image_dict: Optional[Dict[str, List[str]]] = None

    def __init__(self) -> None:
        self.volumes = []
        self.image_dict = {}

        # data states
        self.basic_info_ready = False
        self.volumes_content_ready = False

    def get_volumes_size(self):
        return len(self.volumes)

    def get_chapters_size(self):
        return sum([len(volume.chapters) for volume in self.volumes if volume.chapters])

    def get_image_set(self):
        image_set = set()
        for values in self.image_dict.values():
            for value in values:
                image_set.add(value)
        return image_set

    def add_volume(self, volume: LightNovelVolume):
        self.volumes.append(volume)
        return volume

    def add_volume(self, vid: Optional[Union[int, str]], title: str = '', chapters: LightNovelChapter = None):
        new_volume = LightNovelVolume()
        new_volume.vid = vid
        new_volume.title = title
        new_volume.chapters = chapters
        self.volumes.append(new_volume)
        return new_volume

    def get_volume(self, vid):
        for volume in self.volumes:
            if volume.vid == vid:
                return volume
        return None

    def set_image_dict(self, image_dict: Dict[str, List[str]] = {}):
        self.image_dict = image_dict

    def mark_basic_info_ready(self):
        self.basic_info_ready = True

    def mark_volumes_content_ready(self):
        self.volumes_content_ready = True


from abc import ABC, abstractmethod


class BaseNovelWebsiteSpider(ABC):

    def __init__(self, spider_settings: Optional[Dict] = None):
        self.spider_settings = spider_settings

    @abstractmethod
    def fetch(self) -> LightNovel:
        raise NotImplementedError()


class LinovelibSpider(BaseNovelWebsiteSpider):

    def __init__(self,
                 spider_setting: Optional[Dict] = None):
        super().__init__(spider_setting)
        self._init_http_client()

    def dump_settings(self):
        print(self.spider_settings)

    def _init_http_client(self):
        self.session = requests.Session()

        if self.spider_settings["disable_proxy"]:
            self.session.trust_env = False

        # cookie example: PHPSESSID=...; night=0; jieqiUserInfo=...; jieqiVisitInfo=...
        if self.spider_settings["http_cookie"]:
            cookie_dict = cookiedict_from_str(self.spider_settings["http_cookie"])
            cookiejar = requests.utils.cookiejar_from_dict(cookie_dict)
            self.session.cookies = cookiejar

    def _request_headers(self, referer: str = '', random_ua: bool = True):
        """
            :authority: w.linovelib.com
            :method: GET
            :path: /
            :scheme: https
            accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
            accept-encoding: gzip, deflate, br
            accept-language: en,zh-CN;q=0.9,zh;q=0.8
            cache-control: max-age=0
            cookie: night=0
            referer: https://www.google.com/
            sec-ch-ua: "Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"
            sec-ch-ua-mobile: ?0
            sec-ch-ua-platform: "Windows"
            sec-fetch-dest: document
            sec-fetch-mode: navigate
            sec-fetch-site: cross-site
            sec-fetch-user: ?1
            upgrade-insecure-requests: 1
            user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36
        """
        default_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
        default_referer = 'https://w.linovelib.com'
        headers = {
            # ! don't set any accept fields
            'referer': referer if referer else default_referer,
            'user-agent': self.spider_settings['random_useragent'] if random_ua else default_ua
        }
        return headers

    def _crawl_book_basic_info(self, url):
        result = request_with_retry(self.session,
                                    url,
                                    headers=self._request_headers(),
                                    retry_max=self.spider_settings['http_retries'],
                                    timeout=self.spider_settings["http_timeout"])

        if result and result.status_code == 200:
            print(f'Succeed to get the novel of book_id: {self.spider_settings["book_id"]}')

            # pass html text to beautiful soup parser
            soup = BeautifulSoup(result.text, 'lxml')
            try:
                book_title = soup.find('h2', {'class': 'book-title'}).text
                author = soup.find('div', {'class': 'book-rand-a'}).text[:-2]
                book_summary = soup.find('section', id="bookSummary").text
                book_cover_url = soup.find('img', {'class': 'book-cover'})['src']
                return book_title, author, book_summary, book_cover_url

            except (Exception,):
                print(f'Failed to parse basic info of book_id: {self.spider_settings["book_id"]}')

        return None

    def _crawl_book_content(self, catalog_url):
        book_catalog_rs = None
        try:
            book_catalog_rs = request_with_retry(self.session,
                                                 catalog_url,
                                                 headers=self._request_headers(),
                                                 retry_max=self.spider_settings['http_retries'],
                                                 timeout=self.spider_settings["http_timeout"]
                                                 )
        except (Exception,):
            print(f'Failed to get normal response of {catalog_url}. It may be a network issue.')

        if book_catalog_rs and book_catalog_rs.status_code == 200:
            print(f'Succeed to get the catalog of book_id: {self.spider_settings["book_id"]}')

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
            # ...
            # we should convert it to a dict: (key, value).
            # key is chapter_name, value is a two-dimensional array
            # Every array element is also an array which includes only two element.
            # format: ['插图','/novel/682/117077.html'], [’「彩虹与夜色的交会──远在起始之前──」‘,'/novel/682/32683.html']
            # So, the whole dict will be like this format:
            # (’第一卷 夏娃在黎明时微笑‘,[['插图','/novel/2211/116045.html'], [’「彩虹与夜色的交会──远在起始之前──」‘,'/novel/682/32683.html'],...])
            # (’第二卷 咏唱少女将往何方‘,[...])

            catalog_dict = self._convert_to_catalog_dict(catalog_lis)

            new_novel = LightNovel()
            image_dict: Dict[str, List[str]] = dict()
            url_next = ''

            volume_id = 0
            for volume in catalog_dict:
                volume_id += 1

                new_volume = LightNovelVolume()
                new_volume.vid = volume_id
                new_volume.title = volume

                print(f'volume: {volume}')
                image_dict.setdefault(volume, [])

                chapter_id = -1
                for chapter in catalog_dict[volume]:
                    chapter_content = ''
                    chapter_title = chapter[0]
                    chapter_id += 1
                    # print(f'chapter_id: {chapter_id}')

                    new_chapter = LightNovelChapter()
                    new_chapter.cid = chapter_id
                    new_chapter.title = chapter_title
                    # new_chapter.content = 'UNSOLVED'

                    print(f'chapter : {chapter_title}')

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
                        resp = request_with_retry(self.session, url_next)
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
                                                       timeout=self.spider_settings["http_timeout"])
                        if page_resp:
                            soup = BeautifulSoup(page_resp.text, 'lxml')
                        else:
                            raise Exception(f'[ERROR]: request {page_link} failed.')

                        images = soup.find_all('img')
                        article = str(soup.find(id="acontent"))

                        for _, image in enumerate(images):
                            # img tag format: <img src="https://img.linovelib.com/0/682/117078/50677.jpg" border="0" class="imagecontent">
                            # here we convert its path `0/682/117078/50677.jpg` to `0-682-117078-50677.jpg` as filename.
                            image_src = image['src']
                            image_dict[volume].append(image_src)

                            # example: https://img.linovelib.com/0/682/117077/50675.jpg => [folder]/0-682-117078-50677.jpg

                            src_value = re.search(r"(?<=src=\").*?(?=\")", str(image))
                            replace_value = f'{self.spider_settings["image_download_folder"]}/' + "-".join(
                                src_value.group().split("/")[-4:])
                            # replace all remote images src to local file path
                            article = article.replace(str(src_value.group()), str(replace_value))

                        article = self._sanitize_html(article)
                        chapter_content += article

                        print(f'Processing page... {page_link}')

                    # Here, current chapter's content has been solved
                    new_chapter.content = chapter_content
                    new_volume.add_chapter(new_chapter)

                new_novel.add_volume(new_volume)

            new_novel.set_image_dict(image_dict)

            return new_novel

        else:
            print(f'Failed to get the catalog of book_id: {self.spider_settings["book_id"]}')

        return None

    @staticmethod
    def _sanitize_html(html):
        """
        strip useless script on body tag by reg or soup method.

        e.g. <script>zation();</script>

        :param html:
        :return:
        """
        return re.sub(r'<script.+?</script>', '', html, flags=re.DOTALL)

    def _convert_to_catalog_dict(self, catalog_lis):
        catalog_lis_tmp = catalog_lis

        catalog_dict = dict()
        current_volume = []
        current_volume_text = catalog_lis_tmp[0].text

        for index, catalog_li in enumerate(catalog_lis_tmp):
            catalog_li_text = catalog_li.text
            # is volume name
            if 'chapter-bar' in catalog_li['class']:
                # reset current_* variables
                current_volume_text = catalog_li_text
                current_volume = []
                catalog_dict[current_volume_text] = current_volume
            # is normal chapter
            else:
                href = catalog_li.find("a")["href"]
                whole_url = urljoin(self.spider_settings['base_url'], href)
                current_volume.append([catalog_li_text, whole_url])

        return catalog_dict

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

    def _parse_img_filename_from(self, url):
        return '-'.join(url.split("/")[-4:])

    def fetch(self) -> LightNovel:
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
        novel_whole.mark_basic_info_ready()

        self._post_fecth(novel_whole)

        return novel_whole

    def _post_fecth(self, novel: LightNovel):
        with open(self.spider_settings['novel_pickle_path'], 'wb') as fp:
            pickle.dump(novel, fp)

    def download_images(self, urls=None, pool_size=os.cpu_count()):
        if urls is None:
            urls = []
        print(f'len(image_list) = {len(urls)}')
        urls_set = set(urls)
        print(f'len(image_set) = {len(urls_set)}')

        process_pool = Pool(processes=int(pool_size))
        error_links = process_pool.map(self.download_image, urls_set)
        # if everything is perfect, error_links array will be []
        # if some error occurred, error_links will be those links that failed to request.

        # remove None element from array, only retain error link
        # >>> sorted_error_links := sorted(list(filter(None, error_links)))

        # for loop until all files are downloaded successfully.
        while sorted_error_links := sorted(list(filter(None, error_links))):
            print('Some errors occurred when download images. Retry those links that failed to request.')
            print(f'Error image links size: {len(sorted_error_links)}')
            print(f'Error image links: {sorted_error_links}')

            # multi-process
            error_links = process_pool.map(self.download_image, sorted_error_links)

        # re-check image download result: the number of imgaes downloaded == len(urls_set)
        # - happy result: urls_set - self.image_download_folder == 0
        # - bad result: urls_set - self.image_download_folder > 0
        # downloading image: https://img.linovelib.com/0/682/117082/50748.jpg
        # Image images/0-682-117082-50748.jpg Saved.
        download_image_recheck = len(urls_set) - len(os.listdir(self.spider_settings['image_download_folder']))
        print(f'download_image_recheck: {download_image_recheck}')
        if download_image_recheck == 0:
            print('The result of downloading pictures is perfect.')
        else:
            print('Some pictures to download are missing. Maybe this is a bug. You can Retry.')

    def download_image(self, url: str):
        """
        If a image url download failed, return its url. else return None.

        :param url: single url string
        :return:
        """
        if not is_valid_image_url(url):
            return

        # if url is not desired format, return
        try:
            # filename parse rule depends on the specific website
            # website -> img filepath format -> parse rule
            # use open/close principle to refactor/manage this change
            filename = self._parse_img_filename_from(url)
        except (Exception,):
            return

        save_path = f"{self.spider_settings['image_download_folder']}/{filename}"

        # the file already exists, return
        filename_exists = Path(save_path)
        if filename_exists.exists():
            return

        # url is valid and never downloaded
        try:
            print(f"downloading image: {url}")
            resp = self.session.get(url, headers=self._request_headers(), timeout=self.spider_settings['http_timeout'])
            check_image_integrity(resp)
        except (Exception, ProxyError,) as e:
            print(f'Error occurred when download image of {url}. Error: {e}')
            return url
        else:
            try:
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                print(f'Image {save_path} Saved.')
            except (Exception,):
                print(f'Image {save_path} Save failed. Rollback {url} for next try.')
                return url


class EpubWriter:

    def __init__(self, epub_settings) -> None:
        self.epub_settings = epub_settings

    def prepare(self, book_basic_info, content_dict, image_dict, has_illustration=True, divide_volume=False):
        print(f'[Config]: has_illustration: {has_illustration}; divide_volume: {divide_volume}')

        book_title, author, book_summary, book_cover = book_basic_info
        cover_file = self.image_download_folder + '/' + '-'.join(book_cover.split('/')[-4:])

        # divide_volume(2) x download_image(2) = 4 choices
        if has_illustration:
            # handle all image stuff
            create_folder_if_not_exists(self.image_download_folder)
            image_list = self._extract_image_list(image_dict)
            image_list.append(book_cover)
            self._download_images(image_list)

            if not divide_volume:
                self._write_epub(book_title, author, content_dict, 'cover', cover_file, self.image_download_folder,
                                 has_illustration=True, divide_volume=False)
            else:
                self._create_folder_if_not_exists(f'{book_title}')
                for volume in content_dict:
                    self._write_epub(f'{book_title}_{volume}', author, content_dict[volume], 'cover', cover_file,
                                     self.image_download_folder, book_title, has_illustration=True, divide_volume=True)

        if not has_illustration:
            self._create_folder_if_not_exists(self.image_download_folder)
            # download only book_cover
            self._download_images([book_cover])

            if not divide_volume:
                self._write_epub(book_title, author, content_dict, 'cover', cover_file, self.image_download_folder,
                                 divide_volume=False, has_illustration=False)
            else:
                self._create_folder_if_not_exists(f'{book_title}')
                for volume in content_dict:
                    self._write_epub(f'{book_title}_{volume}', author, content_dict[volume], 'cover', cover_file,
                                     self.image_download_folder, book_title, divide_volume=True, has_illustration=False)

    def write(self, title, author, content, cover_filename, cover_file, images_folder, output_folder=None,
              divide_volume=False, has_illustration=True):
        book = epub.EpubBook()
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(title)
        book.set_language('zh')
        book.add_author(author)
        cover_type = cover_file.split('.')[-1]
        book.set_cover(cover_filename + '.' + cover_type, open(cover_file, 'rb').read())
        write_content = ""
        book.spine = ["nav", ]
        # TODO: now chapter will be from 0 to ...
        # better: reset count increment in every volume.
        chapter_id = -1
        file_index = -1

        # default chapter style
        style_chapter = self._read_pkg_resource('./styles/chapter.css')
        default_style_chapter = epub.EpubItem(uid="style_chapter", file_name="styles/chapter.css",
                                              media_type="text/css", content=style_chapter)

        # custom chapter style
        if self.custom_style_chapter:
            custom_style_chapter = epub.EpubItem(uid="style_chapter_custom", file_name="styles/chapter_custom.css",
                                                 media_type="text/css", content=self.custom_style_chapter)
        else:
            custom_style_chapter = None

        if not divide_volume:
            for volume in content:
                print("volume: " + volume)
                volume_title = "<h1>" + volume + "</h1>"
                write_content += volume_title
                book.toc.append([epub.Section(volume), []])
                chapter_id += 1

                for chapter in content[volume]:
                    print("chapter: " + chapter[0])
                    file_index += 1
                    page = epub.EpubHtml(title=chapter[0], file_name=f"{file_index}.xhtml", lang="zh")
                    chapter_title = "<h2>" + chapter[0] + "</h2>"
                    write_content += chapter_title + str(chapter[1]).replace("<div class=\"acontent\" id=\"acontent\">",
                                                                             "")
                    write_content = write_content.replace('png', 'jpg')
                    page.set_content(write_content)
                    # add `<link>` tag to page `<head>` section.
                    page.add_item(default_style_chapter)
                    if custom_style_chapter:
                        page.add_item(custom_style_chapter)
                    book.add_item(page)

                    # refer ebooklib docs
                    book.toc[chapter_id][1].append(page)
                    book.spine.append(page)

                    write_content = ""
        else:
            print("volume: " + title)
            volume_title = "<h1>" + title + "</h1>"
            write_content += volume_title
            book.toc.append([epub.Section(title), []])
            chapter_id += 1

            for chapter in content:
                print("chapter: " + chapter[0])
                file_index += 1
                page = epub.EpubHtml(title=chapter[0], file_name=f"{file_index}.xhtml", lang="zh")
                chapter_title = "<h2>" + chapter[0] + "</h2>"
                write_content += chapter_title + str(chapter[1]).replace("<div class=\"acontent\" id=\"acontent\">", "")
                write_content = write_content.replace('png', 'jpg')
                page.set_content(write_content)
                # add `<link>` tag to page `<head>` section.
                page.add_item(default_style_chapter)
                if custom_style_chapter:
                    page.add_item(custom_style_chapter)
                book.add_item(page)
                book.toc[chapter_id][1].append(page)
                book.spine.append(page)
                write_content = ""

        # book instance save chpater files only once.
        book.add_item(default_style_chapter)
        if custom_style_chapter:
            book.add_item(custom_style_chapter)

        print('Now book_content(text) is ready.')

        if has_illustration:
            image_files = os.listdir(images_folder)
            for image_file in image_files:
                if not ((".jpg" or ".png" or ".webp" or ".jpeg" or ".bmp" or "gif") in str(image_file)):
                    continue

                try:
                    img = Image.open(images_folder + '/' + image_file)
                except (Exception,):
                    continue

                b = io.BytesIO()
                img = img.convert('RGB')
                img.save(b, 'jpeg')
                data_img = b.getvalue()

                new_image_file = image_file.replace('png', 'jpg')
                img = epub.EpubItem(file_name=f"{self.image_download_folder}/%s" % new_image_file,
                                    media_type="image/jpeg",
                                    content=data_img)
                book.add_item(img)

            print('Now all images in book_content are ready.')

        if output_folder is None:
            folder = ''
        else:
            self._create_folder_if_not_exists(output_folder)
            folder = str(output_folder) + '/'

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        cover_html = book.get_item_with_id('cover')

        # default cover style
        default_style_cover_content = self._read_pkg_resource('./styles/cover.css')
        default_style_cover = epub.EpubItem(uid="style_cover", file_name="styles/cover.css", media_type="text/css",
                                            content=default_style_cover_content)
        cover_html.add_item(default_style_cover)
        book.add_item(default_style_cover)

        # custom cover style
        if self.custom_style_cover:
            custom_style_cover = epub.EpubItem(uid="style_cover_custom", file_name="styles/cover_custom.css",
                                               media_type="text/css",
                                               content=self.custom_style_cover)
            cover_html.add_item(custom_style_cover)
            book.add_item(custom_style_cover)

        nav_html = book.get_item_with_id('nav')

        # default nav style
        default_style_nav_content = self._read_pkg_resource('./styles/nav.css')
        default_style_nav = epub.EpubItem(uid="style_nav", file_name="styles/nav.css",
                                          media_type="text/css", content=default_style_nav_content)
        nav_html.add_item(default_style_nav)
        book.add_item(default_style_nav)

        if self.custom_style_nav:
            custom_style_nav = epub.EpubItem(uid="style_nav_custom", file_name="styles/nav_custom.css",
                                             media_type="text/css", content=self.custom_style_nav)
            nav_html.add_item(custom_style_nav)
            book.add_item(custom_style_nav)

        epub.write_epub(self._sanitize_partial_pathname(folder) + self._sanitize_partial_pathname(title) + '.epub',
                        book)


from . import settings

from .exceptions import LinovelibException

import pickle


class Linovelib2Epub():

    def __init__(self,
                 book_id: Optional[Union[int, str]] = None,
                 base_url: str = settings.BASE_URL,
                 divide_volume: bool = settings.DIVIDE_VOLUME,
                 has_illustration: bool = settings.HAS_ILLUSTRATION,
                 image_download_folder: str = settings.IMAGE_DOWNLOAD_FOLDER,
                 pickle_temp_folder: str = settings.PICKLE_TEMP_FOLDER,
                 clean_artifacts: bool = settings.CLEAN_ARTIFACTS,
                 http_timeout: int = settings.HTTP_TIMEOUT,
                 http_retries: int = settings.HTTP_RETRIES,
                 http_cookie: str = settings.HTTP_COOKIE,
                 disable_proxy: bool = settings.DISABLE_PROXY,
                 custom_style_cover: str = None,
                 custom_style_nav: str = None,
                 custom_style_chapter: str = None):

        if book_id is None:
            raise LinovelibException('book_id parameter must be set.')
        if base_url is None:
            raise LinovelibException('base_url parameter must be set.')

        self.common_settings = {
            'book_id': book_id,
            'base_url': base_url,
            'divide_volume': divide_volume,
            'has_illustration': has_illustration,
            'image_download_folder': image_download_folder,
            'pickle_temp_folder': pickle_temp_folder,
            'novel_pickle_path': f'{pickle_temp_folder}/{book_id}_novel.pickle',
            'clean_artifacts': clean_artifacts
        }

        self.spider_settings = {
            **self.common_settings,
            'http_timeout': http_timeout,
            'http_retries': http_retries,
            'random_useragent': random_useragent(),
            'http_cookie': http_cookie,
            'disable_proxy': disable_proxy
        }
        self._spider = LinovelibSpider(spider_setting=self.spider_settings)

        self.epub_settings = {
            **self.common_settings,
            'custom_style_cover': custom_style_cover,
            'custom_style_nav': custom_style_nav,
            'custom_style_chapter': custom_style_chapter
        }
        self._epub_writer = EpubWriter(epub_settings=self.epub_settings)

    def run(self):
        # recover from last work.
        novel_pickle_path = Path(self.common_settings['novel_pickle_path'])
        if novel_pickle_path.exists():
            if Confirm.ask("The last unfinished work was detected, continue with your last job?"):
                with open(self.common_settings['novel_pickle_path'], 'rb') as fp:
                    novel = pickle.load(fp)
            else:
                os.remove(novel_pickle_path)
                novel = self._spider.fetch()
        else:
            novel = self._spider.fetch()

        if novel:
            print(f'[INFO]: The data of book(id={self.common_settings["book_id"]}) except image files is ready.')

            # TODO write epub

            print('Write epub finished. Now delete all the artifacts if set.')

            # clean temporary files if clean_artifacts option is set to True
            if self.common_settings['clean_artifacts']:
                try:
                    shutil.rmtree(self.common_settings['image_download_folder'])
                    os.remove(novel_pickle_path)
                except (Exception,):
                    pass

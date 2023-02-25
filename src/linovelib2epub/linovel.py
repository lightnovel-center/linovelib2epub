import io
import os
import pickle
import shutil
import time
import urllib.parse
import uuid
from pathlib import Path
from typing import Optional, Union

from ebooklib import epub
from PIL import Image
from rich import print as rich_print
from rich.prompt import Confirm

from . import settings
from .exceptions import LinovelibException
from .logger import Logger
from .models import LightNovel
from .spider import ASYNCIO, LinovelibMobileSpider
from .utils import (create_folder_if_not_exists, random_useragent,
                    read_pkg_resource, sanitize_pathname)


class EpubWriter:

    def __init__(self, epub_settings) -> None:
        self.epub_settings = epub_settings
        self.logger = Logger(logger_name=__class__.__name__,
                             log_filename=self.epub_settings["log_filename"]).get_logger()

    def dump_settings(self):
        self.logger.info(self.epub_settings)

    def write(self, novel: LightNovel):
        start = time.perf_counter()
        self.logger.info(f'[Config]: has_illustration: {self.epub_settings["has_illustration"]};'
                         f' divide_volume: {self.epub_settings["divide_volume"]}')

        # remember _novel_book_title for later usage, don't want to pass novel_book_title
        book_title = self._novel_book_title = novel.book_title
        author = novel.author
        cover_file = self.epub_settings["image_download_folder"] + "/" + novel.book_cover_local

        if not self.epub_settings["divide_volume"]:
            self._write_epub(book_title, author, novel.volumes, cover_file)
        else:
            for volume in novel.volumes:
                self._write_epub(f'{book_title}_{volume["title"]}', author, volume, cover_file)

        # tips: show output file folder
        output_folder = os.path.join(os.getcwd(), self._get_output_folder())
        self.logger.info('(Perf metrics) Write epub took: {} seconds'.format(time.perf_counter() - start))
        rich_print(f"The output epub is located in [link={output_folder}]this folder[/link]. "
                   f"(You can see the link if you use a modern shell.)")

    def _write_epub(self, title, author, volumes, cover_file, cover_filename: str = None):
        """

        :param title: for one epub has many volumes, the title should be book title.
           for one epub per volume, the title should be volume title.
        :param author:
        :param volumes: if divide_volume is False, this parameter should be volume list(List[LightNovelVolume]).
           if divide_volume is True, it should be one volum(LightNovelVolume).
        :param cover_file: local image file path
        :param cover_filename: cover_filename has no format suffix such as ".jpg"
        :return:
        """

        book = epub.EpubBook()
        # epub basic info
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(title)
        book.set_language('zh')
        book.add_author(author)
        cover_type = cover_file.split('.')[-1]
        if cover_filename is None:
            cover_filename = 'cover'
        book.set_cover(cover_filename + '.' + cover_type, open(cover_file, 'rb').read())

        book.spine = ["nav", ]

        default_style_chapter = self._get_default_chapter_style()
        custom_style_chapter = self._get_cutom_chapter_style()

        chapter_index = -1
        file_index = -1

        def _write_volume(book, custom_style_chapter, default_style_chapter, volume, volume_title):
            # reset content
            write_content = ""
            # use outer scope counters
            nonlocal chapter_index
            nonlocal file_index

            html_volume_title = "<h1>" + volume_title + "</h1>"
            write_content += html_volume_title
            book.toc.append([epub.Section(volume_title), []])
            chapter_index += 1
            for chapter in volume['chapters']:
                file_index += 1
                chapter_title = chapter['title']

                html_chapter_title = "<h2>" + chapter_title + "</h2>"
                write_content += html_chapter_title + str(chapter["content"]).replace(
                    """<div class="acontent" id="acontent">""", "")
                write_content = write_content.replace('png', 'jpg')

                page = epub.EpubHtml(title=chapter_title, file_name=f"{file_index}.xhtml", lang="zh")
                page.set_content(write_content)

                # add `<link>` tag to page `<head>` section.
                self._set_page_style(book, custom_style_chapter, default_style_chapter, page)

                book.toc[chapter_index][1].append(page)
                book.spine.append(page)

                write_content = ""

        if not self.epub_settings["divide_volume"]:
            for volume in volumes:
                volume_title = volume['title']
                _write_volume(book, custom_style_chapter, default_style_chapter, volume, volume_title)
        else:
            create_folder_if_not_exists(self._novel_book_title)
            volume = volumes
            volume_title = title
            _write_volume(book, custom_style_chapter, default_style_chapter, volume, volume_title)

        # DEFAULT CHAPTER STYLE & CUSTOM CHAPTER STYLE
        book.add_item(default_style_chapter)
        if custom_style_chapter:
            book.add_item(custom_style_chapter)

        # IMAGES
        images_folder = self.epub_settings["image_download_folder"]
        self._add_images(book, images_folder)

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # COVER STYLE
        cover_html = book.get_item_with_id('cover')
        self._set_default_cover_style(book, cover_html)
        if self.epub_settings["custom_style_cover"]:
            self._set_cutom_cover_style(book, cover_html)

        # NAV STYLE
        nav_html = book.get_item_with_id('nav')
        self._set_default_nav_style(book, nav_html)
        if self.epub_settings["custom_style_nav"]:
            self._set_custom_nav_style(book, nav_html)

        # FINAL WRITE
        # if divide volume, create a folder named title, or leave folder as "“
        out_folder = self._get_output_folder()
        epub.write_epub(sanitize_pathname(out_folder) + "/" + sanitize_pathname(title) + '.epub', book)

    @staticmethod
    def _set_page_style(book, custom_style_chapter, default_style_chapter, page):
        page.add_item(default_style_chapter)
        if custom_style_chapter:
            page.add_item(custom_style_chapter)
        book.add_item(page)

    def _add_images(self, book, images_folder):
        if self.epub_settings["has_illustration"]:
            image_files = os.listdir(images_folder)
            # THINK: if enable multi Linovel instances, need to make sure images_folder corresponds to a seperate instance.
            # Or it will add all images into a certain epub.
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
                img = epub.EpubItem(file_name=f"{images_folder}/{new_image_file}", media_type="image/jpeg",
                                    content=data_img)
                book.add_item(img)

    def _get_output_folder(self):
        if self.epub_settings['divide_volume']:
            out_folder = str(self._novel_book_title)
        else:
            out_folder = '.'
        return out_folder

    def _get_cutom_chapter_style(self):
        if self.epub_settings["custom_style_chapter"]:
            custom_style_chapter = epub.EpubItem(uid="style_chapter_custom", file_name="styles/chapter_custom.css",
                                                 media_type="text/css",
                                                 content=self.epub_settings["custom_style_chapter"])
        else:
            custom_style_chapter = None

        return custom_style_chapter

    def _get_default_chapter_style(self):
        style_chapter = read_pkg_resource('./styles/chapter.css')
        default_style_chapter = epub.EpubItem(uid="style_chapter", file_name="styles/chapter.css",
                                              media_type="text/css", content=style_chapter)
        return default_style_chapter

    def _set_cutom_cover_style(self, book, cover_html):
        custom_style_cover = epub.EpubItem(uid="style_cover_custom", file_name="styles/cover_custom.css",
                                           media_type="text/css",
                                           content=self.epub_settings["custom_style_cover"])
        cover_html.add_item(custom_style_cover)
        book.add_item(custom_style_cover)

    def _set_default_cover_style(self, book, cover_html):
        default_style_cover_content = read_pkg_resource('./styles/cover.css')
        default_style_cover = epub.EpubItem(uid="style_cover", file_name="styles/cover.css", media_type="text/css",
                                            content=default_style_cover_content)
        cover_html.add_item(default_style_cover)
        book.add_item(default_style_cover)

    def _set_custom_nav_style(self, book, nav_html):
        custom_style_nav = epub.EpubItem(uid="style_nav_custom", file_name="styles/nav_custom.css",
                                         media_type="text/css", content=self.epub_settings["custom_style_nav"])
        nav_html.add_item(custom_style_nav)
        book.add_item(custom_style_nav)

    def _set_default_nav_style(self, book, nav_html):
        default_style_nav_content = read_pkg_resource('./styles/nav.css')
        default_style_nav = epub.EpubItem(uid="style_nav", file_name="styles/nav.css",
                                          media_type="text/css", content=default_style_nav_content)
        nav_html.add_item(default_style_nav)
        book.add_item(default_style_nav)


class Linovelib2Epub():

    def __init__(self,
                 book_id: Optional[Union[int, str]] = None,
                 base_url: str = settings.BASE_URL,
                 divide_volume: bool = settings.DIVIDE_VOLUME,
                 has_illustration: bool = settings.HAS_ILLUSTRATION,
                 image_download_folder: str = settings.IMAGE_DOWNLOAD_FOLDER,
                 pickle_temp_folder: str = settings.PICKLE_TEMP_FOLDER,
                 clean_artifacts: bool = settings.CLEAN_ARTIFACTS,
                 select_volume_mode: bool = settings.SELECT_VOLUME_MODE,
                 http_timeout: int = settings.HTTP_TIMEOUT,
                 http_retries: int = settings.HTTP_RETRIES,
                 http_cookie: str = settings.HTTP_COOKIE,
                 disable_proxy: bool = settings.DISABLE_PROXY,
                 image_download_strategy: str = ASYNCIO,
                 custom_style_cover: str = None,
                 custom_style_nav: str = None,
                 custom_style_chapter: str = None):

        if book_id is None:
            raise LinovelibException('book_id parameter must be set.')
        if base_url is None:
            raise LinovelibException('base_url parameter must be set.')
        # add option spider_class

        u = urllib.parse.urlsplit(base_url)

        # identify one-time unique crawl
        # - use for novel_pickle_path
        # - use for a unique log_file name instead of timestamp to avoid big file in one day.
        run_identifier = f'{u.hostname}_{book_id}'

        self.common_settings = {
            'book_id': book_id,
            'base_url': base_url,
            'divide_volume': True if select_volume_mode else divide_volume,
            'has_illustration': has_illustration,
            'image_download_folder': f'{image_download_folder}/{u.hostname}',
            'pickle_temp_folder': pickle_temp_folder,
            'novel_pickle_path': f'{pickle_temp_folder}/{run_identifier}.pickle',
            'clean_artifacts': clean_artifacts,
            'select_volume_mode': select_volume_mode,
            'log_filename': run_identifier
        }

        self.spider_settings = {
            **self.common_settings,
            'image_download_strategy': image_download_strategy,
            'http_timeout': http_timeout,
            'http_retries': http_retries,
            'random_useragent': random_useragent(),
            'http_cookie': http_cookie,
            'disable_proxy': disable_proxy
        }
        # dynamic inject LinovelibSpider or otherSpider definitions
        self._spider = LinovelibMobileSpider(spider_settings=self.spider_settings)

        self.epub_settings = {
            **self.common_settings,
            'custom_style_cover': custom_style_cover,
            'custom_style_nav': custom_style_nav,
            'custom_style_chapter': custom_style_chapter
        }
        self._epub_writer = EpubWriter(epub_settings=self.epub_settings)

        self.logger = Logger(logger_name=__class__.__name__,
                             log_filename=self.common_settings["log_filename"]).get_logger()

    def run(self):
        # recover from last work. only support this format: [hostname]_3573.pickle
        # 1.solve novel pickle
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
            # 2.solve images download and save novel pickle
            self.logger.info(f'The data of book(id={self.common_settings["book_id"]}) except image files is ready.')
            self._spider.post_fetch(novel)

            # 3.write epub
            self._epub_writer.write(novel)

            # 4.cleanup
            self.logger.info('Write epub finished. Now delete all the artifacts if set.')
            self._cleanup()

            self.logger.info('=' * 80)

    def _cleanup(self):
        # clean temporary files if clean_artifacts option is set to True
        if self.common_settings['clean_artifacts']:
            novel_pickle_path = Path(self.common_settings['novel_pickle_path'])
            try:
                shutil.rmtree(self.common_settings['image_download_folder'])
                os.remove(novel_pickle_path)
            except (Exception,):
                pass

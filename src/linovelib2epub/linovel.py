import io
import os
import pickle
import shutil
import time
import urllib.parse
from enum import Enum
from pathlib import Path
from typing import Optional, Union, Dict, Any, List, cast

import uuid
from PIL import Image
from ebooklib import epub
from ebooklib.epub import EpubItem, EpubBook, EpubHtml
from rich import print as rich_print
from rich.prompt import Confirm

from . import settings
from .exceptions import LinovelibException
from .logger import Logger
from .models import LightNovel, LightNovelVolume, LightNovelImage
from .spider import ASYNCIO, LinovelibSpiderMobile, LinovelibSpiderPC  # type: ignore[attr-defined]
from .spider.masiro_spider import MasiroSpider
from .spider.wenku8_spider import Wenku8Spider
from .utils import (create_folder_if_not_exists, random_useragent,
                    read_pkg_resource, sanitize_pathname)


class EpubWriter:

    def __init__(self, epub_settings: Dict[str, Any]) -> None:
        self._novel_book_title = ''
        self.epub_settings = epub_settings
        self.logger = Logger(logger_name=type(self).__name__,
                             log_filename=self.epub_settings["log_filename"]).get_logger()

    def dump_settings(self) -> None:
        self.logger.info(self.epub_settings)

    def write(self, novel: LightNovel) -> None:
        start = time.perf_counter()
        self.logger.info(f'[Config]: has_illustration: {self.epub_settings["has_illustration"]};'
                         f' divide_volume: {self.epub_settings["divide_volume"]}')

        book_title = self._novel_book_title = novel.book_title
        author = novel.author
        cover_file = self.epub_settings["image_download_folder"] + "/" + novel.book_cover.local_relative_path

        if not self.epub_settings["divide_volume"]:
            self._write_epub(book_title, author, novel.volumes, cover_file)
        else:
            for volume in novel.volumes:
                # if volume image folder is not empty, then use the first image as the cover
                if volume.volume_cover:
                    cover_file = f'{self.epub_settings["image_download_folder"]}/{volume.volume_cover.local_relative_path}'
                self._write_epub(f'{book_title}_{volume.title}', author, volume, cover_file)

        # tips: show output file folder
        output_folder = os.path.join(os.getcwd(), self._get_output_folder())
        self.logger.info('(Perf metrics) Write epub took: {} seconds'.format(time.perf_counter() - start))
        rich_print(f"The output epub is located in [link={output_folder}]this folder[/link]. "
                   f"(You can see the link if you use a modern shell.)")

    def _write_epub(self,
                    title: str,
                    author: str,
                    volumes: List[LightNovelVolume] | LightNovelVolume,
                    cover_file: str,
                    cover_filename: str | None = None) -> None:
        """

        :param title: for one epub has many volumes, the title should be book title.
           for one epub per volume, the title should be volume title.
        :param author:
        :param volumes: if divide_volume is False, this parameter should be volume list(List[LightNovelVolume]).
           if divide_volume is True, it should be one volume(LightNovelVolume).
        :param cover_file: local image file path
        :param cover_filename: cover_filename has no format suffix(e.g. ".jpg")
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
        _cover_file = cover_filename + '.' + cover_type
        self.logger.debug(f'Cover file: {_cover_file}')
        try:
            book.set_cover(_cover_file, open(cover_file, 'rb').read())
        except:
            # MUST set cover file to avoid ebooklib error
            width, height = 400, 569
            cover_image_fallback = Image.new("RGB", (width, height), "gray")
            book.set_cover(_cover_file, cover_image_fallback.tobytes())
            self.logger.warning("Cover file is not found or can't be opened. => use empty cover.")

        book.spine = ["nav", ]

        default_style_chapter = self._get_default_chapter_style()
        custom_style_chapter = self._get_custom_chapter_style()

        chapter_index = -1
        file_index = -1

        def _write_volume(book: EpubBook,
                          custom_style_chapter: EpubItem | None,
                          default_style_chapter: EpubItem | None,
                          volume: LightNovelVolume,
                          volume_title: str) -> None:
            # reset content
            write_content = ""
            # use outer scope counters
            nonlocal chapter_index
            nonlocal file_index

            if not self.epub_settings["divide_volume"]:
                # volume_title as h1
                html_volume_title = "<h1>" + volume_title + "</h1>"
                write_content += html_volume_title
                book.toc.append([epub.Link(f"{file_index + 1}.xhtml", volume_title, str(uuid.uuid4())), []])

            chapter_index += 1
            for chapter in volume.chapters:
                file_index += 1
                chapter_title = chapter.title

                if not self.epub_settings["divide_volume"]:
                    # chapter_title as h2
                    html_chapter_title = "<h2>" + chapter_title + "</h2>"
                    write_content += html_chapter_title + str(chapter.content).replace(
                        """<div class="acontent" id="acontent">""", "")
                else:
                    # chapter_title as h1
                    html_chapter_title = "<h1>" + chapter_title + "</h1>"
                    write_content += html_chapter_title + str(chapter.content).replace(
                        """<div class="acontent" id="acontent">""", "")

                write_content = write_content.replace('png', 'jpg')

                page = epub.EpubHtml(title=chapter_title, file_name=f"{file_index}.xhtml", lang="zh")
                page.set_content(write_content)

                # add `<link>` tag to page `<head>` section.
                self._set_page_style(book, custom_style_chapter, default_style_chapter, page)

                if not self.epub_settings["divide_volume"]:
                    # volume_title as h1
                    book.toc[chapter_index][1].append(page)
                else:
                    # chapter_title as h1
                    book.toc.append(epub.Link(f"{file_index}.xhtml", chapter_title, str(uuid.uuid4())))

                book.spine.append(page)

                write_content = ""

        illustrations: List[LightNovelImage] = []

        if not self.epub_settings["divide_volume"]:
            volumes_list = cast(List[LightNovelVolume], volumes)  # Cast to List[LightNovelVolume]
            for volume in volumes_list:
                illustrations.extend(volume.get_illustrations())
                volume_title = volume.title
                _write_volume(book, custom_style_chapter, default_style_chapter, volume, volume_title)
        else:
            create_folder_if_not_exists(self._novel_book_title)

            single_volume = cast(LightNovelVolume, volumes)  # Cast to LightNovelVolume
            volume = single_volume

            illustrations = volume.get_illustrations()
            volume_title = title
            _write_volume(book, custom_style_chapter, default_style_chapter, volume, volume_title)

        # DEFAULT CHAPTER STYLE & CUSTOM CHAPTER STYLE
        book.add_item(default_style_chapter)
        if custom_style_chapter:
            book.add_item(custom_style_chapter)

        # IMAGES
        images_folder = self.epub_settings["image_download_folder"]
        self._add_images(book, images_folder, illustrations)

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # COVER STYLE
        cover_html = book.get_item_with_id('cover')
        if cover_html:
            self._set_default_cover_style(book, cover_html)
            if self.epub_settings["custom_style_cover"]:
                self._set_custom_cover_style(book, cover_html)

        # NAV STYLE
        nav_html = book.get_item_with_id('nav')
        self._set_default_nav_style(book, nav_html)
        if self.epub_settings["custom_style_nav"]:
            self._set_custom_nav_style(book, nav_html)

        # FINAL WRITE
        # if divide volume, create a folder named title, or leave folder as "“
        out_folder = self._get_output_folder()
        prefix = ""
        if not self.epub_settings["divide_volume"]:
            prefix = ""
        else:
            if volume.volume_id is not None:
                prefix = "%02d." % int(volume.volume_id)

        epub.write_epub(sanitize_pathname(out_folder) + "/" + prefix + sanitize_pathname(title) + '.epub', book)

    @staticmethod
    def _set_page_style(book: EpubBook,
                        custom_style_chapter: EpubItem | None,
                        default_style_chapter: EpubItem | None,
                        page: EpubHtml) -> None:
        page.add_item(default_style_chapter)
        if custom_style_chapter:
            page.add_item(custom_style_chapter)
        book.add_item(page)

    def _add_images(self, book: EpubBook, images_folder: str, illustrations: List[LightNovelImage]) -> None:
        def _add_image(images_folder: str, illustration: LightNovelImage) -> None:

            image_extensions_white_list = [".jpg", ".png", ".webp", ".jpeg", ".bmp", ".gif"]
            image_filename = illustration.filename
            if not any(image_filename.endswith(ext) for ext in image_extensions_white_list):
                return

            image_path = f'{images_folder}/{illustration.local_relative_path}'
            try:
                img = Image.open(image_path)
            except (Exception,):
                return

            # unify to JPEG => get better epub reader support
            b = io.BytesIO()
            img = img.convert('RGB')
            img.save(b, 'jpeg')
            data_img = b.getvalue()

            new_image_relative_path = os.path.splitext(illustration.local_relative_path)[0] + ".jpg"
            img = epub.EpubItem(file_name=f'{images_folder}/{new_image_relative_path}',
                                media_type="image/jpeg",
                                content=data_img)
            book.add_item(img)

        for illustration in illustrations:
            _add_image(images_folder, illustration)

    def _get_output_folder(self) -> str:
        if self.epub_settings['divide_volume']:
            out_folder = str(self._novel_book_title)
        else:
            out_folder = '.'
        return out_folder

    def _get_custom_chapter_style(self) -> EpubItem | None:
        if self.epub_settings["custom_style_chapter"]:
            custom_style_chapter = epub.EpubItem(uid="style_chapter_custom", file_name="styles/chapter_custom.css",
                                                 media_type="text/css",
                                                 content=self.epub_settings["custom_style_chapter"])
        else:
            custom_style_chapter = None

        return custom_style_chapter

    @staticmethod
    def _get_default_chapter_style() -> EpubItem:
        style_chapter = read_pkg_resource('styles', 'chapter.css')
        default_style_chapter = epub.EpubItem(uid="style_chapter", file_name="styles/chapter.css",
                                              media_type="text/css", content=style_chapter)
        return default_style_chapter

    def _set_custom_cover_style(self, book: EpubBook, cover_html: EpubHtml) -> None:
        custom_style_cover = epub.EpubItem(uid="style_cover_custom", file_name="styles/cover_custom.css",
                                           media_type="text/css",
                                           content=self.epub_settings["custom_style_cover"])
        cover_html.add_item(custom_style_cover)
        book.add_item(custom_style_cover)

    @staticmethod
    def _set_default_cover_style(book: EpubBook, cover_html: EpubHtml) -> None:
        default_style_cover_content = read_pkg_resource('styles', 'cover.css')
        default_style_cover = epub.EpubItem(uid="style_cover", file_name="styles/cover.css", media_type="text/css",
                                            content=default_style_cover_content)
        cover_html.add_item(default_style_cover)
        book.add_item(default_style_cover)

    def _set_custom_nav_style(self, book: EpubBook, nav_html: EpubHtml) -> None:
        custom_style_nav = epub.EpubItem(uid="style_nav_custom", file_name="styles/nav_custom.css",
                                         media_type="text/css", content=self.epub_settings["custom_style_nav"])
        nav_html.add_item(custom_style_nav)
        book.add_item(custom_style_nav)

    @staticmethod
    def _set_default_nav_style(book: EpubBook, nav_html: EpubHtml) -> None:
        default_style_nav_content = read_pkg_resource('styles', 'nav.css')
        default_style_nav = epub.EpubItem(uid="style_nav", file_name="styles/nav.css",
                                          media_type="text/css", content=default_style_nav_content)
        nav_html.add_item(default_style_nav)
        book.add_item(default_style_nav)


class TargetSite(Enum):
    # ZH [移动版本]
    LINOVELIB_MOBILE = 'linovelib_mobile'
    # 繁体 TW or HK [移动版本]
    LINOVELIB_MOBILE_TRADITIONAL = 'linovelib_mobile_traditional'
    # ZH [电脑网页版本]
    LINOVELIB_PC = 'linovelib_pc'
    # 繁体 TW or HK [电脑网页版本]
    LINOVELIB_PC_TRADITIONAL = 'linovelib_pc_traditional'
    MASIRO = 'masiro'
    WENKU8 = 'wenku8'


class Linovelib2Epub:

    def __init__(self,
                 book_id: Optional[Union[int, str]] = None,
                 target_site: TargetSite = TargetSite.LINOVELIB_MOBILE,
                 divide_volume: bool = settings.DIVIDE_VOLUME,
                 select_volume_mode: bool = settings.SELECT_VOLUME_MODE,
                 has_illustration: bool = settings.HAS_ILLUSTRATION,
                 image_download_folder: str = settings.IMAGE_DOWNLOAD_FOLDER,
                 pickle_temp_folder: str = settings.PICKLE_TEMP_FOLDER,
                 clean_artifacts: bool = settings.CLEAN_ARTIFACTS,
                 http_timeout: int = settings.HTTP_TIMEOUT,
                 http_retries: int = settings.HTTP_RETRIES,
                 http_cookie: str = settings.HTTP_COOKIE,
                 custom_style_cover: str | None = None,
                 custom_style_nav: str | None = None,
                 custom_style_chapter: str | None = None,
                 disable_proxy: bool = settings.DISABLE_PROXY,
                 image_download_strategy: str = ASYNCIO,
                 log_level: str = "INFO",
                 browser_path: str | None = None,
                 browser_driver_path: str | None = None,
                 chapter_crawl_delay: int | None = 3,
                 page_crawl_delay: int | None = 2,
                 headless: bool = False,
                 image_download_max_epochs: int | None = None
                 ):
        if book_id is None:
            raise LinovelibException('book_id parameter must be set.')

        self.target_site = target_site

        site_to_base_url = {
            TargetSite.LINOVELIB_MOBILE: 'https://www.bilinovel.com',
            TargetSite.LINOVELIB_MOBILE_TRADITIONAL: 'https://www.bilinovel.com',

            TargetSite.LINOVELIB_PC: 'https://www.linovelib.com',
            TargetSite.LINOVELIB_PC_TRADITIONAL: 'https://www.linovelib.com',

            TargetSite.MASIRO: 'https://masiro.me',
            TargetSite.WENKU8: 'https://www.wenku8.net',
        }
        # user override base_url, or use fallback detection
        base_url = site_to_base_url[self.target_site]

        # traditional flag
        traditional = False
        if target_site in (TargetSite.LINOVELIB_MOBILE_TRADITIONAL, TargetSite.LINOVELIB_PC_TRADITIONAL):
            traditional = True
        # mobile flag
        mobile = False
        if target_site in (TargetSite.LINOVELIB_MOBILE, TargetSite.LINOVELIB_MOBILE_TRADITIONAL):
            mobile = True

        u = urllib.parse.urlsplit(base_url)

        # identify one-time unique crawl
        # - use for novel_pickle_path
        # - use for a unique log_file name instead of timestamp to avoid big file in one day.
        run_identifier: str = f'{u.hostname}_{book_id}'

        self.common_settings = {
            'book_id': book_id,
            'base_url': base_url,
            'divide_volume': True if select_volume_mode else divide_volume,
            'has_illustration': has_illustration,
            'image_download_folder': image_download_folder,
            'pickle_temp_folder': pickle_temp_folder,
            'novel_pickle_path': f'{pickle_temp_folder}/{run_identifier}.pickle',
            'clean_artifacts': clean_artifacts,
            'select_volume_mode': select_volume_mode,
            'log_filename': run_identifier,
            'log_level': log_level,
            'traditional': traditional,
            'mobile': mobile
        }

        self.spider_settings = {
            **self.common_settings,
            'image_download_strategy': image_download_strategy,
            'http_timeout': http_timeout,
            'http_retries': http_retries,
            'random_useragent': random_useragent(),
            'http_cookie': http_cookie,
            'browser_path': browser_path,
            'browser_driver_path': browser_driver_path,
            'disable_proxy': disable_proxy,
            'chapter_crawl_delay': chapter_crawl_delay,
            'page_crawl_delay': page_crawl_delay,
            'headless': headless,
        }

        if image_download_max_epochs is not None:
            self.spider_settings.update({'image_download_max_epochs': image_download_max_epochs})

        site_to_spider = {
            TargetSite.LINOVELIB_MOBILE: LinovelibSpiderMobile,
            TargetSite.LINOVELIB_MOBILE_TRADITIONAL: LinovelibSpiderMobile,
            TargetSite.LINOVELIB_PC: LinovelibSpiderPC,
            TargetSite.LINOVELIB_PC_TRADITIONAL: LinovelibSpiderPC,
            TargetSite.MASIRO: MasiroSpider,
            TargetSite.WENKU8: Wenku8Spider,
        }
        self._spider = site_to_spider[self.target_site](spider_settings=self.spider_settings)

        self.epub_settings = {
            **self.common_settings,
            'custom_style_cover': custom_style_cover,
            'custom_style_nav': custom_style_nav,
            'custom_style_chapter': custom_style_chapter
        }
        self._epub_writer = EpubWriter(epub_settings=self.epub_settings)

        log_filename = self.common_settings["log_filename"]
        log_filename_str = cast(str, log_filename)
        self.logger = Logger(logger_name=type(self).__name__,
                             logger_level=self.common_settings["log_level"],
                             log_filename=log_filename_str).get_logger()

    def run(self) -> None:
        # recover from last work. only support this format: [hostname]_3573.pickle
        # 1.solve novel pickle
        pickle_path = self.common_settings['novel_pickle_path']
        pickle_path = cast(str, pickle_path)
        novel_pickle_path = Path(pickle_path)
        if novel_pickle_path.exists():
            if Confirm.ask("The last unfinished work was detected, continue with your last job?"):
                with open(pickle_path, 'rb') as fp:
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

    def _cleanup(self) -> None:
        # clean temporary files if clean_artifacts option is set to True
        if self.common_settings['clean_artifacts']:
            pickle_path = cast(str, self.common_settings['novel_pickle_path'])
            novel_pickle_path = Path(pickle_path)
            try:
                shutil.rmtree(self.common_settings['image_download_folder'])  # type: ignore[arg-type]
                os.remove(novel_pickle_path)
            except (Exception,):
                pass

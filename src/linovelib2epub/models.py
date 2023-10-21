import urllib
from dataclasses import dataclass, field
from typing import List, Type
from urllib.parse import urlparse


class ImageDuplicateCheckingStrategy:

    def is_duplicate(self, url_1, url_2):
        return url_1 == url_2


class LinovelibMobileImageDuplicateCheckingStrategy(ImageDuplicateCheckingStrategy):

    def is_duplicate(self, url_1, url_2):
        # https://linovelib-img.zezefans.com/3/3843/206654/227245.jpg => /3/3843/206654/227245.jpg
        # https://img3.readpai.com/3/3843/206654/227245.jpg => /3/3843/206654/227245.jpg
        # linovelib 这种实际上应该也算重复，但是从地址来看，无法感知是否重复。
        # 因此这里需要更加严格的重复判断

        path_1 = urlparse(url_1).path
        path_2 = urlparse(url_2).path
        if path_1 == path_2:
            return True
        else:
            return False


class MasiroImageDuplicateCheckingStrategy(ImageDuplicateCheckingStrategy):

    def is_duplicate(self, url_1, url_2):
        # 完全一致，才被认为是重复
        return url_1 == url_2


class ImageDuplicationChecker:
    def __init__(self, duplicate_checking_strategy):
        self.duplicate_checking_strategy: ImageDuplicateCheckingStrategy = duplicate_checking_strategy

    def is_duplicate(self, url_1, url_2):
        return self.duplicate_checking_strategy.is_duplicate(url_1, url_2)


@dataclass
class LightNovelImage:
    # example: http://example.com no path, host only
    site_base_url: str = ''

    # 这个图片从属html页面的原始地址
    # 这个字段用于处理 src 为相对路径的情况，目前还没有使用。
    related_page_url: str = ""

    # relative url format or full url format
    # example:
    # - http://example.com/path/to/1.jpg => PASS
    # - /path/2.jpg(relative to website root) => ADD hostname
    # - //i0.hdslb.com/bfs/archive/aaa.png(no network protocol) => ADD protocol https or http ?
    # - ./sub_folder/2.jpg(relative to current folder) or ../ or ../../ etc. => not implement yet now.
    remote_src: str = ''

    chapter_id: int | str | None = None

    volume_id: int | str | None = None

    book_id: int | str | None = None

    is_book_cover: bool = False

    @property
    def hostname(self):
        u = urllib.parse.urlsplit(self.site_base_url)
        return u.hostname

    @property
    def download_url(self):
        # computed property from url_prefix and remote_src
        if self.remote_src.startswith("/"):
            full_url = f'{self.site_base_url}{self.remote_src}'
        elif self.remote_src.startswith("//"):
            full_url = f'https:{self.remote_src}'
        else:
            full_url = self.remote_src
        return full_url

    @property
    def filename(self):
        return self.remote_src.rsplit("/", 1)[1]

    @property
    def local_relative_path(self):
        # derived property from self
        if self.is_book_cover:
            local_relative_path = f'{self.hostname}/{self.book_id}/{self.filename}'
        else:
            local_relative_path = f'{self.hostname}/{self.book_id}/{self.volume_id}/{self.filename}'
        return local_relative_path


@dataclass
class LightNovelChapter:
    chapter_id: int | str | None
    title: str = ''
    content: str = ''
    illustrations: List[LightNovelImage] = field(default_factory=list)


@dataclass
class LightNovelVolume:
    volume_id: int | str | None
    title: str = ''
    chapters: List[LightNovelChapter] = field(default_factory=list)

    @property
    def volume_cover(self) -> LightNovelImage | None:
        illustrations = self.get_illustrations()
        if illustrations:
            return illustrations[0]
        return None

    def _resolve_image_duplicate_checking_strategy(self) -> Type[ImageDuplicateCheckingStrategy]:
        if self.chapters and self.chapters[0].illustrations:
            image_sample = self.chapters[0].illustrations[0]
            hostname = image_sample.hostname
            hostname_to_strategy = {
                'w.linovelib.com': LinovelibMobileImageDuplicateCheckingStrategy,
                'masiro.me': MasiroImageDuplicateCheckingStrategy
            }
            return hostname_to_strategy.get(hostname, ImageDuplicateCheckingStrategy)

        return ImageDuplicateCheckingStrategy

    def get_illustrations(self) -> List:
        """
        # 注意，不同章节的 image remote src 之间可能会存在重复。为了加速图片下载，这里需要去重。
        由于LightNovelImage 是一个复杂对象，因此需要自定义逻辑去重，而不能依赖简单的set() 来去重。

        :return: unique image list
        """
        volume_illustrations: List[LightNovelImage] = []
        for chapter in self.chapters:
            volume_illustrations.extend(chapter.illustrations)

        Strategy = self._resolve_image_duplicate_checking_strategy()
        duplication_checker = ImageDuplicationChecker(Strategy())

        # dedupe
        unique_image_list = []
        # for debug
        duplicate_image_list = []

        for image_obj in volume_illustrations:
            is_duplicate_flag = False
            for unique_obj in unique_image_list:
                if duplication_checker.is_duplicate(image_obj.remote_src, unique_obj.remote_src):
                    duplicate_image_list.append(image_obj.remote_src)
                    is_duplicate_flag = True
                    break
            if not is_duplicate_flag:
                unique_image_list.append(image_obj)

        return unique_image_list

    def add_chapter(self, cid: int | str | None, title: str = '', content: str = '',
                    illustrations: List[LightNovelImage] = None) -> None:
        new_chapter: LightNovelChapter = LightNovelChapter(cid, title, content, illustrations)
        self.chapters.append(new_chapter)


@dataclass
class LightNovel:
    book_id: int | str | None = None
    book_title: str = ''
    author: str = ''
    description: str = ''

    book_cover: LightNovelImage = None
    volumes: List[LightNovelVolume] = field(default_factory=list)

    # status flags
    basic_info_ready: bool = False
    volumes_content_ready: bool = False

    def __post_init__(self) -> None:
        # data state flags
        self.basic_info_ready = False
        self.volumes_content_ready = False

    def get_chapters_size(self) -> int:
        return sum([len(volume.chapters) for volume in self.volumes if volume.chapters])

    def get_illustrations(self) -> List:
        """
        这里不需要设计为去重，去重逻辑放在volume的粒度范围
        :return:
        """
        illustrations = []
        for volume in self.volumes:
            illustrations.extend(volume.get_illustrations())
        return illustrations

    def add_volume(self,
                   vid: int | str | None,
                   title: str = '',
                   chapters: List[LightNovelChapter] | None = None
                   ) -> None:
        chapters = chapters or []
        new_volume: LightNovelVolume = LightNovelVolume(vid, title, chapters)
        self.volumes.append(new_volume)

    def mark_basic_info_ready(self) -> None:
        self.basic_info_ready = True

    def mark_volumes_content_ready(self) -> None:
        self.volumes_content_ready = True

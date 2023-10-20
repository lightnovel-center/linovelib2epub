import urllib
from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class LightNovelImage:
    # example: http://example.com/path/to or http://example.com
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
            full_url = f'{self.site_base_url}/{self.remote_src}'
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
        # derived property from book_id, volume_id
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

    def add_illustration(self, light_novel_image: LightNovelImage):
        self.illustrations.append(light_novel_image)


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

    def get_illustrations(self) -> List:
        volume_illustrations: List[LightNovelImage] = []
        for chapter in self.chapters:
            volume_illustrations.extend(chapter.illustrations)
        return volume_illustrations

    def add_chapter(self, cid: int | str | None, title: str = '', content: str = '') -> None:
        new_chapter: LightNovelChapter = LightNovelChapter(cid, title, content)
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

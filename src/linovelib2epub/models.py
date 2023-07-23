from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


@dataclass
class LightNovelChapter:
    cid: int | str | None
    title: str = ''
    content: str = ''


@dataclass
class LightNovelVolume:
    vid: int | str | None
    title: str = ''
    chapters: List[LightNovelChapter] = field(default_factory=list)

    # The set "volume_img_folders" is used to extract images in specific volume when "divide_volume=True"
    volume_img_folders: Set[str] = field(default_factory=set)
    # volume_cover is used as the cover image in specific volume when "divide_volume=True"
    volume_cover: str = ''

    # example: https://img.linovelib.com/0/682/117077/50675.jpg
    # volume_img_folder = {"117077","117900"} or {"117097"}
    # volume_cover = "117077/50677.jpg"

    def add_chapter(self, cid: int | str | None, title: str = '', content: str = '') -> None:
        new_chapter: LightNovelChapter = LightNovelChapter(cid, title, content)
        self.chapters.append(new_chapter)

    def get_chapter_by_cid(self, cid: int | str | None) -> LightNovelChapter | None:
        for chapter in self.chapters:
            if chapter.cid == cid:
                return chapter
        return None

    def get_chapters_size(self) -> int:
        return len(self.get_chapters())

    def get_chapters(self) -> List[LightNovelChapter]:
        return self.chapters


@dataclass
class LightNovel:
    bid: int | str | None = None
    book_title: str = ''
    author: str = ''
    description: str = ''
    book_cover: str = ''
    book_cover_local: str = ''

    volumes: List[LightNovelVolume] = field(default_factory=list)

    # map<volume_name, List[img_url]>
    illustration_dict: Dict[int | str, List[str]] = field(default_factory=dict)

    # status flags
    basic_info_ready: bool = False
    volumes_content_ready: bool = False

    def __post_init__(self) -> None:
        # data state flags
        self.basic_info_ready = False
        self.volumes_content_ready = False

    def get_volumes_size(self) -> int:
        return len(self.volumes)

    def get_chapters_size(self) -> int:
        count = 0
        for volume in self.volumes:
            if volume.chapters:
                count += len(volume.chapters)
        return count

    def get_illustration_set(self) -> Set[str]:
        image_set: Set[str] = set()
        for values in self.illustration_dict.values():
            for value in values:
                image_set.add(value)
        return image_set

    def add_volume(self,
                   vid: int | str | None,
                   title: str = '',
                   chapters: List[LightNovelChapter] | None = None,
                   volume_img_folders: Set[Any] | None = None,
                   volume_cover: str = '') -> None:

        chapters = chapters if chapters else []
        volume_img_folders = volume_img_folders if volume_img_folders else set()

        new_volume: LightNovelVolume = LightNovelVolume(vid, title, chapters, volume_img_folders, volume_cover)
        self.volumes.append(new_volume)

    def get_volume_by_vid(self, vid: int | str | None) -> LightNovelVolume | None:
        for volume in self.volumes:
            if volume.vid == vid:
                return volume
        return None

    def set_illustration_dict(self, illustration_dict: Dict[int | str, List[str]] | None = None) -> None:
        if illustration_dict is None:
            illustration_dict = {}
        self.illustration_dict = illustration_dict

    def mark_basic_info_ready(self) -> None:
        self.basic_info_ready = True

    def mark_volumes_content_ready(self) -> None:
        self.volumes_content_ready = True

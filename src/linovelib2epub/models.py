from typing import Any, Dict, List, Optional, Union


class LightNovelChapter():
    def __init__(self,
                 cid: Union[int, str],
                 title: str = '',
                 content: str = ''):
        self.cid = cid
        self.title = title
        self.content = content


class LightNovelVolume:
    def __init__(self,
                 vid: Union[int, str],
                 title: str = ''):
        self.vid = vid
        self.title = title
        self.chapters = []

    def add_chapter(self, cid: Union[int, str], title: str = '', content: str = ''):
        new_chapter = {
            'cid': cid,
            'title': title,
            'content': content
        }
        self.chapters.append(new_chapter)

    def get_chapter_by_cid(self, cid):
        for chapter in self.chapters:
            if chapter.cid == cid:
                return chapter
        return None

    def get_chapters_size(self):
        return len(self.get_chapters())

    def get_chapters(self):
        return self.chapters


class LightNovel:
    bid: Union[int, str] = None
    book_title: str = ''
    author: str = ''
    description: str = ''
    book_cover: str = ''

    volumes: List[Dict[str, Any]] = []

    # map<volume_name, List[img_url]>
    illustration_dict: Optional[Dict[Union[int, str], List[str]]] = None

    def __init__(self):
        self.volumes = []
        self.illustration_dict = {}

        # data states
        self.basic_info_ready = False
        self.volumes_content_ready = False

    def get_volumes_size(self):
        return len(self.volumes)

    def get_chapters_size(self):
        count = 0
        for volume in self.volumes:
            if volume['chapters']:
                count += len(volume['chapters'])
        return count

    def get_illustration_set(self):
        image_set = set()
        for values in self.illustration_dict.values():
            for value in values:
                image_set.add(value)
        return image_set

    def add_volume(self, vid: Union[int, str], title: str = '', chapters: List = None):
        new_volume = {
            'vid': vid,
            'title': title,
            'chapters': chapters if chapters else []
        }
        self.volumes.append(new_volume)

    def get_volume_by_vid(self, vid):
        for volume in self.volumes:
            if volume.vid == vid:
                return volume
        return None

    def set_illustration_dict(self, illustration_dict: Dict[Union[int, str], List[str]] = {}):
        self.illustration_dict = illustration_dict

    def mark_basic_info_ready(self):
        self.basic_info_ready = True

    def mark_volumes_content_ready(self):
        self.volumes_content_ready = True
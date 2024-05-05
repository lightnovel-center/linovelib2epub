from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from linovelib2epub.models import CatalogLinovelibChapter, CatalogLinovelibVolume
from linovelib2epub.utils import read_file

if __name__ == '__main__':
    uri = '../../analyze/linovelib-pc/volume-list.html'
    html = read_file(uri)
    soup = BeautifulSoup(html, 'lxml')
    volume_list_div = soup.select_one('#volume-list')
    volumes = volume_list_div.select('.volume')

    catalog_list: List[CatalogLinovelibVolume] = []

    for idx, item in enumerate(volumes):
        cover_src = item.select_one('a.volume-cover > img').get('src')
        volume_title = item.select_one('.volume-info > .v-line').text
        chapters = item.select_one('.chapter-list').select('li a')

        _current_chapters: List[CatalogLinovelibChapter] = []
        new_volume = CatalogLinovelibVolume(
            vid=idx + 1,
            volume_title=volume_title,
            chapters=_current_chapters
        )
        catalog_list.append(new_volume)
        for chapter in chapters:
            chapter_href = chapter.get('href')
            chapter_title = chapter.text
            chapter_url = urljoin(f'/novel', chapter_href)
            new_chapter: CatalogLinovelibChapter = CatalogLinovelibChapter(
                chapter_title=chapter_title,
                chapter_url=chapter_url
            )
            _current_chapters.append(new_chapter)

    print(catalog_list)

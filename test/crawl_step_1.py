import os
import pickle
import re
import time
from urllib.parse import urljoin

import demjson
import requests
from bs4 import BeautifulSoup

session = requests.Session()

base_url = 'https://w.linovelib.com/novel'
book_id = 682
book_url = f'{base_url}/{book_id}.html'
book_catalog_url = f'{base_url}/{book_id}/catalog'

divide_volume = False
download_image = True


def crawl_book_basic_info(url):
    # todo retry mechanism
    result = session.get(url)
    if result.status_code == 200:
        print(f'Succeed to get the novel of book_id: {book_id}')

        # pass html text to beautiful soup parser
        soup = BeautifulSoup(result.text, 'lxml')
        try:
            book_title = soup.find('h2', {'class': 'book-title'}).text
            author = soup.find('div', {'class': 'book-rand-a'}).text[:-2]
            book_summary = soup.find('section', id="bookSummary").text
            book_cover = soup.find('img', {'class': 'book-cover'})['src']
            return book_title, author, book_summary, book_cover

        except (Exception,) as e:
            print(f'Failed to parse basic info of book_id: {book_id}')

    return None


def extract_chapter_id(chapter_link):
    # https://w.linovelib.com/novel/682/32792.html => chapter_id is 32792
    return chapter_link.split('/')[-1][:-5]


def crawl_book_content(catalog_url):
    # todo retry mechanism
    book_catalog_rs = None
    try:
        book_catalog_rs = session.get(catalog_url)
    except (Exception,) as e:
        print(f'Failed to get normal response of {book_catalog_url}. It may be a network issue.')

    if book_catalog_rs and book_catalog_rs.status_code == 200:
        print(f'Succeed to get the catalog of book_id: {book_id}')

        # parse catalog data
        soup_catalog = BeautifulSoup(book_catalog_rs.text, 'lxml')
        chapter_count = soup_catalog.find('h4', {'class': 'chapter-sub-title'}).find('output').text
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

        # step 1: fix broken links in place(catalog_lis) if exits
        # catalog_lis_fix = try_fix_broken_chapter_links(catalog_lis)

        # step 2: convert catalog array to catalog dict(table of contents)
        catalog_dict = convert_to_catalog_dict(catalog_lis)

        paginated_content_dict = dict()
        image_dict = dict()
        url_next = ''

        for volume in catalog_dict:
            print(f'volume: {volume}')
            image_dict.setdefault(volume, [])

            chapter_id = -1
            for chapter in catalog_dict[volume]:
                chapter_content = ''
                chapter_title = chapter[0]
                chapter_id += 1
                # print(f'chapter_id: {chapter_id}')

                print(f'chapter : {chapter_title}')
                paginated_content_dict.setdefault(volume, []).append([chapter_title])

                # if chapter[1] is valid link, assign it to url_next
                # if chapter[1] is not a valid link, use url_next
                # handle case like: "javascript:cid(0)" etc.
                if not is_valid_chapter_link(chapter[1]):
                    # now the url_next value is the correct link of of chapter[1].
                    chapter[1] = url_next
                else:
                    url_next = chapter[1]

                while True:
                    for i in range(6):
                        if i >= 5:
                            print("Retry has no effect, stop.")
                            os._exit(0)
                        try:
                            soup = BeautifulSoup(session.get(url_next, timeout=5).text, "lxml")
                        except (Exception,) as e:
                            print(f"It's the {i + 1} time request failed, retry...")
                            print(e)
                            time.sleep(3)
                        else:
                            # when there is no error, break for loop
                            break

                    first_script = soup.find("body", {"id": "aread"}).find("script")
                    first_script_text = first_script.text
                    read_params_text = first_script_text[len('var ReadParams='):]
                    read_params_json = demjson.decode(read_params_text)
                    url_next = urljoin(base_url, read_params_json['url_next'])

                    if '_' in url_next:
                        chapter.append(url_next)
                    else:
                        break

                # handle page content(text and img)
                for page_link in chapter[1:]:
                    for i in range(6):
                        if i >= 5:
                            print("stop.")
                            os._exit(0)
                        try:
                            soup = BeautifulSoup(session.get(page_link, timeout=5).text, "lxml")
                        except:
                            print(f"It's the {i + 1} time request failed, retry...")
                            print(e)
                            time.sleep(3)
                        else:
                            break

                    images = soup.find_all('img')
                    article = str(soup.find(id="acontent"))
                    for _, image in enumerate(images):
                        # img tag format: <img src="https://img.linovelib.com/0/682/117078/50677.jpg" border="0" class="imagecontent">
                        # src format: https://img.linovelib.com/0/682/117078/50677.jpg
                        # here we convert its path `0/682/117078/50677.jpg` to `0-682-117078-50677.jpg` as filename.
                        image_src = image['src']
                        # print(f'image_src: {image_src}')
                        image_dict[volume].append(image_src)

                        # goal: https://img.linovelib.com/0/682/117077/50675.jpg => file/0-682-117078-50677.jpg

                        src_value = re.search(r"(?<=src=\").*?(?=\")", str(image))
                        replace_value = 'file/' + "-".join(src_value.group().split("/")[-4:])
                        local_article = article.replace(str(src_value.group()), str(replace_value))
                        # cache per chapter
                        chapter_content += local_article

                    print(f'Processing page... {page_link}')

                paginated_content_dict[volume][chapter_id].append(chapter_content)

        return paginated_content_dict, image_dict

    else:
        print(f'Failed to get the catalog of book_id: {book_id}')

    return None


def convert_to_catalog_dict(catalog_lis):
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
            whole_url = urljoin(base_url, href)
            current_volume.append([catalog_li_text, whole_url])

    return catalog_dict


def is_valid_chapter_link(href):
    # normal link example: /novel/682/117086.html
    # broken link example: javascript: cid(0)
    # use https://regex101.com/ to debug regular expression
    reg = "\S+/novel/\d+/\S+\.html"
    re_match = bool(re.match(reg, href))
    return re_match


if __name__ == '__main__':
    book_basic_info = crawl_book_basic_info(book_url)
    if book_basic_info:
        book_title, author, book_summary, book_cover = book_basic_info
        print(book_title, author, book_summary, book_cover)
        with open('../pickle/basic_info.pickle', 'wb') as f:
            pickle.dump([book_title, author, book_cover, divide_volume, download_image], f)

    book_content = crawl_book_content(book_catalog_url)
    if book_content:
        paginated_content_dict, image_dict = book_content
        with open('../pickle/paginated_content_dict.pickle', 'wb') as f:
            pickle.dump(paginated_content_dict, f)
        with open('../pickle/image_dict.pickle', 'wb') as f:
            pickle.dump(image_dict, f)
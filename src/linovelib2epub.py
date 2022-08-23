import io
import multiprocessing
import os
import re
import shutil
import time
import uuid
from multiprocessing import Pool
from pathlib import Path
from urllib.parse import urljoin

import demjson
import requests
from PIL import Image
from bs4 import BeautifulSoup
from ebooklib import epub
from fake_useragent import UserAgent
from rich.prompt import Confirm

import pickle

session = requests.Session()

base_url = 'https://w.linovelib.com/novel'
book_id = 3211  # API
book_url = f'{base_url}/{book_id}.html'
book_catalog_url = f'{base_url}/{book_id}/catalog'

divide_volume = False
has_illustration = True

image_download_folder = 'file'

http_timeout = 5
http_retries = 5
custom_cookie = ''


def request_headers(referer='', cookie='', random_ua=True):
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
    default_cookie = 'night=0;'
    default_referer = 'https://w.linovelib.com'
    headers = {
        # ! don't set any accept fields
        'referer': referer if referer else default_referer,
        'cookie': cookie if cookie else default_cookie,
        'user-agent': random_useragent() if random_ua else default_ua
    }
    return headers


def random_useragent():
    try:
        return UserAgent().random
    except:
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'


def request_with_retry(url, retry_max=5, timeout=5):
    current_num_of_request = 0

    while current_num_of_request <= retry_max:
        try:
            response = session.get(url, headers=request_headers(), timeout=timeout)
            if response:
                return response
            else:
                print(f'WARN: request {url} succeed but data is empty.')
                time.sleep(2)
        except (Exception,) as e:
            print(f'ERROR: request {url}', e)
            time.sleep(2)

        current_num_of_request += 1
        print('current_num_of_request: ', current_num_of_request)

    return None


def crawl_book_basic_info(url):
    result = request_with_retry(url)

    if result and result.status_code == 200:
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
    book_catalog_rs = None
    try:
        book_catalog_rs = request_with_retry(catalog_url)
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
                    resp = request_with_retry(url_next)
                    if resp:
                        soup = BeautifulSoup(resp.text, 'lxml')
                    else:
                        raise Exception(f'[ERROR]: request {url_next} failed.')

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
                    page_resp = request_with_retry(page_link)
                    if page_resp:
                        soup = BeautifulSoup(page_resp.text, 'lxml')
                    else:
                        raise Exception(f'[ERROR]: request {page_link} failed.')

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
                        replace_value = f'{image_download_folder}/' + "-".join(src_value.group().split("/")[-4:])
                        article = article.replace(str(src_value.group()), str(replace_value))

                    # print(article)
                    chapter_content += article
                    # sanitize html: replace all \r to " " has no effect for ☆ display
                    # chapter_content = chapter_content.replace('\r', "")
                    print(f'Processing page... {page_link}')

                paginated_content_dict[volume][chapter_id].append(chapter_content)

        print(f'paginated_content_dict(inner): {paginated_content_dict}')
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


def create_folder_if_not_exists(path):
    path_exists = os.path.exists(path)
    if not path_exists:
        os.makedirs(path)


def extract_image_list(image_dict=None):
    image_url_list = []
    for volume_images in image_dict.values():
        for index in range(0, len(volume_images)):
            image_url_list.append(volume_images[index])

    return image_url_list


def is_valid_link(link):
    flag = True

    if "http" not in link:
        flag = False
    if " " in link:
        flag = False

    return flag


def download_file(urls, folder=image_download_folder):
    """
    If a image url download failed, return its url. else return None.

    :param urls: single url string or url array.
    :param folder: image download folder
    :return:
    """
    if isinstance(urls, str):
        # check if the link is valid
        if not is_valid_link(urls): return

        # if url is not desired format, return
        try:
            filename = '-'.join(urls.split("/")[-4:])
        except (Exception,) as e:
            return

        save_path = f"{folder}/{filename}"

        # the file already exists, return
        filename_exists = Path(save_path)
        if filename_exists.exists():
            return

        # url is valid and never downloaded
        try:
            resp = session.get(urls, headers=request_headers(), timeout=http_timeout)
            check_image_integrity(resp)
        except (Exception,) as e:
            print(f'Error occurred when download image of {urls}.')
            print(e)
            try:
                os.remove(save_path)
            except (Exception, e) as e:
                print(e)
            return urls
        else:
            print(f"downloading image: {urls}")
            with open(save_path, "wb") as f:
                f.write(resp.content)

    if isinstance(urls, list):
        error_urls = []

        for url in urls:
            # No need to check links format
            try:
                filename = '-'.join(url.split("/")[-4:])
            except (Exception,) as e:
                return

            save_path = f"{folder}/{filename}"

            filename_exists = Path(save_path)
            if filename_exists.exists():
                return

            try:
                resp = session.get(url, headers=request_headers(), timeout=http_timeout)
                check_image_integrity(resp)
            except (Exception,) as e:
                print(f'Error occurred when download image of {urls}.')
                print(e)
                try:
                    os.remove(save_path)
                except (Exception, e) as e:
                    print(e)
                error_urls.append(url)
            else:
                print(f"downloading image: {url}")
                with open(save_path, "wb") as f:
                    f.write(resp.content)

        return error_urls


def check_image_integrity(resp):
    # check file integrity by comparing HTTP header content-length and real request tell()
    expected_length = resp.headers.get('Content-Length')
    actual_length = resp.raw.tell()  # len(resp.content)
    if expected_length and actual_length:
        # expected_length: 31949; actual_length: 31949
        # print(f'expected_length: {expected_length}; actual_length: {actual_length}')
        if int(actual_length) < int(expected_length):
            raise IOError(
                'incomplete read ({} bytes get, {} bytes expected)'.format(actual_length, expected_length)
            )


def download_images(urls=None, pool_size=os.cpu_count()):
    if urls is None:
        urls = []
    thread_pool = Pool(int(pool_size))
    error_links = thread_pool.map(download_file, urls)
    # if everything is perfect, error_links array will be []
    # if some error occurred, error_links will be those links that failed to request.

    # remove None element from array, only retain error link
    sorted_error_links = sorted(list(filter(None, error_links)))

    # for loop until all files are downloaded successfully.
    while len(sorted_error_links) > 0:
        print('Some errors occurred when download images. Retry those links that failed to request.')
        print(f'Error image links size: {len(sorted_error_links)}')
        print(f'Error image links: {sorted_error_links}')

        sorted_error_links = download_file(sorted_error_links)


def write_epub(title, author, content, cover_filename, cover_file, images_folder, output_folder=None,
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
    chapter_id = -1
    file_index = -1

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
                write_content += chapter_title + str(chapter[1]).replace("<div class=\"acontent\" id=\"acontent\">", "")
                write_content = write_content.replace('png', 'jpg')
                css = '<style>p{text-indent:2em; padding:0px; margin:0px;}</style>'
                write_content += css
                page.set_content(write_content)
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
            css = '<style>p{text-indent:2em; padding:0px; margin:0px;}</style>'
            write_content += css
            page.set_content(write_content)
            book.add_item(page)
            book.toc[chapter_id][1].append(page)
            book.spine.append(page)
            write_content = ""

    print('Now book_content(text) is ready.')

    if has_illustration:
        image_files = os.listdir(images_folder)
        for image_file in image_files:
            if not ((".jpg" or ".png" or ".webp" or ".jpeg" or ".bmp" or "gif") in str(image_file)):
                continue

            try:
                img = Image.open(images_folder + '/' + image_file)
            except (Exception,) as e:
                continue

            b = io.BytesIO()
            img = img.convert('RGB')
            img.save(b, 'jpeg')
            data_img = b.getvalue()

            new_image_file = image_file.replace('png', 'jpg')
            img = epub.EpubItem(file_name=f"{image_download_folder}/%s" % new_image_file, media_type="image/jpeg",
                                content=data_img)
            book.add_item(img)

        print('Now all images in book_content are ready.')

    folder = ''
    if output_folder is None:
        folder = ''
    else:
        create_folder_if_not_exists(output_folder)
        folder = str(output_folder) + '/'

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(folder + title + '.epub', book)


def fresh_crawl():
    create_folder_if_not_exists('pickle/')

    book_basic_info = crawl_book_basic_info(book_url)
    if book_basic_info:
        book_title, author, book_summary, book_cover = book_basic_info
        print(book_title, author, book_summary, book_cover)
        with open(basic_info_pickle_path, 'wb') as f:
            pickle.dump([book_title, author, book_summary, book_cover], f)
            print(f'[Milestone]: save {basic_info_pickle_path} done.')
    else:
        raise Exception(f'Fetch book_basic_info of {book_id} failed.')

    book_content = crawl_book_content(book_catalog_url)
    if book_content:
        paginated_content_dict, image_dict = book_content
        with open(content_dict_pickle_path, 'wb') as f:
            # TODO find why content has \r and \n characters
            pickle.dump(paginated_content_dict, f)
            print(f'[Milestone]: save {content_dict_pickle_path} done.')
        with open(image_dict_pickle_path, 'wb') as f:
            pickle.dump(image_dict, f)
            print(f'[Milestone]: save {image_dict_pickle_path} done.')
    else:
        raise Exception(f'Fetch book_content of {book_id} failed.')

    return book_basic_info, paginated_content_dict, image_dict


def prepare_ebook(book_basic_info, content_dict, image_dict, has_illustration=True, divide_volume=False):
    print(f'[Config]: has_illustration: {has_illustration}; divide_volume: {divide_volume}')

    book_title, author, book_summary, book_cover = book_basic_info
    cover_file = image_download_folder + '/' + '-'.join(book_cover.split('/')[-4:])

    # divide_volume(2) x download_image(2) = 4 choices
    if has_illustration:
        # handle all image stuff
        create_folder_if_not_exists(image_download_folder)
        image_list = extract_image_list(image_dict)
        image_list.append(book_cover)
        download_images(image_list)

        if not divide_volume:
            write_epub(book_title, author, content_dict, 'cover', cover_file, image_download_folder,
                       has_illustration=True, divide_volume=False)
        else:
            create_folder_if_not_exists(f'{book_title}')
            for volume in content_dict:
                write_epub(f'{book_title}_{volume}', author, content_dict[volume], 'cover', cover_file,
                           image_download_folder, book_title, has_illustration=True, divide_volume=True)

    if not has_illustration:
        create_folder_if_not_exists(image_download_folder)
        # download only book_cover
        download_images([book_cover])

        if not divide_volume:
            write_epub(book_title, author, content_dict, 'cover', cover_file, image_download_folder,
                       divide_volume=False, has_illustration=False)
        else:
            create_folder_if_not_exists(f'{book_title}')
            for volume in content_dict:
                write_epub(f'{book_title}_{volume}', author, content_dict[volume], 'cover', cover_file,
                           image_download_folder, book_title, divide_volume=True, has_illustration=False)


if __name__ == '__main__':
    #  The "freeze_support()" line can be omitted if the program is not going to be frozen to produce an executable.
    multiprocessing.freeze_support()

    # recover from last work.
    basic_info_pickle_path = f'pickle/{book_id}_basic_info.pickle'
    content_dict_pickle_path = f'pickle/{book_id}_content_dict.pickle'
    image_dict_pickle_path = f'pickle/{book_id}_image_dict.pickle'

    basic_info_pickle = Path(basic_info_pickle_path)
    content_dict_pickle = Path(content_dict_pickle_path)
    image_dict_pickle = Path(image_dict_pickle_path)

    book_basic_info = None
    paginated_content_dict = None
    image_dict = None

    if basic_info_pickle.exists() and content_dict_pickle.exists() and image_dict_pickle.exists():
        if Confirm.ask("The last unfinished work was detected, continue with your last job?"):
            with open(basic_info_pickle_path, 'rb') as f:
                book_basic_info = pickle.load(f)
            with open(content_dict_pickle_path, 'rb') as f:
                paginated_content_dict = pickle.load(f)
            with open(image_dict_pickle_path, 'rb') as f:
                image_dict = pickle.load(f)

        else:
            os.remove(basic_info_pickle_path)
            os.remove(content_dict_pickle_path)
            os.remove(image_dict_pickle_path)
            book_basic_info, paginated_content_dict, image_dict = fresh_crawl()
    else:
        book_basic_info, paginated_content_dict, image_dict = fresh_crawl()

    if book_basic_info and paginated_content_dict and image_dict:
        print(f'[INFO]: All the data of book(id={book_id}) is ready. Start making an ebook now.')
        prepare_ebook(book_basic_info, paginated_content_dict, image_dict,
                      has_illustration=has_illustration, divide_volume=divide_volume)

        # clean temporary files
        try:
            shutil.rmtree('file')
            os.remove(basic_info_pickle_path)
            os.remove(content_dict_pickle_path)
            os.remove(image_dict_pickle_path)
        except (Exception,) as e:
            pass

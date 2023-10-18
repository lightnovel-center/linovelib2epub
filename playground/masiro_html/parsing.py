from lxml import html

with open('./sample2.html', encoding='utf-8') as fp:
    content = fp.read()

page_body = html.fromstring(content)

XPATH_TITLE = '//div[@class="novel-title"]/text()'
XPATH_AUTHOR = '//div[@class="author"]/a/text()'
XPATH_TAG = '//div[@class="tags"]//a/span/text()'
# 这个表达式很麻烦
XPATH_INTRODUCTION = '//div[@class="brief"]/text() | //div[@class="brief"]/*/text()'
XPATH_COVER = '//img[@class="img img-thumbnail"]/@src'
# XPATH_EPISODE_UL = '//ul[@class="episode-ul"]//a/@href'

title = page_body.xpath(XPATH_TITLE)[0] if page_body.xpath(XPATH_TITLE) else ''
author = page_body.xpath(XPATH_AUTHOR)[0] if page_body.xpath(XPATH_AUTHOR) else ''
tags = page_body.xpath(XPATH_TAG) if page_body.xpath(XPATH_TAG) else ''
introduction = page_body.xpath(XPATH_INTRODUCTION) if page_body.xpath(XPATH_INTRODUCTION) else ''
cover_src = page_body.xpath(XPATH_COVER)[0] if page_body.xpath(XPATH_COVER) else ''
# episode_ul = page_body.xpath(XPATH_EPISODE_UL) if page_body.xpath(XPATH_EPISODE_UL) else ''

print(title)
print(author)
print(tags)
print(introduction)
print(cover_src)

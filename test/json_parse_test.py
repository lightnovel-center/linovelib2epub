import json

import demjson as demjson

str_1 = '''
{url_previous:'/novel/682/32706.html',url_next:'/novel/682/32708.html',url_index:'/novel/682/catalog',url_articleinfo:'/novel/682.html',url_image:'https://w.linovelib.com/files/article/image/0/682/682s.jpg',url_home:'https://w.linovelib.com/',articleid:'682',articlename:'黄昏色的咏使',subid:'/0',author:'细音启',chapterid:'32707',page:'1',chaptername:'第三卷 败者之王高唱阿玛迪斯之诗 回奏「我在那里看到的是——」',chapterisvip:'0',userid:'0',readtime:'1661071648'}
'''
# json_loads = json.loads(str_1)
# print(json_loads)
# json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 2 column 2 (char 2)

demjson_decode = demjson.decode(str_1)
print(demjson_decode)
# it works

rs = eval(str_1, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
print(rs)

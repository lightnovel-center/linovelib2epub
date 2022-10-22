import re

href_1 = '/novel/682/117086.html'
href_2 = 'javascript: cid(0)'
href_3 = 'https://w.linovelib.com/novel/682/117077.html'
reg = "\S+/novel/\d+/\S+\.html"
re_match_1 = bool(re.match(reg, href_1))
re_match_2 = bool(re.match(reg, href_2))
re_match_3 = bool(re.match(reg, href_3))
print(re_match_1, re_match_2, re_match_3)

str_2 = 'https://w.linovelib.com/novel/682/32792.html'
split = str_2.split('/')
print(split[-1][:-5])

img = '''<img border="0" class="imagecontent" src="https://img.linovelib.com/3/3211/163938/193293.jpg"/>'''
src_value = re.search(r"(?<=src=\").*?(?=\")", str(img))
print(src_value.group())

img_url = 'https://img.linovelib.com/3/3211/163938/193293.jpg'
img_url_2 = 'https://img.linovelib.com/3/3211/16938/193293.bmp'
img_url_3 = 'https://img.linovelib.com/3/321/16338/193293.jpeg'
img_url_4 = 'https://img.linovelib.com/3/3211/16393/19293.png'
image_pattern = r"^https?://(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpe?g|gif|png|webp|bmp|svg)$"
rs = bool(re.match(image_pattern, img_url))
rs_2 = bool(re.match(image_pattern, img_url_2))
rs_3 = bool(re.match(image_pattern, img_url_3))
rs_4 = bool(re.match(image_pattern, img_url_4))
print(rs,rs_2,rs_3,rs_4)

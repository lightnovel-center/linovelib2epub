import re

href_1 = '/novel/682/117086.html'
href_2 = 'javascript: cid(0)'
reg = "/novel/\d+/\d+\.html"
re_match_1 = bool(re.match(reg, href_1))
re_match_2 = bool(re.match(reg, href_2))
print(re_match_1,re_match_2)
import requests

headers = {
    # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    # 'Referer': 'https://w.linovelib.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46'
}

# Accept:
# image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8

# Accept-Encoding:
# gzip, deflate, br

# Accept-Language:
# zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6

img_path= "https://img3.readpai.com/3/3279/167340/196667.jpg"
# page = "https://w.linovelib.com/novel/3279.html"

resp = requests.get(img_path, headers=headers, )
# print(resp.text)
print(resp.status_code)

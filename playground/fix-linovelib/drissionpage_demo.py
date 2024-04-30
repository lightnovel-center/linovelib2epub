from DrissionPage import ChromiumPage

# https://blog.nashtechglobal.com/mastering-cloudflare-captcha-bypass-in-automation/

page = ChromiumPage()

url = 'https://www.bilinovel.com/novel/1030/42006.html'

resp = page.get(url)

print(resp)

# work

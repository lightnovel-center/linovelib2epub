from DrissionPage import ChromiumPage

# https://blog.nashtechglobal.com/mastering-cloudflare-captcha-bypass-in-automation/

page = ChromiumPage()

challenge_url2 = 'https://nowsecure.nl'

resp = page.get(challenge_url2)

print(resp)

# work


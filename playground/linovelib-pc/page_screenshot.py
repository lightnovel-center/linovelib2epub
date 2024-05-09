import io
import time

import pytesseract
from DrissionPage import ChromiumPage
from PIL import Image

page = ChromiumPage()
# has font-obfuscation
# url = 'https://www.linovelib.com/novel/2356/83547_6.html'
url = 'https://www.linovelib.com/novel/2356/83547_2.html'
# no font obfuscation
# url = 'https://www.linovelib.com/novel/2356/83547_3.html'
page.set.load_mode.eager()
time1 = time.perf_counter()
resp = page.get(url)
time2 = time.perf_counter()
print(f'elapsed: {time2 - time1}')
js_check = """
const last_p = document.querySelector('#TextContent p:last-of-type')
const p_style = window.getComputedStyle(last_p)
const p_font_style = p_style.getPropertyValue('font-family')
if (p_font_style && p_font_style.includes('read')) {
    return true;
}
return false;
"""
has_font_obfuscation = page.run_js(js_check)
if has_font_obfuscation:
    print('Has font obfuscation.')
    last_p = page.ele('css:#TextContent p:last-of-type')
    print(last_p)

    print(last_p.text.encode('utf-8'))
    # utf16
    print(last_p.text.encode('unicode-escape'))

    # save artifacts if in debug mode
    # '诲。'
    # last_p.get_screenshot()
    # refer doc: https://www.drissionpage.cn/ChromiumPage/screen/#%EF%B8%8F%EF%B8%8F-%EF%B8%8F%EF%B8%8F-%E5%85%83%E7%B4%A0%E6%88%AA%E5%9B%BE
    bytes_str = last_p.get_screenshot(as_bytes='png')  # 返回截图二进制文本 `

    image = Image.open(io.BytesIO(bytes_str))
    text = pytesseract.image_to_string(image, lang='chi_sim+eng')

    # remove all white-spaces and line-break on each side
    new_text = text.replace(" ", "").strip()
    # https://www.drissionpage.cn/ChromiumPage/ele_operation/#%EF%B8%8F%EF%B8%8F-%E4%BF%AE%E6%94%B9%E5%85%83%E7%B4%A0
    # patch this html by new_text
    last_p.set.innerHTML(new_text)
else:
    print('No font obfuscation.')

div = page.ele('#TextContent').text
print(div)

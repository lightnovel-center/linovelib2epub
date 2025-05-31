import pytesseract
from PIL import Image

# Open the PNG image
# image_path = './p.jpg'
image_path = './sample/sample2.png'
image = Image.open(image_path)

print(pytesseract.get_languages())
# ['chi_sim', 'chi_tra', 'eng', 'enm', 'equ', 'osd']

# Perform OCR on the image
text = pytesseract.image_to_string(image, lang='chi_sim+eng')

# strip white space characters
new_text = text.replace(" ", "")
# Print the extracted text
print(new_text)

# sample1
# 这里出现了错误，[嘲] 应当是 [嗯]
# 品尝完第一口,纱雪幸福洋溢地[嘲~|了一声。

# sample2
# 破折号识别错误。识别成了 [一一]
# 看着同一部电影、交换感想、一同欢笑一一要是今后也能继续谱出这种属于情侣的平凡幸福,
# 真是件何其美妙的事。
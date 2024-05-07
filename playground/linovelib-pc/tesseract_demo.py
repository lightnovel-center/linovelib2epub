import pytesseract
from PIL import Image

# Open the PNG image
image_path = './p.jpg'
image = Image.open(image_path)

print(pytesseract.get_languages())
# ['chi_sim', 'chi_tra', 'eng', 'enm', 'equ', 'osd']

# Perform OCR on the image
text = pytesseract.image_to_string(image, lang='chi_sim+eng')

# strip white space characters
new_text = text.replace(" ", "")
# Print the extracted text
print(new_text)

from PIL import Image, ImageDraw, ImageFont, ImageOps

class MyObject:
    def __init__(self, url, screenshot, ocr_text, final_text):
        self.url = url
        self.screenshot = screenshot  # 假设这是一个Pillow图像对象
        self.ocr_text = ocr_text
        self.final_text = final_text

    def create_combined_image(self, output_filename):
        # 定义图像的宽度和高度
        combined_width = max(self.screenshot.width, 1400)  # 确保宽度足够
        combined_height = self.screenshot.height + 200  # 高度为截图高度加200像素

        # 创建一个新的空白图像
        combined_image = Image.new('RGB', (combined_width, combined_height), color='white')
        draw = ImageDraw.Draw(combined_image)

        # 绘制截图
        combined_image.paste(self.screenshot, (0, 0))

        # 绘制文本
        # 使用微软雅黑字体
        try:
            font = ImageFont.truetype("C:\\Windows\\Fonts\\msyh.ttc", 20)
        except IOError:
            font = ImageFont.load_default()  # 如果字体加载失败，则使用默认字体
        draw.text((10, self.screenshot.height + 10), f"URL: {self.url}", fill="black", font=font)
        draw.text((10, self.screenshot.height + 40), f"OCR 文本: {self.ocr_text}", fill="black", font=font)
        draw.text((10, self.screenshot.height + 70), f"最终文本: {self.final_text}", fill="black", font=font)

        # add border
        # top, right, bottom, left
        border = (1, 1, 1, 1)
        new_img = ImageOps.expand(combined_image, border=border, fill='gray')

        # 保存拼合后的图像
        new_img.save(output_filename)

# 创建一个示例图像
screenshot_image = Image.new('RGB', (1400, 200), color='blue')  # 创建一个蓝色的400x200像素图像

# 创建对象
my_obj = MyObject(
    url='https://example.com',
    screenshot=screenshot_image,
    ocr_text='这是OCR提取的文本,很长很长的文字就是我',
    final_text='这是最终文本，只能到喀什市返回喀什分行'
)

# 保存拼合后的图像
my_obj.create_combined_image('combined_image.png')

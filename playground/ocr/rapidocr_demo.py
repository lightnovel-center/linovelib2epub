import sys

from rapidocr import RapidOCR

import paddle
print(paddle.utils.run_check())

import onnxruntime as ort
print(ort.get_device())  # 检查 ONNX Runtime 的设备
# CPU

# sys.exit(0)

engine = RapidOCR()

img_url = "./sample/img3.png"
result = engine(img_url)
print(result)
print(result.txts)

result.vis("output/rapidocr/vis_result_img3.jpg")

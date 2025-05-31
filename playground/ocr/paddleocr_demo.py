import pathlib

from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_angle_cls=False,  # 替代 use_doc_orientation_classify
    det_db_unclip_ratio=1.5,  # 2.10.0 关键参数
    rec_algorithm='CRNN',  # 2.10.0 默认算法
    # lang="en"  # 显式指定语言
)

# 执行 OCR 推理（2.10.0 的 predict 用法）
# filepath = "./sample/sample1.png"
# filepath = "./sample/sample2.png"
filepath = "./sample/sample3.png"
# filepath = "./sample/img3.png"
filename = pathlib.Path(filepath).stem
result = ocr.ocr(filepath, cls=False)  # cls=False 表示禁用方向分类


def save(filepath, result):
    import json
    output_data = [
        {
            "text": line[1][0],
            "confidence": float(line[1][1]),
            "position": [[float(x), float(y)] for x, y in line[0]]
        }
        for res in result for line in res
    ]
    with open(filepath, mode='w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)


if result is not None:
    for idx, res in enumerate(result):
        print(f"--- 第 {idx + 1} 个检测区域 ---")
        for line in res:
            print(f"文本: {line[1][0]}, 置信度: {line[1][1]:.2f}, 位置: {line[0]}")

    save(f"output/paddleocr/{filename}.json", result)
else:
    print("未检测到任何文本！")

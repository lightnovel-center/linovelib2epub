import re

def remove_comments(js_code):
    # 使用正则表达式匹配和替换注释
    pattern = r"/\*[\s\S]*?\*/|//.*?$"
    cleaned_code = re.sub(pattern, "", js_code, flags=re.MULTILINE)
    return cleaned_code

# 读取原始 JavaScript 文件
original_js = 'tw.readtool.js'
with open(original_js, 'r', encoding='utf-8') as file:
    original_code = file.read()

# 去除注释后的 JavaScript 代码
cleaned_code = remove_comments(original_code)

# 将去除注释后的代码写入新文件
with open('cleaned.js', 'w', encoding='utf-8') as file:
    file.write(cleaned_code)

print("Comments removed and saved to 'cleaned.js'")

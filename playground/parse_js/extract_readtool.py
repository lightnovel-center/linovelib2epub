import esprima

# 读取原始 JavaScript 文件
original_js = 'cleaned.js'
with open(original_js, 'r', encoding='utf-8') as file:
    original_code = file.read()

ast = esprima.parse(original_code)


def extract_contentid(ast) -> str:
    try:
        properties = ast.body[0].declarations[0].init.properties
        iterator = filter(lambda x: x.key.name == 'contentid', properties)
        list = [item for item in iterator]
        contentid_val = list[0].value.value
        return contentid_val
    except:
        # fallback
        return 'acontent1'


extract_contentid(ast)

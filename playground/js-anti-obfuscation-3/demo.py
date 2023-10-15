import re


def read_file(path):
    with open(path, encoding='utf-8') as fp:
        return fp.read()


# content = read_file('hm-key-parts.js')
content = read_file('hm.js')
decoded_s = content.encode('utf-8').decode('unicode_escape')
# print(decoded_s)

# var fOvlc1 = window["document"]['getElementById']('ccacontent')['innerHTML'];
pattern_content_id = r"window\[\"document\"\]\[\'getElementById']\(\'(.+?)\'\)"
match = re.search(pattern_content_id, decoded_s)

content_id = ""
if match:
    content_id = match[1]
    print(content_id)

pattern = r"\"RegExp\"]\([\'|\"]([^\"]+?)[\"|\'],\s*[\'|\"]gi[\'|\"]\),\s*[\'|\"]([^\"]+?)[\"|\']"
matches = re.findall(pattern, decoded_s)

replace_rules = {}
for match in matches:
    key = match[0]
    value = match[1]
    replace_rules[key] = value

print(replace_rules)

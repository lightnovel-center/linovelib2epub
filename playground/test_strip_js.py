import re


text1 = """<body>before <script src="http://path/to"></script> some text</body>"""
text2 = """<body>before <script>zation();</script>asdf</body>"""

new_text_1 = re.sub(r'<script.+?</script>', '', text1, flags=re.DOTALL)
new_text_2 = re.sub(r'<script.+?</script>', '', text2, flags=re.DOTALL)
print(new_text_1)
print(new_text_2)


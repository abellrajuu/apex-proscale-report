import sys
import re

html_file = 'templates/belt_scale.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

pattern_short = r'(<input type="text" name="short_check" id="short_check".*?)(>)'
content = re.sub(pattern_short, r'\1 value="Checked and found ok"\2', content)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("Injected short_check default")

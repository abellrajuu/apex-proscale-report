import re
html = open('templates/belt_scale.html', encoding='utf-8').read()
match = re.search(r'<div style="display: flex; justify-content: flex-end; align-items: center; gap: 12px;">.*?</div>\s*</form>', html, flags=re.DOTALL)
print(match is not None)

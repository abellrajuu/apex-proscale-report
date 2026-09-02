import re
html = open('templates/belt_scale.html', encoding='utf-8').read()
match = re.search(r'<div class="wizard-progress-bar".*?</div>\s*</div>', html, flags=re.DOTALL)
if match:
    print(match.group(0))

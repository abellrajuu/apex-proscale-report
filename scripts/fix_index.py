import re
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

pattern = r'<!-- WIZARD STEPPER -->\s*<div class="stepper-bar".*?</div>\s*</div>'
html = re.sub(pattern, '', html, flags=re.DOTALL)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Cleaned up index.html")

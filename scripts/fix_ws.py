import re
with open('templates/weighing_system.html', 'r', encoding='utf-8') as f:
    html = f.read()

pattern = r'<!-- WIZARD STEPPER -->\s*<div class="stepper-bar".*?</div>\s*</div>'
html = re.sub(pattern, '', html, flags=re.DOTALL)

with open('templates/weighing_system.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Cleaned up weighing_system.html")

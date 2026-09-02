import re
with open('templates/belt_scale.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the injected wizard-progress-bar
pattern = r'<div class="wizard-progress-bar".*?</div>\s*</div>'
html = re.sub(pattern, '', html, flags=re.DOTALL)

with open('templates/belt_scale.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Removed wizard progress bar from belt_scale.html")

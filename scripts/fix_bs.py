import re
with open('templates/belt_scale.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the injected stepper bar
pattern = r'<!-- WIZARD STEPPER -->\s*<div class="stepper-bar".*?</div>\s*</div>'
html = re.sub(pattern, '', html, flags=re.DOTALL)

with open('templates/belt_scale.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Removed injected stepper from belt_scale.html")

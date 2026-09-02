import re
with open('templates/belt_scale.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the original stepper bar
html = re.sub(r'<!-- STEP PROGRESS BAR -->.*?</div>\s*<form', '<form', html, flags=re.DOTALL)

# Remove the wizard actions div but keep the buttons inside
html = re.sub(r'<div class="wizard-actions".*?>\s*<button type="button" class="btn-wizard-prev".*?</button>\s*<div style="display: flex; gap: 12px;">', '<div style="display: flex; gap: 12px; margin-top: 24px;">', html, flags=re.DOTALL)

with open('templates/belt_scale.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Removed stepper from belt_scale.html")

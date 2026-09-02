import glob
import re
import os

# 1. Fix style.css
css_path = 'static/css/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()
css = re.sub(r'form:has\(\.stepper-bar\)\s*\.section-box\s*\{\s*display:\s*none;\s*\}', '', css)
css = re.sub(r'form:has\(\.stepper-bar\)\s*\.section-box\.active\s*\{\s*display:\s*block;\s*\}', '', css)
with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

# 2. Fix templates
for filepath in glob.glob('templates/*.html'):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Remove stepper bar
    html = re.sub(r'<div class="stepper-bar".*?</div>\s*</div>\s*</div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<div class="stepper-bar".*?</div>', '', html, flags=re.DOTALL)
    
    # Remove progress bar
    html = re.sub(r'<div class="wizard-progress-bar".*?</div>\s*</div>', '', html, flags=re.DOTALL)
    
    # Fix buttons: Make Submit visible, remove Next/Prev
    html = html.replace('id="btnSubmitPDF" class="btn-primary" style="display: none;', 'id="btnSubmitPDF" class="btn-primary" style="display: inline-flex;')
    html = re.sub(r'<button type="button" id="btnPrevStep".*?</button>', '', html, flags=re.DOTALL)
    html = re.sub(r'<button type="button" id="btnNextStep".*?</button>', '', html, flags=re.DOTALL)
    
    # Also fix belt_scale if it has btn-wizard-next
    html = html.replace('onclick="goToStep(2)"', '')
    html = html.replace('onclick="goToStep(3)"', '')
    html = html.replace('onclick="goToStep(4)"', '')
    html = html.replace('onclick="goToStep(5)"', '')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

print("De-wizardified templates and CSS.")

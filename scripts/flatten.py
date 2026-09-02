import glob
import re

html_files = glob.glob('templates/*.html')
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Remove stepper bar
    html = re.sub(r'<!-- WIZARD STEPPER -->.*?<div class="wizard-progress-bar".*?</div>\s*</div>', '', html, flags=re.DOTALL)

    # Hide Prev/Next
    html = html.replace('id="btnPrevStep" class="btn-secondary"', 'id="btnPrevStep" class="btn-secondary" style="display: none;"')
    html = html.replace('id="btnNextStep" class="btn-primary"', 'id="btnNextStep" class="btn-primary" style="display: none;"')
    
    # Show Submit
    html = html.replace('id="btnSubmitPDF" class="btn-primary" style="display: none;', 'id="btnSubmitPDF" class="btn-primary" style="display: inline-flex;')
    html = html.replace('id="btnSubmitForm" class="btn-primary" style="display: none;', 'id="btnSubmitForm" class="btn-primary" style="display: inline-flex;')
    
    # In belt_scale.html which has inline buttons:
    html = re.sub(r'<div class="wizard-actions".*?</div>', '', html, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
print("Flattened wizards in all HTML files.")

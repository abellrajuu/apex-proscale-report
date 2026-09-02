import os
import glob
import re

html_files = glob.glob('templates/*.html')
skip_files = ['crane_scale.html', 'portal.html', 'login.html', 'index.html', 'admin_users.html', 'layout.html']

for filepath in html_files:
    filename = os.path.basename(filepath)
    if filename in skip_files:
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
        
    if 'class="step-panel"' in html:
        continue
        
    sections = re.findall(r'<div class="section-box"', html)
    total = len(sections)
    if total <= 1:
        continue
        
    print(f"Converting {filename} ({total} sections)...")
    
    # 1. Inject app.js at the end
    if 'app.js' not in html:
        html = html.replace('</body>', '    <script src="/static/js/app.js"></script>\n</body>')
        
    # 2. Add stepper bar right after <form id="recordForm">
    stepper_html = '''
                <!-- WIZARD STEPPER -->
                <div class="stepper-bar" style="display: flex; gap: 8px; margin-bottom: 24px; overflow-x: auto; flex-wrap: nowrap; padding-bottom: 8px;">
'''
    for i in range(1, total + 1):
        active = ' active' if i == 1 else ''
        stepper_html += f'                    <div class="step-indicator{active}" data-step="{i}">Step {i}</div>\n'
    
    stepper_html += '''                </div>
                <div class="wizard-progress-bar" style="height: 6px; background: #334155; border-radius: 4px; margin-bottom: 32px; overflow: hidden;">
                    <div id="wizardProgressFill" style="height: 100%; width: ''' + str(100/total) + '''%; background: linear-gradient(90deg, #0ea5e9, #38bdf8); transition: width 0.3s ease;"></div>
                </div>
'''
    html = re.sub(r'(<form id="recordForm"[^>]*>)', r'\1' + stepper_html, html, count=1)
    
    # 3. Change form actions to wizard buttons
    form_actions_replacement = '''
                        <button type="button" id="btnPrevStep" class="btn-secondary" style="visibility: hidden;"><i class="fa-solid fa-arrow-left"></i> Previous Step</button>
                        <div style="display: flex; justify-content: flex-end; align-items: center; gap: 12px;">
                            <button type="button" id="btnNextStep" class="btn-primary">Next Step <i class="fa-solid fa-arrow-right"></i></button>
                            <button type="button" id="btnPreviewForm" class="btn-secondary" style="padding: 14px 24px; font-size: 15px; border-radius: 12px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.2); color: #f8fafc; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; font-weight: 600; transition: all 0.2s;"><i class="fa-solid fa-eye" style="color: #38bdf8;"></i> Preview PDF</button>
                            <button type="submit" id="btnSubmitPDF" class="btn-primary" style="display: none; padding: 14px 28px; font-size: 15px; border-radius: 12px; box-shadow: 0 6px 18px rgba(2, 132, 199, 0.3);">
                                <i class="fa-solid fa-file-pdf"></i> Submit & Generate Report
                            </button>
                        </div>'''
    
    # We replace the content of the div that contains btnPreviewForm and btnSubmitForm
    html = re.sub(r'<div style="display: flex; justify-content: flex-end.*?</div>\s*</div>\s*</form>', form_actions_replacement + '\n                    </div>\n                </form>', html, flags=re.DOTALL)
    
    # Wait, the buttons are wrapped in a div? Yes.
    
    # 4. Wrap sections in step-panels!
    # Because we don't know where the closing div is, we can just do a split!
    parts = html.split('<div class="section-box"')
    new_html = parts[0]
    
    for i in range(1, len(parts)):
        active = ' active' if i == 1 else ''
        # The closing div for step-panel needs to go AT THE END of parts[i]
        # BUT parts[i] might contain the form-actions at the very end (for the last section).
        # We need to split parts[i] if it has the form-actions, or just close it before the next section box!
        
        # Actually, wait. We can just close the step-panel right before the NEXT split!
        # What about the LAST split? It goes until </form>.
        # Let's use a regex instead: replace <div class="section-box" with <div class="step-panel..."><div class="section-box"
        # And where does it close? We can't easily.
        pass

    # Easier strategy: modify app.js to just use .section-box as the step panels!!
    print(f"Skipping wrapping for {filename}, we will modify app.js instead!")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

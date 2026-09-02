import glob
import re
import os

skip_files = ['crane_scale.html', 'portal.html', 'login.html', 'index.html', 'admin_users.html', 'layout.html', 'weighing_system.html']

form_actions_replacement = '''
                    <div class="form-actions" style="margin-top: 32px; display: flex; gap: 16px; justify-content: space-between; align-items: center; background: var(--card-bg); padding: 20px; border-radius: 12px; border: 1px solid var(--card-border);">
                        <button type="button" id="btnPrevStep" class="btn-secondary" style="visibility: hidden;"><i class="fa-solid fa-arrow-left"></i> Previous Step</button>
                        
                        <div style="display: flex; gap: 12px;">
                            <button type="button" id="btnNextStep" class="btn-primary">Next Step <i class="fa-solid fa-arrow-right"></i></button>
                            <button type="button" id="btnPreviewForm" class="btn-secondary" style="padding: 14px 24px; font-size: 15px; border-radius: 12px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.2); color: #f8fafc; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; font-weight: 600; transition: all 0.2s;"><i class="fa-solid fa-eye" style="color: #38bdf8;"></i> Preview PDF</button>
                            <button type="submit" id="btnSubmitPDF" class="btn-primary" style="display: none; padding: 14px 28px; font-size: 15px; border-radius: 12px; box-shadow: 0 6px 18px rgba(2, 132, 199, 0.3);">
                                <i class="fa-solid fa-file-pdf"></i> Submit & Generate Report
                            </button>
                        </div>
                    </div>'''

for filepath in glob.glob('templates/*.html'):
    filename = os.path.basename(filepath)
    if filename in skip_files:
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
        
    # Find the old form actions div:
    # <div style="display: flex; justify-content: flex-end; align-items: center; gap: 12px;"> ... </div>\s*</form>
    pattern = r'<div style="display: flex; justify-content: flex-end; align-items: center; gap: 12px;">.*?</div>\s*</form>'
    
    if re.search(pattern, html, flags=re.DOTALL):
        html = re.sub(pattern, form_actions_replacement + '\n                </form>', html, flags=re.DOTALL)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Fixed wizard buttons in {filename}")

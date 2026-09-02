import os
import glob
import re

tmpl_dir = r'C:\Users\abell\OneDrive\Desktop\TEST REPORT PRODUCTION final\templates'
results = []

for filepath in glob.glob(os.path.join(tmpl_dir, '*.html')):
    filename = os.path.basename(filepath)
    if filename in ['portal.html', 'admin_users.html', 'login.html']:
        continue
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    sec_boxes = len(re.findall(r'class="[^"]*section-box[^"]*"', content))
    inputs = len(re.findall(r'<(?:input|select|textarea)', content))

    has_hidden_css = '.section-box' in content and 'display: none' in content
    has_active_first = bool(re.search(r'class="section-box[^"]*active', content))

    results.append({
        'filename': filename,
        'boxes': sec_boxes,
        'inputs': inputs,
        'hidden_css': has_hidden_css,
        'active_first': has_active_first
    })

print("--- SYSTEM TEMPLATES DETAILED FORM FIELD AUDIT ---")
for r in results:
    needs_fix = (r['hidden_css'] and not r['active_first']) or (r['inputs'] < 4)
    status = "NEEDS FIX" if needs_fix else "OK"
    print(f"{r['filename']:<35} | Boxes: {r['boxes']:<2} | Inputs: {r['inputs']:<3} | HiddenCSS: {r['hidden_css']} | ActiveFirst: {r['active_first']} -> {status}")

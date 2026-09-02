import os
import glob
import re

tmpl_dir = r'C:\Users\abell\OneDrive\Desktop\TEST REPORT PRODUCTION final\templates'

for filepath in glob.glob(os.path.join(tmpl_dir, '*.html')):
    filename = os.path.basename(filepath)
    if filename in ['portal.html', 'admin_users.html', 'login.html']:
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # If the template does NOT use step-by-step wizard (or if section-box display:none causes issues), remove .section-box { display: none; }
    if 'active-step' not in content and 'step-panel' not in content:
        new_content = re.sub(r'\.section-box\s*\{\s*display:\s*none;\s*\}', '.section-box { display: block; }', content)
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Cleaned unused hidden CSS in {filename}!")

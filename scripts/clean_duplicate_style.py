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

    # Remove display: none; inside .section-box rules if section-box active-step is not used or if it causes hidden forms
    new_content = re.sub(r'(\.section-box\s*\{[^}]*?)display:\s*none;?', r'\1display: block;', content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Cleaned duplicate style in {filename}!")

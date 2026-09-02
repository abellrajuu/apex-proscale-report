import os
import glob
import re

tmpl_dir = r'C:\Users\abell\OneDrive\Desktop\TEST REPORT PRODUCTION final\templates'

for filepath in glob.glob(os.path.join(tmpl_dir, '*.html')):
    filename = os.path.basename(filepath)
    if filename in ['admin_users.html', 'login.html']:
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove loadHistory() calls and loadHistory function definition
    content_clean = re.sub(r'loadHistory\(\);?', '', content)
    content_clean = re.sub(r'async function loadHistory\(\)\s*\{[\s\S]*?\n\s*\}', '', content_clean)
    content_clean = re.sub(r'function loadHistory\(\)\s*\{[\s\S]*?\n\s*\}', '', content_clean)

    if content_clean != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content_clean)
        print(f"Cleaned JS history references in {filename}!")

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

    # Match glass-card containing historyTableBody or History Archive
    pattern = r'\s*(<!--\s*(?:History Archive|HISTORY ARCHIVE|Report Archive).*?-->\s*)?<div class="glass-card" style="margin-top:\s*28px;">[\s\S]*?historyTableBody[\s\S]*?</table>\s*</div>\s*</div>'

    new_content = re.sub(pattern, '', content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Completely purged Archive History table from {filename}!")

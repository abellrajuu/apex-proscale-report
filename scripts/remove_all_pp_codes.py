import os
import glob
import re

tmpl_dir = r'C:\Users\abell\OneDrive\Desktop\TEST REPORT PRODUCTION final\templates'

for filepath in glob.glob(os.path.join(tmpl_dir, '*.html')):
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex pattern to clean PP-05 codes and surrounding parentheses
    # Examples: (PP-05/11 Form), (PP-05/06), PP-05/18/A), (PP-05/08 CWS Form)
    new_content = re.sub(r'\s*\([^)]*PP-05[^)]*\)', '', content)
    new_content = re.sub(r'\s*PP-05/[^\)\s<]*\)?', '', new_content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Removed all PP-05 code references from {filename}!")

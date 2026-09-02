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

    new_content = content

    if filename == 'crane_scale.html':
        # Single-page layout requirement for CWS: force section-box display: block
        new_content = re.sub(r'\.section-box\s*\{\s*display:\s*none;\s*\}', '.section-box { display: block !important; }', new_content)
        new_content = re.sub(r'class="section-box"', 'class="section-box active-step"', new_content)
    else:
        # Multi-step wizard layout: ensure the first section box has active-step
        def replace_first(match):
            cls = match.group(1)
            if 'active-step' not in cls and 'active' not in cls:
                return f'class="{cls} active-step"'
            return match.group(0)

        # Replace only the first occurrence of class="section-box..."
        new_content = re.sub(r'class="([^"]*section-box[^"]*)"', replace_first, new_content, count=1)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed section box visibility in {filename}!")

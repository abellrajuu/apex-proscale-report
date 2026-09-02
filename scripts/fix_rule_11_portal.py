import re

portal_path = r'C:\Users\abell\OneDrive\Desktop\TEST REPORT PRODUCTION final\templates\portal.html'

with open(portal_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove all <span class="doc-badge">...</span> elements
content_fixed = re.sub(r'<span class="doc-badge">[\s\S]*?</span>', '', content)

# 2. Replace Generate PDF with Open System inside card action buttons
content_fixed = re.sub(r'<i class="fa-solid fa-file-pdf"></i>\s*Generate PDF', '<i class="fa-solid fa-folder-open"></i> Open System', content_fixed)

with open(portal_path, 'w', encoding='utf-8') as f:
    f.write(content_fixed)

print("Rule 11 cleanup complete on portal.html!")

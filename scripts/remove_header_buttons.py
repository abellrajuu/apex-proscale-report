import glob
import re

html_files = glob.glob('templates/*.html')
for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove online badge
    content = re.sub(r'<div class="header-badge header-badge-online">\s*Online\s*</div>', '', content)
    
    # Remove log out button
    content = re.sub(r'<a href="/logout" class="header-nav-link header-nav-logout">\s*<i class="fa-solid fa-power-off"></i> Log Out\s*</a>', '', content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
print("Removed Online and Log Out from all templates")

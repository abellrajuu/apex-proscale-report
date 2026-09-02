import glob
import re

html_files = glob.glob('templates/*.html')
for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = re.sub(r'<a href="/logout" class="mobile-nav-item">\s*<i class="fa-solid fa-power-off"></i>\s*<span>Log Out</span>\s*</a>', '', content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
print("Removed mobile Log Out from all templates")

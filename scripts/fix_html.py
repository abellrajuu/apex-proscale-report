import re

with open('templates/job_traveller_card.html', 'r', encoding='utf-8') as f:
    html = f.read()

pattern = r'<!-- 3\. ASSEMBLY STAGE -->\s*<div class=\"section-box\">.*?<!-- 4\. WIRING STAGE -->'
html = re.sub(pattern, '<!-- 4. WIRING STAGE -->', html, flags=re.DOTALL)

with open('templates/job_traveller_card.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated job_traveller_card.html")

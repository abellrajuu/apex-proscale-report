import re
html = open('templates/job_traveller_card.html', encoding='utf-8').read()
for match in re.findall(r'<div class="section-title">.*?</div>', html):
    print(match)

import sys
import re

html_file = 'templates/belt_scale.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove value="Kg/m" from act_4
content = content.replace('name="act_4" class="table-input" value="Kg/m"', 'name="act_4" class="table-input"')

# Remove value="m/s" from act_5
content = content.replace('name="act_5" class="table-input" value="m/s"', 'name="act_5" class="table-input"')

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("Removed Kg/m and m/s from UI")

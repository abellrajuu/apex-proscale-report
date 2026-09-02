import sys

html_file = 'templates/belt_scale.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the bad defaults I added
content = content.replace('name="spec_3" class="table-input" value="Display and Keypad Functionality">', 'name="spec_3" class="table-input">')
content = content.replace('name="spec_6" class="table-input" value="Number of PF Contacts">', 'name="spec_6" class="table-input">')
content = content.replace('name="spec_7" class="table-input" value="Communication Output">', 'name="spec_7" class="table-input">')
content = content.replace('name="spec_8" class="table-input" value="Analog Output">', 'name="spec_8" class="table-input">')
content = content.replace('name="spec_9" class="table-input" value="Wiring, TB and Component Layout">', 'name="spec_9" class="table-input">')

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("Reverted HTML defaults")

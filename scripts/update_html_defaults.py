import sys

html_file = 'templates/belt_scale.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add value="Display and Keypad Functionality" to spec_3
content = content.replace('name="spec_3" class="table-input">', 'name="spec_3" class="table-input" value="Display and Keypad Functionality">')

# Add value="Number of PF Contacts" to spec_6
content = content.replace('name="spec_6" class="table-input">', 'name="spec_6" class="table-input" value="Number of PF Contacts">')

# Add value="Communication Output" to spec_7
content = content.replace('name="spec_7" class="table-input">', 'name="spec_7" class="table-input" value="Communication Output">')

# Add value="Analog Output" to spec_8
content = content.replace('name="spec_8" class="table-input">', 'name="spec_8" class="table-input" value="Analog Output">')

# spec_9 is already "Wiring, TB" in old, but they want "Wiring, TB and Component Layout"
content = content.replace('name="spec_9" class="table-input">', 'name="spec_9" class="table-input" value="Wiring, TB and Component Layout">')


with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated HTML defaults")

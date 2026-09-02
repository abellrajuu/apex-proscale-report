import sys
import re

html_file = 'templates/belt_scale.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

def set_val(name, val):
    global content
    # Find the input tag for this name and add/replace value attribute
    pattern = rf'(<input type="text" name="{name}" class="table-input")((?:(?!value=).)*?)(>)'
    
    if val:
        # replace it with value="val"
        replacement = rf'\1\2 value="{val}"\3'
        content = re.sub(pattern, replacement, content)
    
set_val('spec_1', '230V')
set_val('act_1', '230V')

set_val('spec_2', '24V')
set_val('act_2', '24V')

set_val('spec_3', 'OK')
set_val('act_3', 'OK')

set_val('spec_4', '5.00 mV')
set_val('act_4', 'Kg/m')

set_val('spec_5', '23.87 HZ')
set_val('act_5', 'm/s')

set_val('spec_6', '4')
set_val('act_6', '4')

set_val('spec_7', 'RS-485')
set_val('act_7', 'RS-485')

set_val('spec_8', '4-20mA')
set_val('act_8', '4-20mA')

set_val('spec_9', 'OK')
set_val('act_9', 'OK')

# Also short_check
# <input type="text" name="short_check" id="short_check" class="table-input" style="max-width: 300px;">
pattern_short = r'(<input type="text" name="short_check" id="short_check" class="table-input".*?)(>)'
content = re.sub(pattern_short, r'\1 value="Checked and found ok"\2', content)


with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("Injected actual defaults")

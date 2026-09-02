import sys
import re

html_file = 'templates/belt_scale.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the dumb generic overwrites with specific ones!
bad_code = """                document.querySelectorAll('input[name^="act_"]').forEach(el => el.value = "OK");
                document.querySelectorAll('input[name^="spec_"]').forEach(el => el.value = "As per Spec");"""

good_code = """                document.getElementById('spec_1').value = '230V';
                document.getElementById('act_1').value = '230V';
                document.getElementById('spec_2').value = '24V';
                document.getElementById('act_2').value = '24V';
                document.getElementById('spec_3').value = 'OK';
                document.getElementById('act_3').value = 'OK';
                document.getElementById('spec_4').value = '5.00 mV';
                document.getElementById('spec_5').value = '23.87 HZ';
                document.getElementById('spec_6').value = '4';
                document.getElementById('act_6').value = '4';
                document.getElementById('spec_7').value = 'RS-485';
                document.getElementById('act_7').value = 'RS-485';
                document.getElementById('spec_8').value = '4-20mA';
                document.getElementById('act_8').value = '4-20mA';
                document.getElementById('spec_9').value = 'OK';
                document.getElementById('act_9').value = 'OK';"""

if bad_code in content:
    content = content.replace(bad_code, good_code)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced dummy data generation with exact values!")
else:
    print("Could not find bad code!")

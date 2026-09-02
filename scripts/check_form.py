import re
html = open('templates/acc_charge.html', encoding='utf-8').read()
match = re.search(r'<div class="stepper-bar".*?</form>', html, flags=re.DOTALL)
if match:
    print(match.group(0)[-1500:])

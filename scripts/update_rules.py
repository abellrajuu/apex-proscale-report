with open('RULES.md', 'r', encoding='utf-8') as f:
    rules = f.read()

new_rule = '''
### 6. Reference Material & Screenshots
- **User Reference Images:** Any screenshots or image mockups provided by the user must be saved in the `SCREENSHOTS/` directory within the network drive (`\\\\192.168.100.248\\prdndata\\ABEL\\SOFTWARE BUGS\\TEST REPORT\\SCREENSHOTS`) for future reference and documentation tracking.
- **Naming Convention:** Use clear, descriptive names for the saved images (e.g., TRAVLLER CARD DEMO.png).
'''

if '6. Reference Material & Screenshots' not in rules:
    rules += '\n' + new_rule
    with open('RULES.md', 'w', encoding='utf-8') as f:
        f.write(rules)
    print("RULES.md updated.")

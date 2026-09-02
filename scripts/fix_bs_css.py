import re
with open('templates/belt_scale.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'\.section-box\s*\{\s*background: #ffffff;.*?display: none;\s*\}', r'.section-box {\n            background: #ffffff;\n            border: 1.5px solid #e2e8f0;\n            border-radius: 18px;\n            padding: 28px 24px;\n            margin-bottom: 24px;\n            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);\n            display: block;\n        }', html, flags=re.DOTALL)

with open('templates/belt_scale.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Fixed belt_scale.html CSS")

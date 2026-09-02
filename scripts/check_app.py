with open('static/js/app.js', 'r', encoding='utf-8') as f:
    appjs = f.read()
lines = appjs.split('\n')
for i, line in enumerate(lines):
    if 'stepPanels' in line or 'section-box' in line:
        print(f"{i}: {line}")

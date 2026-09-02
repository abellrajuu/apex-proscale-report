lines = open('static/js/app.js', encoding='utf-8').readlines()
for i, line in enumerate(lines):
    if '$' + '{' in line and '' not in line:
        print(str(i) + ': ' + line.strip())

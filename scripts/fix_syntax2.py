import re
with open('static/js/app.js', 'r', encoding='utf-8') as f:
    appjs = f.read()

appjs = re.sub(r'fetch\(\$\{getServerBaseUrl\(\)\}/api/submit', r'fetch(${getServerBaseUrl()}/api/submit', appjs)

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(appjs)
print("Regex replace done.")

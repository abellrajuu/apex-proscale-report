with open('static/js/app.js', 'r', encoding='utf-8') as f:
    appjs = f.read()

appjs = appjs.replace('const res = await fetch(/api/submit, {', 'const res = await fetch(${getServerBaseUrl()}/api/submit, {')

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(appjs)
print("Fixed syntax error in app.js")

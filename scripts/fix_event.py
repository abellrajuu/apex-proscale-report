with open('static/js/app.js', 'r', encoding='utf-8') as f:
    appjs = f.read()

appjs = appjs.replace('e.preventDefault();\n            const btnPrev', 'e.preventDefault();\n            e.stopImmediatePropagation();\n            const btnPrev')

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(appjs)

with open('static/js/app.js', 'r', encoding='utf-8') as f:
    appjs = f.read()

appjs = appjs.replace('extractGridData ? extractGridData() : []', 'typeof extractGridData === "function" ? extractGridData() : []')
appjs = appjs.replace('extractRoutineTests ? extractRoutineTests() : []', 'typeof extractRoutineTests === "function" ? extractRoutineTests() : []')

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(appjs)

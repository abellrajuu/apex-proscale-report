with open('static/js/app.js', 'r', encoding='utf-8') as f:
    appjs = f.read()

# Find the end of goToStep function or just insert it after the definitions
insertion = '''

    // INITIALIZE WIZARD ON PAGE LOAD
    if (stepPanels.length > 0) {
        goToStep(1);
    }
'''

# We will put it right before the btnNextStep listener
appjs = appjs.replace('if (btnNextStep) {', insertion + '\n    if (btnNextStep) {')

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(appjs)
print("Added goToStep(1) on load")

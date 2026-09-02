with open('static/js/app.js', 'r', encoding='utf-8') as f:
    appjs = f.read()

# Replace hardcoded totalSteps
appjs = appjs.replace('const totalSteps = 5;', 'const totalSteps = stepPanels.length > 0 ? stepPanels.length : 1;')
appjs = appjs.replace('const stepPanels = document.querySelectorAll(\'.step-panel\').length > 0 ? document.querySelectorAll(\'.step-panel\') : document.querySelectorAll(\'.section-box\');', '')

# Move stepPanels declaration to the top
new_vars = '''
    const stepPanels = document.querySelectorAll('.step-panel').length > 0 ? document.querySelectorAll('.step-panel') : document.querySelectorAll('.section-box');
    const totalSteps = stepPanels.length > 0 ? stepPanels.length : 1;
'''
appjs = appjs.replace('let currentStep = 1;', new_vars + '\n    let currentStep = 1;')

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(appjs)
print("Fixed totalSteps in app.js")

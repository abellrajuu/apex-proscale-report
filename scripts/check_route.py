import re
with open('app.py', 'r', encoding='utf-8') as f:
    app_py = f.read()
print('belt-scale in app.py?', 'belt-scale' in app_py)

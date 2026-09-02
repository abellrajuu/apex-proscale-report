import glob
for f in glob.glob('templates/*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'app.js' not in content and '</body>' in content:
        content = content.replace('</body>', '    <script src="/static/js/app.js"></script>\n</body>')
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Injected app.js into {f}")

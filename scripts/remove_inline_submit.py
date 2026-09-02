import glob, re
for f in glob.glob('templates/*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content, n = re.subn(r'(document\.getElementById\(\'recordForm\'\)\?\.addEventListener\(\'submit\', async \(e\) => \{.*?\n            \}\);)', r'/* \1 */', content, flags=re.DOTALL)
    
    if n > 0:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Removed inline submit from {f}")

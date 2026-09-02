import glob, re
for f in glob.glob('templates/*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # We will just comment out the event listener for btnPreviewForm
    content, n = re.subn(r'(document\.getElementById\(\'btnPreviewForm\'\)\?\.addEventListener\(\'click\', async \(\) => \{.*?\n            \}\);)', r'/* \1 */', content, flags=re.DOTALL)
    
    if n > 0:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Removed inline preview from {f}")

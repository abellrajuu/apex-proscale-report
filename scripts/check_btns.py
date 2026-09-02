import glob
for f in glob.glob('templates/*.html'):
    html = open(f, encoding='utf-8').read()
    if 'id="btnSubmitPDF"' in html:
        idx = html.find('id="btnSubmitPDF"')
        print(f, html[idx-20:idx+60].replace('\n', ' '))

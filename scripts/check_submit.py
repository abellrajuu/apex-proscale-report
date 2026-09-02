html = open('templates/belt_scale.html', encoding='utf-8').read()
idx = html.find('btnSubmitForm')
if idx != -1:
    print(html[idx-100:idx+200])

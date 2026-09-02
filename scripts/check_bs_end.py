html = open('templates/belt_scale.html', encoding='utf-8').read()
idx = html.find('</form>')
print(html[idx-1000:idx+7])

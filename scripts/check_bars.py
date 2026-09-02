html = open('templates/belt_scale.html', encoding='utf-8').read()
idx = 0
while True:
    idx = html.find('stepper-bar', idx)
    if idx == -1: break
    print(html[idx-50:idx+150])
    idx += 1

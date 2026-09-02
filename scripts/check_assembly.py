html = open('templates/job_traveller_card.html', encoding='utf-8').read()
idx = html.find('ASSEMBLY')
if idx != -1:
    print(html[max(0, idx-500):idx+500])

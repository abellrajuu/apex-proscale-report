html = open('templates/belt_scale.html', encoding='utf-8').read()
if 'goToStep(' in html:
    print("WARNING: goToStep still in HTML")
else:
    print("goToStep removed from HTML")
    
if 'btn-wizard-next' in html:
    print("btn-wizard-next still present")

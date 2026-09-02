import re
html = open('templates/weighing_system.html', encoding='utf-8').read()
match = re.search(r'</form>', html)
if match:
    start = max(0, match.start() - 1000)
    print(html[start:match.end()])

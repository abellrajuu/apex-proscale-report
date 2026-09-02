
with open("static/js/app.js", "r", encoding="utf-8") as f:
    text = f.read()

target = "const res = await fetch(${getServerBaseUrl()}/api/submit, {"
replacement = "const res = await fetch(`${getServerBaseUrl()}/api/submit`, {"

text = text.replace(target, replacement)

with open("static/js/app.js", "w", encoding="utf-8") as f:
    f.write(text)


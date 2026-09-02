import sys

html_file = 'templates/belt_scale.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

target = """                            <div class="input-group"><label>Conveyor No.</label><input type="text" name="conveyor_no"
                                    id="conveyor_no"></div>"""

replacement = """                            <div class="input-group"><label>Conveyor No.</label><input type="text" name="conveyor_no"
                                    id="conveyor_no"></div>
                            <div class="input-group"><label>Version</label><input type="text" name="version"
                                    id="version"></div>"""

if target in content:
    content = content.replace(target, replacement)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added Version to HTML")
else:
    print("Target not found")

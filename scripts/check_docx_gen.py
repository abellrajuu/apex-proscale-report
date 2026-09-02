import re
with open('docx_generator.bak', 'r', encoding='utf-8') as f:
    code = f.read()
    match = re.search(r'def replace_text_in_runs.*?def ', code, flags=re.DOTALL)
    if match: print(match.group(0)[:1500])

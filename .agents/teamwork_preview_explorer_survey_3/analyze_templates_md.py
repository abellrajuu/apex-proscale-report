import json

with open(r"C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\.agents\teamwork_preview_explorer_survey_3\detailed_templates_dump.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for fname, d in data.items():
    print(f"### Template: `{fname}`")
    print(f"- **System Key**: `{d['key']}`")
    print(f"- **Paragraphs**: {d['paragraphs_count']}, **Tables**: {d['tables_count']}")
    
    # Analyze Header / Key text
    header_lines = [p['text'] for p in d['paragraphs'] if p['text'].strip()]
    print(f"- **Header / Key Paragraphs**:")
    for hl in header_lines[:8]:
        print(f"  - `{hl}`")
        
    print(f"- **Tables Summary**:")
    for t in d['tables']:
        hdr = [c['text'].replace('\n', ' ') for c in t['rows'][0]['cells']] if t['rows'] else []
        print(f"  - Table {t['table_idx']}: {t['rows_count']} rows x {t['cols_count']} cols | Header: {hdr}")
    print()

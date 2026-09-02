import json

with open(r"C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\.agents\teamwork_preview_explorer_survey_3\detailed_templates_dump.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for fname, d in data.items():
    print("=" * 80)
    print(f"FILE: {fname}")
    print("ALL PARAGRAPHS:")
    for p in d['paragraphs']:
        if p['text'].strip():
            print(f"  P[{p['index']}]: {p['text']}")
    print("ALL TABLES:")
    for t in d['tables']:
        print(f"  Table[{t['table_idx']}] ({t['rows_count']}x{t['cols_count']}):")
        for r in t['rows']:
            c_str = " | ".join([c['text'].replace('\n', ' ') for c in r['cells']])
            print(f"    R[{r['row_idx']}]: {c_str}")

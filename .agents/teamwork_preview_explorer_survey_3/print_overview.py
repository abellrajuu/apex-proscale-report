import json

with open(r"C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\.agents\teamwork_preview_explorer_survey_3\detailed_templates_dump.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for fname, d in data.items():
    print("=" * 80)
    print(f"TEMPLATE: {fname} (key: {d['key']})")
    print(f"Total Paras: {d['paragraphs_count']}, Total Tables: {d['tables_count']}")
    
    print("PARAGRAPHS:")
    for p in d['paragraphs']:
        if p['text']:
            print(f"  P[{p['index']}]: {p['text']}")
            
    print("TABLES:")
    for t in d['tables']:
        print(f"  Table[{t['table_idx']}]: {t['rows_count']} rows x {t['cols_count']} cols")
        for r in t['rows']:
            # get text of all cells
            c_texts = [c['text'].replace('\n', ' | ') for c in r['cells']]
            print(f"    R[{r['row_idx']}]: {c_texts[:4]}")
            if len(c_texts) > 4:
                print(f"         more cols: {c_texts[4:8]}")

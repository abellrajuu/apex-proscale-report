import json

with open(r"C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\.agents\teamwork_preview_explorer_survey_1\template_breakdown.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    fname = item["filename"]
    p_len = len(item["paragraphs"])
    t_len = len(item["tables"])
    print(f"\n=======================================================")
    print(f"FILE: {fname}")
    print(f"Paragraphs: {p_len}, Tables: {t_len}")
    
    # Print key paragraph texts
    print("--- PARAGRAPHS ---")
    for p in item["paragraphs"][:10]:
        print(f"  [P{p['index']}]: {p['text']}")
    if p_len > 10:
        print(f"  ... (+{p_len - 10} more paragraphs)")
        
    print("--- TABLES ---")
    for t in item["tables"]:
        print(f"  Table {t['index']} ({t['shape']}):")
        for r_i, r in enumerate(t["rows"][:4]):
            short_r = [c.replace('\n', ' ')[:30] for c in r]
            print(f"    R{r_i}: {short_r}")
        if len(t["rows"]) > 4:
            print(f"    ... (+{len(t['rows']) - 4} more rows)")

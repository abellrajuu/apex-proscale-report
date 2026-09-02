import json

with open(r".agents\teamwork_preview_explorer_survey_2\template_dump.json", encoding="utf-8") as f:
    data = json.load(f)

with open(r".agents\teamwork_preview_explorer_survey_2\template_analysis.txt", "w", encoding="utf-8") as out:
    out.write(f"Total files in dump: {len(data)}\n\n")

    for fname, d in sorted(data.items()):
        if fname.startswith("PP - 05 PRODUCTION"):
            continue
        out.write(f"### TEMPLATE: {fname}\n")
        out.write(f"Paragraphs count: {len(d['paragraphs'])}\n")
        for p in d["paragraphs"]:
            out.write(f"  [{p['index']}] {p['text']}\n")
        out.write(f"Tables count: {len(d['tables'])}\n")
        for ti, t in enumerate(d["tables"]):
            out.write(f"  Table {ti} ({t['rows_count']} rows x {t['cols_count']} cols):\n")
            for ri, row in enumerate(t["rows"]):
                cells_text = [c["text"].replace('\n', ' ') for c in row]
                out.write(f"    R{ri}: {' | '.join(cells_text[:5])}\n")
        out.write("\n" + "="*70 + "\n\n")

print("Done writing template_analysis.txt")

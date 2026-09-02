import json

with open(r"C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\.agents\teamwork_preview_explorer_survey_3\detailed_templates_dump.json", "r", encoding="utf-8") as f:
    data = json.load(f)

first_batch = [
    'PP-05_02 Job Traveller Card.docx',
    'PP-05_04 Batching System.docx',
    'PP-05_05 Remote Indicator.docx',
    'PP-05_06 Digital Indicator.docx',
    'PP-05_07 Weigh Feeder.docx',
    'PP-05_08 Crane Scale.docx',
    'PP-05_09 Signal Conditioner.docx',
    'PP-05_10 tRIP sAFE.docx',
    'PP-05_11 Vibration Switch.docx',
    'PP-05_12 ACC mV.docx'
]

for fname in first_batch:
    d = data[fname]
    print(f"### Template: `{fname}`")
    print(f"- **System Key**: `{d['key']}`")
    print(f"- **Paragraphs**: {d['paragraphs_count']}, **Tables**: {d['tables_count']}")
    
    header_lines = [p['text'] for p in d['paragraphs'] if p['text'].strip()]
    print(f"- **Header / Key Paragraphs**:")
    for hl in header_lines[:10]:
        print(f"  - `{hl}`")
        
    print(f"- **Tables Summary**:")
    for t in d['tables']:
        hdr = [c['text'].replace('\n', ' ') for c in t['rows'][0]['cells']] if t['rows'] else []
        print(f"  - Table {t['table_idx']}: {t['rows_count']} rows x {t['cols_count']} cols | Header: {hdr[:5]}")
    print()

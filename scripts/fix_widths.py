import docx
from docx.shared import Inches

doc = docx.Document('templates_docx/PP-05_03 Belt Scale.docx')

# Fix paragraph 9 wrapping
# Replace excessive spaces with tabs/fewer spaces
doc.paragraphs[9].text = "\tResolution: L: {{res_l}}\t\tS: {{res_s}}\t\tr: {{res_r}}\t\tt: {{res_t}}"
for r in doc.paragraphs[9].runs:
    r.bold = True
    r.font.size = docx.shared.Pt(10)

# Fix Table 3 widths
t = doc.tables[3]
t.autofit = True # Let MS Word auto-fit it to the window

# Manually force all cells in all rows to a smaller width so they don't spill
target_width = Inches(0.9)
for row in t.rows:
    for cell in row.cells:
        cell.width = target_width

doc.save('templates_docx/PP-05_03 Belt Scale.docx')
print("Fixed template widths and spaces!")

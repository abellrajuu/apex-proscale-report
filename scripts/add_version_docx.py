import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = docx.Document('templates_docx/PP-05_03 Belt Scale.docx')

# Find the paragraph containing "CONVEYOR NO"
insert_idx = -1
for i, p in enumerate(doc.paragraphs):
    if "CONVEYOR NO" in p.text:
        insert_idx = i
        break

if insert_idx != -1:
    # Insert a new paragraph below it
    new_p = doc.paragraphs[insert_idx].insert_paragraph_before("Version - {{version}}")
    new_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    # To insert AFTER, we actually insert before the NEXT paragraph
    # Let's move the text to the next paragraph's insert_before
    new_p.text = ""
    new_p = doc.paragraphs[insert_idx+1].insert_paragraph_before("Version - {{version}}")
    new_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    doc.save('templates_docx/PP-05_03 Belt Scale.docx')
    print("Added Version to DOCX")
else:
    print("Could not find CONVEYOR NO")

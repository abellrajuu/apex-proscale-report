import docx

doc = docx.Document('templates_docx/PP-05_03 Belt Scale.docx')

# Bold everything in the headers that were wiped
for idx in [3, 4, 5, 13, 16, 17]:
    for run in doc.paragraphs[idx].runs:
        run.bold = True
        run.font.size = docx.shared.Pt(10) # Set to typical size just in case

doc.save('templates_docx/PP-05_03 Belt Scale.docx')
print("Fixed bolding!")

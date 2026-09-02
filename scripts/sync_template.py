import docx

# Open the NEW template that the user provided
doc = docx.Document('LATEST TEMPLATE/PP-05_03 Belt Scale.docx')

# 1. Paragraphs (Headers, Footers, Info)
doc.paragraphs[3].text = "JOB No.\t: {{job_no}}\t\t\t\t\t\tCUSTOMER: {{customer}}"
doc.paragraphs[4].text = "CAPACITY\t: {{capacity}}\t\t                                                    CONVEYOR NO: {{conveyor_no}}"
doc.paragraphs[5].text = "                                                                                                                                        Version - {{version}}"
doc.paragraphs[9].text = "\tResolution: L: {{res_l}}                               S: {{res_s}}                                 r: {{res_r}}                                   t: {{res_t}}                        \t"
doc.paragraphs[13].text = "      Instrument Used: {{instrument_used}}\t\t\t\t\t\t\t\t                      \t\t   "
doc.paragraphs[16].text = "  Tested by: {{tested_by}}\t                                                       \t\t                         Approved by: {{approved_by}}    "
doc.paragraphs[17].text = "         Date: {{date}}\t\t\t\t\t\t\t\t\t(HOD - PDN)"

# 2. Table 0 (Equipment info)
t0 = doc.tables[0]
t0.cell(1, 0).text = "Model No. {{bs_model}}\n\nSerial No. {{bs_serial}}\n\nREMOTE:\nModel No. {{remote_model}}\nSerial No. {{remote_serial}}"
t0.cell(1, 1).text = "Model No. {{sensor_model}}\n\nSerial No.\n1) {{s1}}\n2) {{s2}}\n3) {{s3}}\n4) {{s4}}"
t0.cell(1, 2).text = "{{tacho_type}} Sensor\n\nModel No. {{tacho_model}}\n\nSerial No. {{tacho_serial}}"
t0.cell(1, 3).text = "Model No. {{jbox_model1}}\nSerial No. {{jbox_serial1}}\n\nModel No. {{jbox_model2}}\nSerial No. {{jbox_serial2}}"

# 3. Table 1 (Short Check)
t1 = doc.tables[1]
t1.cell(0, 0).text = "Check for short between Line & Neutral,\nNeutral & Earth , Line & Earth                   : {{short_check}}"

# 4. Table 2 (Test Performed Matrix)
t2 = doc.tables[2]
for i in range(1, 10):
    t2.cell(i, 2).text = f"{{{{spec_{i}}}}}"
    t2.cell(i, 3).text = f"{{{{act_{i}}}}}"

# 5. Table 3 (Calibration Data Matrix)
t3 = doc.tables[3]
# Row 0 is header, rows 1 through 11 are empty cells for g1_0 to g6_5
for r in range(1, 7):
    for c in range(6):
        t3.cell(r, c).text = f"{{{{g{r}_{c}}}}}"

# Save as the system's template!
doc.save('templates_docx/PP-05_03 Belt Scale.docx')
print("Successfully synced user's new template into the system!")

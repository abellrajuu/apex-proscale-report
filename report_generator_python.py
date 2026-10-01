import os
import sys
import docx
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from werkzeug.utils import secure_filename
import threading
import copy
from datetime import datetime
import math
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "backend_docx_templates")
EXPORTS_DIR = os.path.join(BASE_DIR, "backend_report_outputs")
os.makedirs(EXPORTS_DIR, exist_ok=True)

TEMPLATE_MAP = {
    "job_traveller_card": "PP-05_02 Job Traveller Card.docx",
    "belt_scale": "PP-05_03 Belt Scale.docx",
    "batching_system": "PP-05_04 Batching System.docx",
    "remote_indicator": "PP-05_05 Remote Indicator.docx",
    "digital_indicator": "PP-05_06 Digital Indicator - 4 LC Load.docx",
    "weigh_feeder": "PP-05_07 Weigh Feeder.docx",
    "crane_scale": "PP-05_08 Crane Scale.docx",
    "signal_conditioner": "PP-05_09 Signal Conditioner.docx",
    "trip_safe": "PP-05_10 tRIP sAFE.docx",
    "vibration_switch": "PP-05_11 Vibration Switch.docx",
    "acc_mv": "PP-05_12 ACC mV.docx",
    "acc_charge": "PP-05_13 ACC Charge.docx",
    "vibration_meter": "PP-05_14 Vibration Meter.docx",
    "charge_amplifier": "PP-05_15 Charge Amplifier.docx",
    "inprocess_register": "PP-05_16 Inprocess.docx",
    "inprocess": "PP-05_16 Inprocess.docx",
    "misc_report": "PP-05_17 Misc - Load Cell.docx",
    "misc": "PP-05_17 Misc - Load Cell.docx",
    "odd_system": "PP-05_18_A ODD System.docx",
    "dd_system": "PP-05_18_B DD System.docx",
    "work_instructions": "PP-05_19 Work Instructions.docx",
    "performance_index": "PP-05_20 Performance Index.docx",
    "performance_delay_analysis": "PP-05_21 Performance Delay Analysis.docx",
    "performance_delay": "PP-05_21 Performance Delay Analysis.docx",
    "equipment_list": "PP-05_22 Equipment List.docx",
    "loss_in_weigh_feeder": "PP-05_24 Loss in Weigh Feeder.docx",
}

def replace_in_paragraph(p, field_map):
    for key, val in field_map.items():
        placeholder = f"{{{{{key}}}}}"
        val_str = str(val) if val is not None else ""
        if placeholder in val_str:
            val_str = val_str.replace(placeholder, "")
        
        max_replacements = 50
        count = 0
        while count < max_replacements:
            count += 1
            t_elems = p._p.xpath('.//w:t')
            if not t_elems:
                break
                
            full_text = "".join(t.text for t in t_elems if t.text)
            if placeholder not in full_text:
                break
            
            char_mapping = []
            for t_idx, t in enumerate(t_elems):
                if t.text:
                    for char_idx in range(len(t.text)):
                        char_mapping.append((t_idx, char_idx))
                        
            start_idx = full_text.find(placeholder)
            end_idx = start_idx + len(placeholder) - 1
            
            if start_idx < 0 or start_idx >= len(char_mapping) or end_idx >= len(char_mapping):
                break
            
            start_t_idx, start_char_idx = char_mapping[start_idx]
            end_t_idx, end_char_idx = char_mapping[end_idx]
            
            for i in range(start_t_idx + 1, end_t_idx):
                t_elems[i].text = ""
                
            if start_t_idx == end_t_idx:
                r_text = t_elems[start_t_idx].text
                t_elems[start_t_idx].text = r_text[:start_char_idx] + val_str + r_text[end_char_idx + 1:]
            else:
                r_start = t_elems[start_t_idx].text
                t_elems[start_t_idx].text = r_start[:start_char_idx] + val_str
                r_end = t_elems[end_t_idx].text
                t_elems[end_t_idx].text = r_end[end_char_idx + 1:]

com_lock = threading.Lock()

def convert_docx_to_pdf(docx_path, pdf_path=None):
    if not pdf_path:
        pdf_path = docx_path.replace(".docx", ".pdf")
    
    with com_lock:
        word = None
        doc = None
        try:
            import pythoncom
            import win32com.client
            pythoncom.CoInitialize()
            word = win32com.client.DispatchEx("Word.Application")
            word.Visible = False
            word.DisplayAlerts = False
            try:
                word.ActivePrinter = 'Microsoft Print to PDF'
            except Exception:
                pass
            
            doc = word.Documents.Open(os.path.abspath(docx_path))
            doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17) # 17 = wdFormatPDF
        except Exception as e:
            print(f"[PDF CONVERT WARNING] MS Word COM conversion failed for {docx_path}: {e}")
            # Try docx2pdf if available as fallback
            try:
                from docx2pdf import convert
                convert(docx_path, pdf_path)
            except Exception as e2:
                print(f"[PDF CONVERT WARNING] Secondary fallback failed: {e2}")
        finally:
            if doc:
                try: doc.Close(0)
                except Exception: pass
            if word:
                try: word.Quit()
                except Exception: pass

    if not os.path.exists(pdf_path):
        print(f"[PDF CONVERT ERROR] PDF file was not created: {pdf_path}")
    return pdf_path

def clean_unhandled_tags(p):
    import re
    # Clear any remaining {{...}} tags to empty string
    max_clean = 50
    count = 0
    while count < max_clean:
        count += 1
        t_elems = p._p.xpath('.//w:t')
        if not t_elems:
            break
        full_text = "".join(t.text for t in t_elems if t.text)
        m = re.search(r'\{\{.*?\}\}', full_text)
        if not m:
            break
        placeholder = m.group(0)
        char_mapping = []
        for t_idx, t in enumerate(t_elems):
            if t.text:
                for char_idx in range(len(t.text)):
                    char_mapping.append((t_idx, char_idx))
        start_idx = full_text.find(placeholder)
        end_idx = start_idx + len(placeholder) - 1
        if start_idx < 0 or start_idx >= len(char_mapping) or end_idx >= len(char_mapping):
            break
        start_t_idx, start_char_idx = char_mapping[start_idx]
        end_t_idx, end_char_idx = char_mapping[end_idx]
        for i in range(start_t_idx + 1, end_t_idx):
            t_elems[i].text = ""
        if start_t_idx == end_t_idx:
            r_text = t_elems[start_t_idx].text
            t_elems[start_t_idx].text = r_text[:start_char_idx] + r_text[end_char_idx + 1:]
        else:
            r_start = t_elems[start_t_idx].text
            t_elems[start_t_idx].text = r_start[:start_char_idx]
            r_end = t_elems[end_t_idx].text
            t_elems[end_t_idx].text = r_end[end_char_idx + 1:]

def generate_digital_indicator_record(data, output_path):
    calib_mode = str(data.get("calib_mode", "mv")).lower().strip()
    lc_system = str(data.get("lc_system", "4")).lower().strip()
    raw_ao = str(data.get("num_outputs") or data.get("num_ao") or "").strip()
    raw_cur = str(data.get("current_output") or "").lower().strip()
    has_ao2 = any(str(data.get(f"g{r}_5_ao2") or "").strip() for r in range(1, 13))

    if raw_cur in ["no", "none", "0"] or raw_ao == "0":
        num_ao = "0"
        cur_out_enabled = False
    elif raw_ao == "2" or raw_cur in ["2", "2 ao", "2 outputs"] or has_ao2:
        num_ao = "2"
        cur_out_enabled = True
    else:
        num_ao = "1"
        cur_out_enabled = True

    # Determine template
    if "load" in calib_mode:
        is_load_calib = True
        if num_ao == "2":
            tmpl_name = "PP-05_06 Digital Indicator - 8 LC Load - 2 AO.docx" if lc_system == "8" else "PP-05_06 Digital Indicator - 4 LC Load - 2 AO.docx"
        else:
            tmpl_name = "PP-05_06 Digital Indicator - 8 LC Load.docx" if lc_system == "8" else "PP-05_06 Digital Indicator - 4 LC Load.docx"
    else:
        is_load_calib = False
        if num_ao == "2":
            tmpl_name = "PP-05_06 Digital Indicator - 8 LC mV - 2 AO.docx" if lc_system == "8" else "PP-05_06 Digital Indicator - 4 LC mV - 2 AO.docx"
        else:
            tmpl_name = "PP-05_06 Digital Indicator - 8 LC mV.docx" if lc_system == "8" else "PP-05_06 Digital Indicator - 4 LC mV.docx"

    master_path = os.path.join(TEMPLATES_DIR, tmpl_name)
    if not os.path.exists(master_path):
        doc_candidate = os.path.join(BASE_DIR, "DOC", tmpl_name)
        if os.path.exists(doc_candidate):
            master_path = doc_candidate
        else:
            raise FileNotFoundError(f"Template not found: {master_path}")

    doc = docx.Document(master_path)

    def get_val(*keys, default=""):
        for k in keys:
            v = data.get(k)
            if v is not None and str(v).strip():
                return str(v).strip()
        return default

    job_no = get_val("job_no", "job", default="")
    customer = get_val("customer", "customer_name", "cust", default="")
    capacity = get_val("capacity", "cap", default="")
    tag_no = get_val("conveyor_no", "tag_no", "conveyor_tag", default="")
    resolution = get_val("resolution", "res_l", default="")

    di_model = get_val("di_model", "bs_model", "model_no", default="")
    di_serial = get_val("di_serial", "bs_serial", "serial_no", default="")
    sw_version = get_val("sw_version", "bs_sw", "version", default="")

    lc_model = get_val("lc_model", "sensor_model", default="")
    s1 = get_val("s1", default="")
    s2 = get_val("s2", default="")
    s3 = get_val("s3", default="")
    s4 = get_val("s4", default="")
    s5 = get_val("s5", default="")
    s6 = get_val("s6", default="")
    s7 = get_val("s7", default="")
    s8 = get_val("s8", default="")

    remote_model = get_val("remote_model", "rm_model", default="")
    remote_serial = get_val("remote_serial", "rm_serial", default="")

    jbox_model = get_val("jbox_model", "jbox_model1", "jb_1_model", default="")
    jbox_serial = get_val("jbox_serial", "jbox_serial1", "jb_1_serial", default="")
    jbox2_model = get_val("jbox2_model", "jbox_model2", "jb_2_model", default="")
    jbox2_serial = get_val("jbox2_serial", "jbox_serial2", "jb_2_serial", default="")

    short_check = get_val("short_check", "test_voltage_chk", default="")

    def _set_para_with_tab(p, text_left, text_right, tab_pos_dxa, font_size_pt=10.5):
        from docx.oxml import parse_xml
        from docx.oxml.ns import nsdecls, qn
        p.text = f"{text_left}\t{text_right}"
        pPr = p._p.get_or_add_pPr()
        for old_tabs in pPr.findall(qn('w:tabs')):
            pPr.remove(old_tabs)
        tabs_xml = parse_xml(f'<w:tabs {nsdecls("w")}><w:tab w:val="left" w:pos="{tab_pos_dxa}"/></w:tabs>')
        pPr.append(tabs_xml)
        for r in p.runs:
            r.bold = True
            r.font.size = Pt(font_size_pt)

    # 1. Update Header Paragraphs
    for p in doc.paragraphs:
        txt = p.text
        if "SYSTEM  :" in txt or "SYSTEM:" in txt:
            p.text = "        SYSTEM  : DIGITAL INDICATOR"
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(10.5)
        elif "JOB No." in txt and "CUSTOMER NAME:" in txt:
            _set_para_with_tab(p, f"        JOB No.    : {job_no}", f"CUSTOMER NAME: {customer}", 5740, 10.5)
        elif "CAPACITY:" in txt and "TAG. NO:" in txt:
            cap_str = capacity
            if cap_str and not any(u in cap_str.upper() for u in ["KG", "TON"]):
                cap_str = f"{cap_str} Kg"
            _set_para_with_tab(p, f"        CAPACITY: {cap_str}", f"TAG. NO: {tag_no}", 5740, 10.5)
        elif "Resolution:" in txt:
            res_str = resolution if resolution else ""
            p.text = f"\tResolution: {res_str}" if res_str else "\tResolution: L: kg/T"
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(10.5)
        elif "REMARKS (If ANY):" in txt:
            remarks = get_val("remarks", default="")
            p.text = f"REMARKS (If ANY): - {remarks}"
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(10.5)
        elif "Instrument Used:" in txt:
            inst = get_val("instrument_used", default="")
            p.text = f"               Instrument Used: {inst}"
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(10.5)
        elif "Tested by:" in txt and "Approved by:" in txt:
            tb = get_val("tested_by", default="")
            ab = get_val("approved_by", default="")
            _set_para_with_tab(p, f"      Tested by: {tb}", f"Approved by: {ab}", 7240, 10.5)
            p.paragraph_format.space_after = Pt(14)
        elif "Date:" in txt and "(HOD" in txt:
            dt = get_val("date", default=datetime.now().strftime("%d-%b-%Y"))
            _set_para_with_tab(p, f"      Date: {dt}", "(HOD - PDN)", 7240, 10.5)

    # 2. Table 0 (Equipment Specs)
    if len(doc.tables) > 0:
        t0 = doc.tables[0]
        # Digital Indicator Cell
        t0.cell(1, 0).text = f"Model No: {di_model}\n\nSerial No: {di_serial}\n\nS/W Version: {sw_version}"
        for cp in t0.cell(1, 0).paragraphs:
            for r in cp.runs:
                r.font.size = Pt(10)

        # SENSOR Cell
        c1 = t0.cell(1, 1)
        if len(c1.paragraphs) >= 8:
            c1.paragraphs[1].text = f"Model No: {lc_model}" if lc_model else "Model No:"
            if c1.paragraphs[1].runs:
                c1.paragraphs[1].runs[0].font.size = Pt(10)
            c1.paragraphs[3].text = "Serial No:"
            if c1.paragraphs[3].runs:
                c1.paragraphs[3].runs[0].font.size = Pt(10)
            if lc_system == "8":
                pairs = [(s1, s5), (s2, s6), (s3, s7), (s4, s8)]
                for idx, (va, vb) in enumerate(pairs):
                    p_idx = 4 + idx
                    t_left = f"{idx+1}) {va}".strip() if va else f"{idx+1})"
                    t_right = f"{idx+5}) {vb}".strip() if vb else f"{idx+5})"
                    c1.paragraphs[p_idx].text = f"{t_left}\t{t_right}"
                    for r in c1.paragraphs[p_idx].runs:
                        r.font.size = Pt(9.5)
            else:
                singles = [s1, s2, s3, s4]
                for idx, va in enumerate(singles):
                    p_idx = 4 + idx
                    c1.paragraphs[p_idx].text = f"{idx+1}) {va}".strip() if va else f"{idx+1})"
                    for r in c1.paragraphs[p_idx].runs:
                        r.font.size = Pt(9.5)
        else:
            if lc_system == "8":
                c1.text = (
                    f"Model No: {lc_model}\n\nSerial No:\n"
                    f"1) {s1}\t5) {s5}\n"
                    f"2) {s2}\t6) {s6}\n"
                    f"3) {s3}\t7) {s7}\n"
                    f"4) {s4}\t8) {s8}"
                )
            else:
                c1.text = (
                    f"Model No: {lc_model}\n\nSerial No:\n"
                    f"1) {s1}\n2) {s2}\n3) {s3}\n4) {s4}"
                )
            for cp in c1.paragraphs:
                for r in cp.runs:
                    r.font.size = Pt(9.5)

        # REMOTE Cell
        rm_m = remote_model if remote_model else "N/A"
        rm_s = remote_serial if remote_serial else "N/A"
        t0.cell(1, 2).text = f"Model No: {rm_m}\n\nSerial No: {rm_s}"
        for cp in t0.cell(1, 2).paragraphs:
            for r in cp.runs:
                r.font.size = Pt(10)

        # JUNCTION BOX Cell (Supports dual junction boxes)
        jb1_m = jbox_model if jbox_model else "N/A"
        jb1_s = jbox_serial if jbox_serial else "N/A"
        jb2_m = jbox2_model if jbox2_model else ""
        jb2_s = jbox2_serial if jbox2_serial else ""

        c_jb = t0.cell(1, 3)
        if len(c_jb.paragraphs) >= 6:
            c_jb.paragraphs[1].text = f"Model No: {jb1_m}"
            c_jb.paragraphs[2].text = f"Serial No: {jb1_s}"
            c_jb.paragraphs[4].text = f"Model No: {jb2_m}" if jb2_m else ("Model No: N/A" if jb2_s else "Model No:")
            c_jb.paragraphs[5].text = f"Serial No: {jb2_s}" if jb2_s else ("Serial No: N/A" if jb2_m else "Serial No:")
            for p_idx in [1, 2, 4, 5]:
                for r in c_jb.paragraphs[p_idx].runs:
                    r.font.size = Pt(9.5)
        else:
            jb2_text = f"\n\nModel No: {jb2_m}\nSerial No: {jb2_s}" if (jb2_m or jb2_s) else ""
            c_jb.text = f"Model No: {jb1_m}\nSerial No: {jb1_s}{jb2_text}"
            for cp in c_jb.paragraphs:
                for r in cp.runs:
                    r.font.size = Pt(9.5)

    # 3. Table 1 (Short Check)
    if len(doc.tables) > 1:
        t1 = doc.tables[1]
        if short_check:
            short_display = "Checked & found OK" if ("ok" in short_check.lower() or "passed" in short_check.lower()) else short_check
        else:
            short_display = ""
        t1.cell(0, 0).text = f"Check for short between Line & Neutral , Neutral & Earth , Line & Earth                   : {short_display}"
        for cp in t1.cell(0, 0).paragraphs:
            for r in cp.runs:
                r.font.size = Pt(10)

    # 4. Table 2 (Routine Tests 1 to 5)
    if len(doc.tables) > 2:
        t2 = doc.tables[2]
        for row_i in range(1, 6):
            if row_i < len(t2.rows):
                spec_v = get_val(f"spec_{row_i}", default="")
                act_v = get_val(f"act_{row_i}", default="")
                t2.cell(row_i, 2).text = spec_v
                t2.cell(row_i, 3).text = act_v
                for col_idx in [2, 3]:
                    for cp in t2.cell(row_i, col_idx).paragraphs:
                        for r in cp.runs:
                            r.font.size = Pt(10)

    # 5. Table 3 (Calibration Matrix: 12 Rows)
    if len(doc.tables) > 3:
        t3 = doc.tables[3]
        grid_data = data.get("grid_data")
        
        if num_ao == "2":
            # 2 AO template has 2 header rows, data starts at index 2 (rows 2 to 13)
            for r_idx in range(1, 13):
                r_target = r_idx + 1 # 2 to 13
                if r_target < len(t3.rows):
                    row_cells = t3.rows[r_target].cells
                    
                    # Col 0: Load
                    v0 = get_val(f"g{r_idx}_0")
                    if not v0 and isinstance(grid_data, list) and r_idx <= len(grid_data):
                        row_arr = grid_data[r_idx - 1]
                        if isinstance(row_arr, list) and len(row_arr) > 0:
                            v0 = str(row_arr[0] or "")
                    if v0:
                        row_cells[0].text = v0
                    
                    # Col 1..4: LC1..LC4
                    for c_lc in range(1, 5):
                        v_lc = get_val(f"g{r_idx}_{c_lc}")
                        if not v_lc and isinstance(grid_data, list) and r_idx <= len(grid_data):
                            row_arr = grid_data[r_idx - 1]
                            if isinstance(row_arr, list) and len(row_arr) > c_lc:
                                v_lc = str(row_arr[c_lc] or "")
                        if v_lc:
                            row_cells[c_lc].text = v_lc
                    
                    # Col 5: AO1
                    v_ao1 = get_val(f"g{r_idx}_5_ao1", f"g{r_idx}_5")
                    if not v_ao1 and isinstance(grid_data, list) and r_idx <= len(grid_data):
                        row_arr = grid_data[r_idx - 1]
                        if isinstance(row_arr, list) and len(row_arr) > 5:
                            v_ao1 = str(row_arr[5] or "")
                    if v_ao1:
                        row_cells[5].text = v_ao1
                    
                    # Col 6: AO2
                    v_ao2 = get_val(f"g{r_idx}_5_ao2")
                    if not v_ao2 and isinstance(grid_data, list) and r_idx <= len(grid_data):
                        row_arr = grid_data[r_idx - 1]
                        if isinstance(row_arr, list) and len(row_arr) > 6:
                            v_ao2 = str(row_arr[6] or "")
                    if v_ao2:
                        row_cells[6].text = v_ao2
                    
                    # Col 7..10: LC5..LC8 (if lc_system == '8')
                    if lc_system == "8":
                        for idx_lc8, c_extra in enumerate(range(7, 11), start=6):
                            v_extra = get_val(f"g{r_idx}_{c_extra}", f"g{r_idx}_{idx_lc8}")
                            if not v_extra and isinstance(grid_data, list) and r_idx <= len(grid_data):
                                row_arr = grid_data[r_idx - 1]
                                if isinstance(row_arr, list) and len(row_arr) > c_extra:
                                    v_extra = str(row_arr[c_extra] or "")
                            if v_extra:
                                row_cells[c_extra].text = v_extra
                    else:
                        for c_extra in range(7, 11):
                            row_cells[c_extra].text = ""
                    
                    for col_idx in range(len(row_cells)):
                        for cp in row_cells[col_idx].paragraphs:
                            for r in cp.runs:
                                r.font.size = Pt(10)
        else:
            # 1 AO template (or current output NO) - data starts at row 1 (rows 1 to 12)
            for r_idx in range(1, 13):
                if r_idx < len(t3.rows):
                    row_cells = t3.rows[r_idx].cells
                    
                    # Col 0: Load
                    v0 = get_val(f"g{r_idx}_0")
                    if not v0 and isinstance(grid_data, list) and r_idx <= len(grid_data):
                        row_arr = grid_data[r_idx - 1]
                        if isinstance(row_arr, list) and len(row_arr) > 0:
                            v0 = str(row_arr[0] or "")
                    if v0:
                        row_cells[0].text = v0
                    
                    # Col 1..4: LC1..LC4
                    for c_lc in range(1, 5):
                        v_lc = get_val(f"g{r_idx}_{c_lc}")
                        if not v_lc and isinstance(grid_data, list) and r_idx <= len(grid_data):
                            row_arr = grid_data[r_idx - 1]
                            if isinstance(row_arr, list) and len(row_arr) > c_lc:
                                v_lc = str(row_arr[c_lc] or "")
                        if v_lc:
                            row_cells[c_lc].text = v_lc
                    
                    # Col 5: Current output mA (blank if current_output is 'no')
                    if cur_out_enabled:
                        v_ma = get_val(f"g{r_idx}_5_ao1", f"g{r_idx}_5")
                        if not v_ma and isinstance(grid_data, list) and r_idx <= len(grid_data):
                            row_arr = grid_data[r_idx - 1]
                            if isinstance(row_arr, list) and len(row_arr) > 5:
                                v_ma = str(row_arr[5] or "")
                        if v_ma:
                            row_cells[5].text = v_ma
                    else:
                        row_cells[5].text = ""
                    
                    # Col 6..9: LC5..LC8 (if lc_system == '8')
                    if lc_system == "8":
                        for c_extra in range(6, 10):
                            v_extra = get_val(f"g{r_idx}_{c_extra}")
                            if not v_extra and isinstance(grid_data, list) and r_idx <= len(grid_data):
                                row_arr = grid_data[r_idx - 1]
                                if isinstance(row_arr, list) and len(row_arr) > c_extra:
                                    v_extra = str(row_arr[c_extra] or "")
                            if v_extra:
                                row_cells[c_extra].text = v_extra
                    else:
                        for c_extra in range(6, 10):
                            row_cells[c_extra].text = ""
                    
                    for col_idx in range(len(row_cells)):
                        for cp in row_cells[col_idx].paragraphs:
                            for r in cp.runs:
                                r.font.size = Pt(10)

    # 6. Table 4 (Checklist 6 to 10)
    if len(doc.tables) > 4:
        t4 = doc.tables[4]
        for row_i in range(1, 6):
            if row_i < len(t4.rows):
                chk_v = get_val(f"check_{row_i + 5}", default="")
                if chk_v:
                    t4.cell(row_i, 2).text = chk_v

    # 7. Table 5 (SPAN, TARE, EXC V - Load Cell mode only)
    if is_load_calib and len(doc.tables) > 5:
        t5 = doc.tables[5]
        max_lc = 8 if lc_system == "8" else 4
        # Row 1: SPAN
        for lc_idx in range(1, max_lc + 1):
            if lc_idx < len(t5.columns):
                val_span = get_val(f"span_lc{lc_idx}", f"span_{lc_idx}", default="")
                if val_span:
                    t5.cell(1, lc_idx).text = val_span
        # Row 2: TARE
        for lc_idx in range(1, max_lc + 1):
            if lc_idx < len(t5.columns):
                val_tare = get_val(f"tare_lc{lc_idx}", f"tare_{lc_idx}", default="")
                if val_tare:
                    t5.cell(2, lc_idx).text = val_tare
        # Row 3: EXC V
        for lc_idx in range(1, max_lc + 1):
            if lc_idx < len(t5.columns):
                val_excv = get_val(f"excv_lc{lc_idx}", f"excv_{lc_idx}", default="")
                if val_excv:
                    t5.cell(3, lc_idx).text = val_excv

    # 8. Clean up excess empty spacer paragraphs and enforce clean page transition
    paras_to_remove = []
    # Remove empty spacer paragraphs between Table 3 and Table 4, and lock heading to Page 2
    for i, p in enumerate(doc.paragraphs):
        if "ROUTINE TEST RECORD" in p.text and i > 0:
            p.paragraph_format.page_break_before = True
            for k in range(i - 1, -1, -1):
                if not doc.paragraphs[k].text.strip():
                    paras_to_remove.append(doc.paragraphs[k])
            break

    # Remove extra empty spacer paragraphs before Instrument Used (between Table 5 and footer)
    empty_before_inst = []
    for i, p in enumerate(doc.paragraphs):
        if "Instrument Used" in p.text:
            for k in range(i - 1, -1, -1):
                if not doc.paragraphs[k].text.strip():
                    empty_before_inst.append(doc.paragraphs[k])
                    if len(empty_before_inst) >= 6:
                        break
            break

    for p in paras_to_remove + empty_before_inst:
        try:
            p._p.getparent().remove(p._p)
        except Exception:
            pass

    # Save to output path
    doc.save(output_path)

    # Convert to PDF
    convert_docx_to_pdf(output_path)
    return output_path

def generate_signal_conditioner_record(data, output_path):
    calib_type = str(data.get("calib_type") or data.get("calib_mode") or "mv").lower().strip()
    is_lc_calib = "load" in calib_type

    if is_lc_calib:
        tmpl_name = "PP-05_09 Signal Conditioner - Load Cell.docx"
    else:
        tmpl_name = "PP-05_09 Signal Conditioner.docx"

    master_path = os.path.join(TEMPLATES_DIR, tmpl_name)
    if not os.path.exists(master_path):
        raise FileNotFoundError(f"Template not found: {master_path}")

    doc = docx.Document(master_path)

    def get_val(*keys, default=""):
        for k in keys:
            v = data.get(k)
            if v is not None and str(v).strip():
                return str(v).strip()
        return default

    job_no = get_val("job_no", "job", default="")
    customer = get_val("customer", "customer_name", "cust", default="")
    sc_model = get_val("sc_model", "model_no", default="")
    sc_serial = get_val("sc_serial", "serial_no", default="")
    lc_model = get_val("lc_model", default="")
    lc_serial = get_val("lc_serial", default="")

    span = get_val("span", default="")
    tare = get_val("tare", default="")
    exc_v = get_val("exc_v", "excitation_voltage", default="")

    annunciation = get_val("annunciation", default="")
    pct_error = get_val("pct_error", "error_percent", default="")
    multimeter_used = get_val("multimeter_used", "multimeter", default="")
    tested_by = get_val("tested_by", "user_name", default="")
    approved_by = get_val("approved_by", default="")
    date_val = get_val("date", default="")
    if not date_val:
        date_val = datetime.now().strftime("%d-%b-%Y")

    def find_p(predicate):
        for p in doc.paragraphs:
            if predicate(p.text):
                return p
        return None

    def set_para_2col(p, label1, val1, label2, val2, tab1_pos=850, val1_pos=2400, tab2_pos=5102, val2_pos=6600, font_name='Arial', font_size=10):
        if not p: return
        p.text = ''
        pPr = p._p.get_or_add_pPr()
        existing_tabs = pPr.find(qn('w:tabs'))
        if existing_tabs is not None:
            pPr.remove(existing_tabs)
        tabs = OxmlElement('w:tabs')
        pPr.append(tabs)
        for pos in [tab1_pos, val1_pos, tab2_pos, val2_pos]:
            tab = OxmlElement('w:tab')
            tab.set(qn('w:val'), 'left')
            tab.set(qn('w:pos'), str(pos))
            tabs.append(tab)

        r = p.add_run('\t' + label1 + '\t')
        r.bold = True
        r.font.name = font_name
        r.font.size = Pt(font_size)

        r_v1 = p.add_run(val1 if val1 else '')
        r_v1.bold = False
        r_v1.font.name = font_name
        r_v1.font.size = Pt(font_size)

        r2 = p.add_run('\t' + label2 + '\t')
        r2.bold = True
        r2.font.name = font_name
        r2.font.size = Pt(font_size)

        r_v2 = p.add_run(val2 if val2 else '')
        r_v2.bold = False
        r_v2.font.name = font_name
        r_v2.font.size = Pt(font_size)

    def set_para_1col(p, label, val, tab1_pos=850, val_pos=2400, font_name='Arial', font_size=10):
        if not p: return
        p.text = ''
        pPr = p._p.get_or_add_pPr()
        existing_tabs = pPr.find(qn('w:tabs'))
        if existing_tabs is not None:
            pPr.remove(existing_tabs)
        tabs = OxmlElement('w:tabs')
        pPr.append(tabs)
        for pos in [tab1_pos, val_pos]:
            tab = OxmlElement('w:tab')
            tab.set(qn('w:val'), 'left')
            tab.set(qn('w:pos'), str(pos))
            tabs.append(tab)

        r = p.add_run('\t' + label + '\t')
        r.bold = True
        r.font.name = font_name
        r.font.size = Pt(font_size)

        r_v = p.add_run(val if val else '')
        r_v.bold = False
        r_v.font.name = font_name
        r_v.font.size = Pt(font_size)

    # Populate Metadata
    set_para_1col(find_p(lambda t: "job order no" in t.lower()), 'JOB ORDER No:', job_no)
    set_para_1col(find_p(lambda t: "customer:" in t.lower()), 'CUSTOMER:', customer)

    p_sc_lc = find_p(lambda t: "signal conditioner" in t.lower() and "load cell" in t.lower() and "test record" not in t.lower())
    if p_sc_lc:
        p_sc_lc.text = ''
        pPr = p_sc_lc._p.get_or_add_pPr()
        existing_tabs = pPr.find(qn('w:tabs'))
        if existing_tabs is not None:
            pPr.remove(existing_tabs)
        tabs = OxmlElement('w:tabs')
        pPr.append(tabs)
        for pos in [850, 5102]:
            tab = OxmlElement('w:tab')
            tab.set(qn('w:val'), 'left')
            tab.set(qn('w:pos'), str(pos))
            tabs.append(tab)
        r1 = p_sc_lc.add_run('\tSIGNAL CONDITIONER\tLOAD CELL')
        r1.bold = True
        r1.font.name = 'Arial'
        r1.font.size = Pt(10)

    set_para_2col(find_p(lambda t: "model no:" in t.lower()), 'MODEL NO:', sc_model, 'MODEL NO:', lc_model)
    set_para_2col(find_p(lambda t: "serial no:" in t.lower()), 'SERIAL NO:', sc_serial, 'SERIAL NO:', lc_serial)

    # Populate Linearity Table (Table 0)
    if doc.tables:
        t = doc.tables[0]
        for i in range(1, 7):
            if i < len(t.rows):
                in_val = get_val(f"cal_in_{i}", default="")
                out_val = get_val(f"cal_out_{i}", default="")
                if not in_val and isinstance(data.get("grid_data"), list) and i-1 < len(data["grid_data"]):
                    row_data = data["grid_data"][i-1]
                    if len(row_data) >= 2:
                        in_val = str(row_data[0])
                        out_val = str(row_data[1])

                row_cells = t.rows[i].cells
                row_cells[0].text = ''
                p0 = row_cells[0].paragraphs[0]
                p0.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
                r_sl = p0.add_run(str(i))
                r_sl.font.name = 'Arial'
                r_sl.font.size = Pt(9.5)

                row_cells[1].text = ''
                p1 = row_cells[1].paragraphs[0]
                p1.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
                r_in = p1.add_run(str(in_val))
                r_in.font.name = 'Arial'
                r_in.font.size = Pt(9.5)

                row_cells[2].text = ''
                p2 = row_cells[2].paragraphs[0]
                p2.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
                r_out = p2.add_run(str(out_val))
                r_out.font.name = 'Arial'
                r_out.font.size = Pt(9.5)

    # If Load Cell Calibration, populate Table 1 (SPAN, TARE, EXC V)
    if len(doc.tables) > 1 and is_lc_calib:
        t1 = doc.tables[1]
        def set_c(cell, val_text):
            cell.text = ''
            p = cell.paragraphs[0]
            p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val_text))
            r.font.name = 'Arial'
            r.font.size = Pt(9.5)

        if len(t1.rows) > 1:
            if len(t1.rows[1].cells) >= 3:
                set_c(t1.rows[1].cells[0], span)
                set_c(t1.rows[1].cells[1], tare)
                set_c(t1.rows[1].cells[2], exc_v)

    # Functional Checks & Multimeter
    set_para_1col(find_p(lambda t: "power on annunciation" in t.lower()), 'Check the POWER ON Annunciation:', annunciation, tab1_pos=850, val_pos=4200)
    set_para_1col(find_p(lambda t: "percentage of error" in t.lower()), 'Percentage of error:', pct_error, tab1_pos=850, val_pos=3000)
    set_para_1col(find_p(lambda t: "multimeter used" in t.lower()), 'Multimeter Used:', multimeter_used, tab1_pos=850, val_pos=3000)

    # Sign-Off
    set_para_2col(find_p(lambda t: "tested by:" in t.lower()), 'Tested by:', tested_by, 'Approved by:', approved_by, tab1_pos=850, val1_pos=2200, tab2_pos=5102, val2_pos=6400)
    set_para_2col(find_p(lambda t: "date:" in t.lower()), 'Date:', date_val, '(HOD - PDN)', '', tab1_pos=850, val1_pos=2200, tab2_pos=5102, val2_pos=6400)

    doc.save(output_path)
    convert_docx_to_pdf(output_path)
    return output_path

def generate_misc_record(data, output_path):
    category = str(data.get("misc_type") or data.get("misc_category") or "load_cell").lower().strip()

    if "load" in category:
        tmpl_name = "PP-05_17 Misc - Load Cell.docx"
        mode = "load_cell"
    elif "remote" in category or "display" in category:
        tmpl_name = "PP-05_17 Misc - Remote Display.docx"
        mode = "remote_display"
    elif "multiple" in category or "multi" in category:
        tmpl_name = "PP-05_17 Misc - Junction Box Multiple.docx"
        mode = "jb_multiple"
    elif "single" in category or "junction" in category or "jb" in category:
        tmpl_name = "PP-05_17 Misc - Junction Box Single.docx"
        mode = "jb_single"
    else:
        tmpl_name = "PP-05_17 Misc - General Blank.docx"
        mode = "general"

    master_path = os.path.join(TEMPLATES_DIR, tmpl_name)
    if not os.path.exists(master_path):
        raise FileNotFoundError(f"Template not found: {master_path}")

    doc = docx.Document(master_path)

    def get_val(*keys, default=""):
        for k in keys:
            v = data.get(k)
            if v is not None and str(v).strip():
                return str(v).strip()
        return default

    def set_para_tab(p, left_text, right_text, tab_pos=5800, font_size=10, bold_label=True):
        if not p: return
        p.text = f"{left_text}\t{right_text}"
        pPr = p._p.get_or_add_pPr()
        for old_tabs in pPr.findall(qn('w:tabs')):
            pPr.remove(old_tabs)
        from docx.oxml import parse_xml
        from docx.oxml.ns import nsdecls
        tabs_xml = parse_xml(f'<w:tabs {nsdecls("w")}><w:tab w:val="left" w:pos="{tab_pos}"/></w:tabs>')
        pPr.append(tabs_xml)
        for r in p.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(font_size)
            r.bold = bold_label

    job_no = get_val("job_no", "job", default="")
    customer = get_val("customer", "customer_name", "cust", default="")
    item_desc = get_val("item_desc", "item_description", default="")
    qty = get_val("qty", "quantity", default="")
    model_no = get_val("model_no", "model", default="")

    # Parse serial numbers
    raw_serials = data.get("serials") or data.get("serial_no") or data.get("serial") or ""
    if isinstance(raw_serials, list):
        serials_list = [str(s).strip() for s in raw_serials if str(s).strip()]
    else:
        serials_list = [s.strip() for s in str(raw_serials).replace('\n', ',').split(',') if s.strip()]

    serial_count = len(serials_list)
    serials_str = ", ".join(serials_list)

    # 1. Header Box (Table 0 Row 0 Cell 0)
    c0 = doc.tables[0].rows[0].cells[0]
    if mode == "jb_multiple":
        hdr_model = ""
        hdr_serial = ""
    elif mode in ["remote_display", "jb_single"]:
        hdr_model = model_no
        hdr_serial = serials_str if serial_count <= 3 else ""
    else:
        hdr_model = model_no
        hdr_serial = serials_str

    set_para_tab(c0.paragraphs[0], f"Job No: {job_no}", f"Model No: {hdr_model}", 5800, 10, True)
    set_para_tab(c0.paragraphs[1], f"Customer: {customer}", f"Sl. No: {hdr_serial}", 5800, 10, True)
    set_para_tab(c0.paragraphs[2], f"Item Description: {item_desc}", f"Qty: {qty}", 5800, 10, True)

    # 2. Body (Table 0 Row 1 Cell 0)
    c1 = doc.tables[0].rows[1].cells[0]
    tracking_no = get_val("tracking_no", "tracking_number", default="")

    if mode == "load_cell":
        # Tracking Number: If present, show heading; if empty, clear heading completely
        p_trk = c1.paragraphs[2] if len(c1.paragraphs) > 2 else None
        if p_trk:
            if tracking_no:
                p_trk.text = f"TRACKING NO: {tracking_no}"
                for r in p_trk.runs:
                    r.bold = True
                    r.font.name = 'Arial'
                    r.font.size = Pt(10)
            else:
                p_trk.text = ""

        # Populate Nested Table (Rows 1 to 4)
        if c1.tables:
            nt = c1.tables[0]
            for idx in range(1, 5):
                s = get_val(f"lc_serial_{idx}", default="")
                in_r = get_val(f"lc_in_res_{idx}", default="")
                out_r = get_val(f"lc_out_res_{idx}", default="")
                unb = get_val(f"lc_unbalance_{idx}", default="")
                if idx < len(nt.rows):
                    cells = nt.rows[idx].cells
                    row_vals = [str(idx), s, in_r, out_r, unb]
                    for ci, val in enumerate(row_vals):
                        cells[ci].text = val
                        p = cells[ci].paragraphs[0]
                        p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
                        if p.runs:
                            p.runs[0].font.name = 'Arial'
                            p.runs[0].font.size = Pt(9)

    elif mode == "remote_display":
        p_trk = c1.paragraphs[2] if len(c1.paragraphs) > 2 else None
        if p_trk:
            if tracking_no:
                p_trk.text = f"TRACKING NO: {tracking_no}"
                for r in p_trk.runs:
                    r.bold = True
                    r.font.name = 'Arial'
                    r.font.size = Pt(10)
            else:
                p_trk.text = ""

        p_sl = c1.paragraphs[4] if len(c1.paragraphs) > 4 else None
        if p_sl:
            p_sl.text = f"Sl. No: {serials_str}" if serial_count > 3 else ""
            for r in p_sl.runs:
                r.font.name = 'Arial'
                r.font.size = Pt(10)

        ind_model = get_val("indicator_model", "di_model", default="")
        p_comm = c1.paragraphs[9] if len(c1.paragraphs) > 9 else None
        if p_comm:
            rep = f"{ind_model} " if ind_model else ""
            p_comm.text = f"The above-mentioned items were checked for its communication (rs485) using {rep}indicator and was found ok"
            for r in p_comm.runs:
                r.font.name = 'Arial'
                r.font.size = Pt(10)

    elif mode == "jb_single":
        p_sl = c1.paragraphs[4] if len(c1.paragraphs) > 4 else None
        if p_sl:
            p_sl.text = f"Sl. No: {serials_str}" if serial_count > 3 else ""
            for r in p_sl.runs:
                r.font.name = 'Arial'
                r.font.size = Pt(10)

    elif mode == "jb_multiple":
        pairs = [(2, 3), (7, 8), (11, 12), (15, 16), (19, 20)]
        for i, (pm, ps) in enumerate(pairs, start=1):
            vm = get_val(f"variant_model_{i}", default="")
            vs = get_val(f"variant_serial_{i}", default="")
            vq = get_val(f"variant_qty_{i}", default="")
            if vm or vs or vq:
                set_para_tab(c1.paragraphs[pm], f"MODEL NO: {vm}", f"QTY: {vq}", 5800, 10, True)
                c1.paragraphs[ps].text = f"SL NO: {vs}"
                for r in c1.paragraphs[ps].runs:
                    r.font.name = 'Arial'
                    r.font.size = Pt(10)
            else:
                c1.paragraphs[pm].text = ""
                c1.paragraphs[ps].text = ""

    elif mode == "general":
        p_idx = 1
        for i in range(1, 15):
            lbl = get_val(f"entry_label_{i}", default="")
            val = get_val(f"entry_val_{i}", default="")
            if lbl or val:
                p = c1.paragraphs[p_idx] if p_idx < len(c1.paragraphs) else c1.add_paragraph()
                p.text = f"{lbl} : {val}"
                for r in p.runs:
                    r.font.name = 'Arial'
                    r.font.size = Pt(10)
                p_idx += 1
        while p_idx < len(c1.paragraphs):
            c1.paragraphs[p_idx].text = ""
            p_idx += 1

    # 3. Sign-off
    tested_by = get_val("tested_by", "user_name", default="")
    approved_by = get_val("approved_by", default="")
    date_val = get_val("date", default="") or datetime.now().strftime("%d-%b-%Y")

    set_para_tab(doc.paragraphs[3], f"Tested by: {tested_by}", f"Approved by: {approved_by}", 7200, 10, False)
    set_para_tab(doc.paragraphs[4], f"Date: {date_val}", "(HOD-PDN)", 7200, 10, False)

    doc.save(output_path)
    convert_docx_to_pdf(output_path)
    return output_path

def generate_docx_record(data, output_path):
    report_type = data.get("report_type", "belt_scale")
    if report_type == "digital_indicator":
        return generate_digital_indicator_record(data, output_path)
    if report_type == "signal_conditioner":
        return generate_signal_conditioner_record(data, output_path)
    if report_type in ["misc_report", "misc", "miscellaneous", "miscellaneous_items"]:
        return generate_misc_record(data, output_path)

    template_name = TEMPLATE_MAP.get(report_type)
    if report_type == "belt_scale":
        raw_ao = data.get("num_outputs")
        if raw_ao is not None and str(raw_ao).strip() in ["1", "2", "3"]:
            num_ao = str(raw_ao).strip()
        else:
            has_ao3 = any(str(data.get(f"g{r}_5_ao3") or "").strip() for r in range(1, 12))
            has_ao2 = any(str(data.get(f"g{r}_5_ao2") or "").strip() for r in range(1, 12))
            if has_ao3: num_ao = "3"
            elif has_ao2: num_ao = "2"
            else: num_ao = "1"

        lc_system = str(data.get("lc_system") or "").strip()
        if not lc_system:
            has_8lc = any(str(data.get(f"s{i}") or data.get(f"lc_s{i}") or "").strip() for i in range(5, 9))
            lc_system = "8" if has_8lc else "4"

        if lc_system == "8":
            if num_ao == "3":
                template_name = "PP-05_03 Belt Scale - 3 AO - 8 LC.docx"
            elif num_ao == "2":
                template_name = "PP-05_03 Belt Scale - 2 AO - 8 LC.docx"
            else:
                template_name = "PP-05_03 Belt Scale - 8 LC.docx"
        else:
            if num_ao == "3":
                template_name = "PP-05_03 Belt Scale - 3 AO.docx"
            elif num_ao == "2":
                template_name = "PP-05_03 Belt Scale - 2 AO.docx"
            else:
                template_name = "PP-05_03 Belt Scale.docx"

    if not template_name:
        raise ValueError(f"Unknown report type: {report_type}")

    template_path = os.path.join(TEMPLATES_DIR, template_name)
    if not os.path.exists(template_path):
        doc_dir_path = os.path.join(BASE_DIR, "DOC", template_name)
        if os.path.exists(doc_dir_path):
            template_path = doc_dir_path
        else:
            raise FileNotFoundError(f"Template not found: {template_path} (or {doc_dir_path})")

    doc = docx.Document(template_path)

    # Convert all None to empty strings to avoid 'None' printing
    field_map = {k: (v if v is not None else "") for k, v in data.items()}

    # Flatten routine_tests array into spec_1..9 and act_1..9 (only if non-empty)
    if isinstance(data.get("routine_tests"), list):
        for idx, item in enumerate(data["routine_tests"], start=1):
            if isinstance(item, dict):
                spec_v = item.get("spec")
                act_v = item.get("act") or item.get("actual")
                if spec_v is not None and str(spec_v).strip():
                    field_map[f"spec_{idx}"] = str(spec_v)
                if act_v is not None and str(act_v).strip():
                    field_map[f"act_{idx}"] = str(act_v)

    # Flatten grid_data array into g1_0..g11_5 (only if non-empty)
    if isinstance(data.get("grid_data"), list):
        for r_idx, row in enumerate(data["grid_data"], start=1):
            if isinstance(row, list):
                for c_idx, val in enumerate(row):
                    str_val = str(val) if val is not None else ""
                    if str_val.strip():
                        if report_type == 'belt_scale' and c_idx == 2:
                            import re
                            try:
                                g_speed = float(re.sub(r'[^0-9.]', '', str_val))
                                str_val = f"{g_speed:.2f}"
                            except Exception:
                                pass
                        field_map[f"g{r_idx}_{c_idx}"] = str_val
                        if c_idx == 5 and f"g{r_idx}_5_ao1" not in field_map:
                            field_map[f"g{r_idx}_5_ao1"] = str_val

    # Ensure aliasing for Column 5 if g{r}_5_ao1 was entered
    for r in range(1, 12):
        if not field_map.get(f"g{r}_5") and field_map.get(f"g{r}_5_ao1"):
            field_map[f"g{r}_5"] = field_map[f"g{r}_5_ao1"]

    # System-specific aliases & default fallbacks
    if report_type == 'belt_scale':
        def get_first(*keys):
            for k in keys:
                v = str(field_map.get(k) or data.get(k) or '').strip()
                if v:
                    return v
            return ''

        cust_val = get_first('customer', 'customer_name')
        field_map['customer'] = cust_val
        field_map['customer_name'] = cust_val

        bs_m_val = get_first('bs_model', 'model_no', 'belt_scale_model')
        field_map['bs_model'] = bs_m_val
        field_map['model_no'] = bs_m_val
        field_map['belt_scale_model'] = bs_m_val

        bs_s_val = get_first('bs_serial', 'serial_no', 'belt_scale_serial')
        field_map['bs_serial'] = bs_s_val
        field_map['serial_no'] = bs_s_val
        field_map['belt_scale_serial'] = bs_s_val

        sw_val = get_first('bs_sw', 'version', 'sw_version')
        field_map['bs_sw'] = sw_val
        field_map['version'] = sw_val

        rm_m_val = get_first('rm_model', 'remote_model')
        field_map['rm_model'] = rm_m_val
        field_map['remote_model'] = rm_m_val

        rm_s_val = get_first('rm_serial', 'remote_serial')
        field_map['rm_serial'] = rm_s_val
        field_map['remote_serial'] = rm_s_val

        lc_m_val = get_first('lc_model', 'sensor_model', 'load_cell_model')
        field_map['lc_model'] = lc_m_val
        field_map['sensor_model'] = lc_m_val

        # Support lc_serials list if passed
        lc_serials_arr = data.get('lc_serials') or field_map.get('lc_serials')
        if isinstance(lc_serials_arr, list):
            for i_lc, s_val in enumerate(lc_serials_arr, start=1):
                if i_lc <= 8:
                    field_map[f's{i_lc}'] = str(s_val).strip()

        for i_s in range(1, 9):
            field_map[f's{i_s}'] = get_first(f's{i_s}', f'lc_s{i_s}', f'lc_serial_{i_s}', f'sensor_s{i_s}')

        # Dynamic spacing calculation for 8-LC templates so right column stays aligned
        def format_8lc_line(num1, num2):
            val1 = field_map.get(f's{num1}', '').strip()
            val2 = field_map.get(f's{num2}', '').strip()
            left_str = f"{num1}) {val1}" if val1 else f"{num1})"
            right_str = f"{num2}) {val2}" if val2 else f"{num2})"
            gap_spaces = max(2, 21 - len(left_str) - len(right_str))
            return f"{left_str}{' ' * gap_spaces}{right_str}"

        field_map['lc_line_1'] = format_8lc_line(1, 5)
        field_map['lc_line_2'] = format_8lc_line(2, 6)
        field_map['lc_line_3'] = format_8lc_line(3, 7)
        field_map['lc_line_4'] = format_8lc_line(4, 8)

        ss_m_val = get_first('ss_model', 'tacho_model', 'speed_sensor_model')
        field_map['ss_model'] = ss_m_val
        field_map['tacho_model'] = ss_m_val

        ss_s_val = get_first('ss_serial', 'tacho_serial', 'speed_sensor_serial')
        field_map['ss_serial'] = ss_s_val
        field_map['tacho_serial'] = ss_s_val

        as_m_val = get_first('as_model', 'angle_sensor_model')
        field_map['as_model'] = as_m_val
        field_map['angle_sensor_model'] = as_m_val

        as_s_val = get_first('as_serial', 'angle_sensor_serial')
        field_map['as_serial'] = as_s_val
        field_map['angle_sensor_serial'] = as_s_val

        jb1_m_val = get_first('jb_1_model', 'jbox_model1')
        field_map['jb_1_model'] = jb1_m_val
        field_map['jbox_model1'] = jb1_m_val

        jb1_s_val = get_first('jb_1_serial', 'jbox_serial1')
        field_map['jb_1_serial'] = jb1_s_val
        field_map['jbox_serial1'] = jb1_s_val

        jb2_m_val = get_first('jb_2_model', 'jbox_model2')
        field_map['jb_2_model'] = jb2_m_val
        field_map['jbox_model2'] = jb2_m_val

        jb2_s_val = get_first('jb_2_serial', 'jbox_serial2')
        field_map['jb_2_serial'] = jb2_s_val
        field_map['jbox_serial2'] = jb2_s_val

        jb3_m_val = get_first('jb_3_model', 'jbox_model3')
        field_map['jb_3_model'] = jb3_m_val
        field_map['jbox_model3'] = jb3_m_val

        jb3_s_val = get_first('jb_3_serial', 'jbox_serial3')
        field_map['jb_3_serial'] = jb3_s_val
        field_map['jbox_serial3'] = jb3_s_val

        chk_val = get_first('test_voltage_chk', 'short_check')
        field_map['test_voltage_chk'] = chk_val
        field_map['short_check'] = chk_val
        
        # Ensure belt_speed fallback from tacho_belt_speed if missing
        if not field_map.get('belt_speed') and field_map.get('tacho_belt_speed'):
            field_map['belt_speed'] = field_map['tacho_belt_speed']

        # Format belt_speed to 2 decimal places if provided
        import re
        raw_speed_str = str(field_map.get('belt_speed') or '').strip()
        speed_val = 0.0
        if raw_speed_str:
            try:
                speed_val = float(re.sub(r'[^0-9.]', '', raw_speed_str))
                if 'm/s' not in raw_speed_str.lower():
                    field_map['belt_speed'] = f"{speed_val:.2f} m/s"
            except Exception:
                pass

        # Automatic Resolution calculation ONLY IF user entered capacity and speed
        raw_cap_str = str(field_map.get('capacity') or '').strip()
        if raw_cap_str and speed_val > 0:
            try:
                cap_val = float(re.sub(r'[^0-9.]', '', raw_cap_str))
                full_load = (cap_val * 1000.0) / (3600.0 * speed_val)
                
                def calc_res(val):
                    v = abs(float(val))
                    if v <= 99: return '0.01'
                    if v <= 999: return '0.1'
                    return '1'

                if not field_map.get('res_l'): field_map['res_l'] = calc_res(full_load)
                if not field_map.get('res_r'): field_map['res_r'] = calc_res(cap_val)
                if not field_map.get('res_s'): field_map['res_s'] = '0.01'
                if not field_map.get('res_t'): field_map['res_t'] = '0.1'
            except Exception:
                pass

        # Re-format measurement grid values based on resolution
        if isinstance(data.get("grid_data"), list):
            for r_idx, row in enumerate(data["grid_data"], start=1):
                if isinstance(row, list):
                    for c_idx, val in enumerate(row):
                        str_val = str(val).strip()
                        if str_val:
                            try:
                                num_v = float(re.sub(r'[^0-9.]', '', str_val))
                                if c_idx == 0:  # Load kg
                                    field_map[f"g{r_idx}_0"] = f"{num_v:.{dec_r}f}"
                                elif c_idx == 1:  # Belt Kg/m
                                    field_map[f"g{r_idx}_1"] = f"{num_v:.{dec_l}f}"
                                elif c_idx == 2:  # Speed m/s
                                    field_map[f"g{r_idx}_2"] = f"{num_v:.{dec_s}f}"
                                elif c_idx == 3:  # Rate tph
                                    field_map[f"g{r_idx}_3"] = f"{num_v:.{dec_r}f}"
                                elif c_idx == 4:  # Totalizer Tonnes
                                    field_map[f"g{r_idx}_4"] = f"{num_v:.{dec_t}f}"
                                elif c_idx == 5:  # AO mA
                                    field_map[f"g{r_idx}_5"] = f"{num_v:.2f}"
                            except Exception:
                                pass

        # Short abbreviated keys to match 100% with backend template
        field_map['job'] = str(field_map.get('job_no') or data.get('job_no') or '')
        field_map['cust'] = str(field_map.get('customer') or data.get('customer') or '')
        field_map['cap'] = str(field_map.get('capacity') or data.get('capacity') or '')
        field_map['cn'] = str(field_map.get('conveyor_no') or data.get('conveyor_no') or '')

        field_map['bm'] = str(field_map.get('bs_model') or '')
        field_map['bs'] = str(field_map.get('bs_serial') or '')
        field_map['sw'] = str(field_map.get('bs_sw') or field_map.get('version') or '')

        field_map['rmm'] = str(field_map.get('rm_model') or field_map.get('remote_model') or '')
        field_map['rms'] = str(field_map.get('rm_serial') or field_map.get('remote_serial') or '')

        field_map['lm'] = str(field_map.get('sensor_model') or field_map.get('lc_model') or '')
        field_map['s1'] = str(field_map.get('s1') or '')
        field_map['s2'] = str(field_map.get('s2') or '')
        field_map['s3'] = str(field_map.get('s3') or '')
        field_map['s4'] = str(field_map.get('s4') or '')
        field_map['s5'] = str(field_map.get('s5') or '')
        field_map['s6'] = str(field_map.get('s6') or '')
        field_map['s7'] = str(field_map.get('s7') or '')
        field_map['s8'] = str(field_map.get('s8') or '')

        field_map['sm'] = str(field_map.get('tacho_model') or field_map.get('ss_model') or '')
        field_map['ss'] = str(field_map.get('tacho_serial') or field_map.get('ss_serial') or '')

        field_map['am'] = str(field_map.get('angle_sensor_model') or field_map.get('as_model') or '')
        field_map['as'] = str(field_map.get('angle_sensor_serial') or field_map.get('as_serial') or '')

        field_map['j1m'] = str(field_map.get('jbox_model1') or field_map.get('jb_1_model') or '')
        field_map['j1s'] = str(field_map.get('jbox_serial1') or field_map.get('jb_1_serial') or '')
        field_map['j2m'] = str(field_map.get('jbox_model2') or field_map.get('jb_2_model') or '')
        field_map['j2s'] = str(field_map.get('jbox_serial2') or field_map.get('jb_2_serial') or '')
        field_map['j3m'] = str(field_map.get('jbox_model3') or field_map.get('jb_3_model') or '')
        field_map['j3s'] = str(field_map.get('jbox_serial3') or field_map.get('jb_3_serial') or '')

        # Check if input supply is 24V
        raw_sup = str(field_map.get('spec_1') or field_map.get('act_1') or field_map.get('sp1') or field_map.get('ac1') or '').strip().upper()
        is_24v = '24' in raw_sup

        # Table 1: Pre-check handling
        if is_24v:
            field_map['sc'] = 'CHECKED AND FOUND OK'
            if len(doc.tables) > 1 and len(doc.tables[1].rows) > 0 and len(doc.tables[1].rows[0].cells) > 0:
                t1_cell = doc.tables[1].rows[0].cells[0]
                if len(t1_cell.paragraphs) >= 2:
                    t1_cell.paragraphs[0].text = "Check for 24V DC                                          :   CHECKED AND FOUND OK"
                    t1_cell.paragraphs[1].text = ""
                elif len(t1_cell.paragraphs) == 1:
                    t1_cell.paragraphs[0].text = "Check for 24V DC                                          :   CHECKED AND FOUND OK"
        else:
            sc_val = str(field_map.get('test_voltage_chk') or field_map.get('short_check') or '').strip()
            if not sc_val or sc_val.upper() in ['OK', 'CHECKED', 'PASSED']:
                field_map['sc'] = 'CHECKED AND FOUND OK'
            else:
                field_map['sc'] = sc_val

        field_map['rl'] = str(field_map.get('res_l') or '')
        field_map['rs'] = str(field_map.get('res_s') or '')
        field_map['rr'] = str(field_map.get('res_r') or '')
        field_map['rt'] = str(field_map.get('res_t') or '')

        # 1. Input Supply Voltage (Row 1)
        if is_24v:
            field_map['sp1'] = '24V'
            field_map['ac1'] = '24V'
        else:
            field_map['sp1'] = '230V'
            field_map['ac1'] = '230V'

        # 2. Derived DC Voltages (Row 2)
        if is_24v:
            field_map['sp2'] = 'NA'
            field_map['ac2'] = 'NA'
        else:
            field_map['sp2'] = '24V'
            field_map['ac2'] = '24V'

        # 3. Display and Keypad Functionality (Row 3)
        field_map['sp3'] = 'OK'
        field_map['ac3'] = 'OK'

        # 4. Belt Load (Row 4) - sp4 is strictly 5.00 mV, ac4 is clean load value matching resolution
        field_map['sp4'] = '5.00 mV'
        try:
            raw_c = re.sub(r'[^0-9.]', '', str(field_map.get('capacity') or field_map.get('rated_capacity') or '0'))
            c_val = float(raw_c) if raw_c else 0.0
            raw_s = re.sub(r'[^0-9.]', '', str(field_map.get('belt_speed') or '0'))
            s_val = float(raw_s) if raw_s else 0.0
            calc_load = (c_val * 1000.0) / (3600.0 * s_val) if (c_val > 0 and s_val > 0) else None
        except Exception:
            calc_load = None
            s_val = 0.0

        res_l = str(field_map.get('res_l') or field_map.get('rl') or '').strip()
        if res_l == '0.01':
            dec_l = 2
        elif res_l == '0.1':
            dec_l = 1
        elif res_l == '1':
            dec_l = 0
        else:
            if calc_load is not None:
                dec_l = 2 if calc_load <= 99 else (1 if calc_load <= 999 else 0)
            else:
                dec_l = 2

        raw_ac4 = str(field_map.get('act_4') or field_map.get('ac4') or '').strip()
        clean_ac4 = re.sub(r'(?i)\s*kg/m', '', raw_ac4).strip()
        clean_ac4 = re.sub(r'(?i)\s*tph', '', clean_ac4).strip()
        clean_ac4_digits = re.sub(r'[^0-9.]', '', clean_ac4)
        if clean_ac4_digits:
            try:
                field_map['ac4'] = f"{float(clean_ac4_digits):.{dec_l}f}"
            except Exception:
                field_map['ac4'] = clean_ac4_digits
        elif calc_load is not None:
            field_map['ac4'] = f"{calc_load:.{dec_l}f}"
        else:
            field_map['ac4'] = "0.00"

        # 5. Belt Speed (Row 5) - sp5 is Frequency Hz, ac5 is clean speed value
        try:
            raw_p = re.sub(r'[^0-9.]', '', str(field_map.get('pulses') or field_map.get('speed_pulses') or '12'))
            p_val = float(raw_p) if raw_p else 12.0
            raw_d = re.sub(r'[^0-9.]', '', str(field_map.get('pulley_diameter') or field_map.get('tacho_wheel_dia') or '0.16'))
            d_val = float(raw_d) if raw_d else 0.16
            if d_val > 5.0:
                d_val = d_val / 1000.0
            calc_hz = (s_val * p_val) / (math.pi * d_val) if (s_val > 0 and d_val > 0) else None
        except Exception:
            calc_hz = None

        raw_sp5 = str(field_map.get('spec_5') or field_map.get('sp5') or '').strip()
        clean_sp5 = re.sub(r'(?i)\s*hz', '', raw_sp5).strip()
        clean_sp5_digits = re.sub(r'[^0-9.]', '', clean_sp5)
        if clean_sp5_digits:
            try:
                field_map['sp5'] = f"{float(clean_sp5_digits):.2f} Hz"
            except Exception:
                field_map['sp5'] = f"{clean_sp5_digits} Hz"
        elif calc_hz is not None:
            field_map['sp5'] = f"{calc_hz:.2f} Hz"
        else:
            field_map['sp5'] = "31.83 Hz"

        raw_ac5 = str(field_map.get('act_5') or field_map.get('ac5') or '').strip()
        clean_ac5 = re.sub(r'(?i)\s*m/s', '', raw_ac5).strip()
        clean_ac5_digits = re.sub(r'[^0-9.]', '', clean_ac5)
        if clean_ac5_digits:
            try:
                field_map['ac5'] = f"{float(clean_ac5_digits):.2f}"
            except Exception:
                field_map['ac5'] = clean_ac5_digits
        elif s_val > 0:
            field_map['ac5'] = f"{s_val:.2f}"
        else:
            field_map['ac5'] = "2.50"

        # 6. Number of PF Contacts (Row 6)
        field_map['sp6'] = '4'
        field_map['ac6'] = '4'

        # 7. Communication Output (Row 7)
        field_map['sp7'] = 'RS 485'
        field_map['ac7'] = 'RS 485'

        # 8. Analog Output (Row 8) label based on num_ao if not specified
        raw_ao = data.get("num_outputs") or field_map.get("num_outputs")
        if raw_ao is not None and str(raw_ao).strip() in ["1", "2", "3"]:
            num_ao = str(raw_ao).strip()
        else:
            has_ao3 = any(str(data.get(f"g{r}_5_ao3") or field_map.get(f"g{r}_5_ao3") or "").strip() for r in range(1, 12))
            has_ao2 = any(str(data.get(f"g{r}_5_ao2") or field_map.get(f"g{r}_5_ao2") or "").strip() for r in range(1, 12))
            if has_ao3: num_ao = "3"
            elif has_ao2: num_ao = "2"
            else: num_ao = "1"

        if num_ao == "3":
            field_map['sp8'] = '3 x 4-20mA'
            field_map['ac8'] = '3 x 4-20mA'
        elif num_ao == "2":
            field_map['sp8'] = '2 x 4-20mA'
            field_map['ac8'] = '2 x 4-20mA'
        else:
            field_map['sp8'] = '4-20mA'
            field_map['ac8'] = '4-20mA'

        # 9. Wiring, TB and Component Layout (Row 9)
        field_map['sp9'] = 'OK'
        field_map['ac9'] = 'OK'

        # Map grid data g10..g115 and AO1, AO2, AO3 - DO NOT duplicate AO1 into AO2/AO3!
        for r_g in range(1, 12):
            for c_g in range(5):
                val_g = str(field_map.get(f'g{r_g}_{c_g}') or '')
                field_map[f'g{r_g}{c_g}'] = val_g

            # AO values
            val_ao1 = str(field_map.get(f'g{r_g}_5_ao1') or field_map.get(f'g{r_g}_5') or '')
            val_ao2 = str(field_map.get(f'g{r_g}_5_ao2') or '')
            val_ao3 = str(field_map.get(f'g{r_g}_5_ao3') or '')

            field_map[f'g{r_g}5'] = val_ao1
            field_map[f'g{r_g}5_ao1'] = val_ao1
            field_map[f'g{r_g}5_ao2'] = val_ao2
            field_map[f'g{r_g}5_ao3'] = val_ao3

        field_map['inst'] = str(field_map.get('instrument_used') or data.get('instrument_used') or '')
        field_map['tb'] = str(field_map.get('tested_by') or data.get('tested_by') or '')
        field_map['ab'] = str(field_map.get('approved_by') or data.get('approved_by') or '')
        field_map['dt'] = str(field_map.get('date') or data.get('date') or '')

    # 1. Paragraph replacement
    for p in doc.paragraphs:
        replace_in_paragraph(p, field_map)

    # 2. Table cell replacement
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    replace_in_paragraph(p, field_map)

    # 3. Clean up any unhandled template tags
    for p in doc.paragraphs:
        clean_unhandled_tags(p)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    clean_unhandled_tags(p)

    # Output path is passed from app.py
    doc.save(output_path)

    pdf_path = output_path.replace(".docx", ".pdf")
    convert_docx_to_pdf(output_path, pdf_path)

    return pdf_path

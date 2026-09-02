import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if os.getcwd() != BASE_DIR:
    os.chdir(BASE_DIR)
import os
import sys
import json
import shutil
import datetime
import docx

# Set working directory to project root
PROJECT_DIR = r"C:\Users\abell\OneDrive\Desktop\TEST REPORT PRODUCTION final"
OUTPUT_TARGET_DIR = r"C:\Users\abell\OneDrive\Desktop\testing"

sys.path.insert(0, PROJECT_DIR)

import app
import docx_generator

os.makedirs(OUTPUT_TARGET_DIR, exist_ok=True)

# 23 Production Systems
SYSTEMS = [
    "job_traveller_card",
    "batching_system",
    "remote_indicator",
    "digital_indicator",
    "weigh_feeder",
    "crane_scale",
    "signal_conditioner",
    "trip_safe",
    "vibration_switch",
    "acc_mv",
    "acc_charge",
    "vibration_meter",
    "charge_amplifier",
    "inprocess",
    "odd_system",
    "dd_system",
    "work_instructions",
    "performance_delay",
    "equipment_list",
    "loss_in_weigh_feeder",
    "misc",
    "belt_scale"
]

CUSTOMERS = [
    "Jindal Steel & Power Ltd",
    "Tata Steel Ltd (Kalinganagar)",
    "JSW Steel Ltd (Vijayanagar)",
    "Adani Power & Infra Corp",
    "NTPC Ramagundam STPS",
    "Ultratech Cement Works",
    "Alstom Transport India Ltd",
    "BHEL Heavy Electricals",
    "NMDC Steel Plant (Nagarnar)",
    "Vedanta Aluminium & Power"
]

TECHNICIANS = [
    "Rajesh Kumar (Sr. Engineer)",
    "Amit Sharma (QA Tech)",
    "Priya Patel (QC Inspector)",
    "Suresh Reddy (Field Engineer)",
    "Anil Verma (Lead Specialist)"
]

APPROVERS = [
    "Dr. V. K. Malhotra (QA HOD)",
    "Sunil Narang (Plant Head)",
    "R. C. Das (Chief Auditor)",
    "M. S. Rao (Quality Manager)",
    "K. L. Mehta (Technical Director)"
]

def generate_payload_variations(system_key, test_idx):
    cust = CUSTOMERS[test_idx % len(CUSTOMERS)]
    tech = TECHNICIANS[test_idx % len(TECHNICIANS)]
    appr = APPROVERS[test_idx % len(APPROVERS)]
    job_no = f"JOB-{system_key.upper()[:4]}-2026-{100 + test_idx}"
    date_str = (datetime.date.today() - datetime.timedelta(days=test_idx)).strftime("%Y-%m-%d")
    
    base = {
        "report_type": system_key,
        "user_name": tech,
        "job_no": job_no,
        "customer": cust,
        "conveyor_no": f"CV-0{test_idx + 1}" if test_idx % 2 == 0 else f"CONV-MAIN-{test_idx}",
        "capacity": f"{100 * (test_idx + 1)} TPH",
        "date": date_str,
        "tested_by": tech,
        "approved_by": appr,
        "item_desc": f"Industrial {system_key.replace('_', ' ').title()} Unit",
        "model_no": f"MDL-{system_key.upper()[:3]}-{200 + test_idx}",
        "serial_no": f"SN-8800{test_idx}",
        "qty": str((test_idx % 4) + 1),
        "visual_inspection": "PASSED",
        "insulation_test": "PASSED (>1000M Ohm)",
        "calibration_test": "PASSED",
        "remarks": f"Test run #{test_idx + 1}: All parameters verified within acceptable engineering tolerances."
    }
    
    # Add system-specific multi-row table variations
    if system_key in ["misc", "belt_scale", "digital_indicator", "weigh_feeder", "crane_scale", "loss_in_weigh_feeder"]:
        rows_count = (test_idx % 6) + 1
        table_data = []
        for r in range(rows_count):
            table_data.append({
                "sl_no": str(r + 1),
                "input_res": f"{350.0 + (r * 0.2):.1f}",
                "output_res": f"{350.2 + (r * 0.1):.1f}",
                "init_unbalance": f"{(0.01 * (r + 1)):.2f}",
                "remarks": "PASSED"
            })
        base["table_data"] = table_data
        
    return base

def check_unfilled_tags(doc_path):
    doc = docx.Document(doc_path)
    unfilled = []
    
    def check_text(txt):
        if "{{" in txt or "}}" in txt or "TODO" in txt or "[ ___ ]" in txt:
            unfilled.append(txt.strip())
            
    for p in doc.paragraphs:
        check_text(p.text)
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    check_text(p.text)
                    
    return unfilled

def run_mass_test():
    print("=" * 80)
    print("  MASS STRESS TEST & FORENSIC BUG HUNT (230 TEST CASES)")
    print(f"  Target Output Folder: {OUTPUT_TARGET_DIR}")
    print("=" * 80)
    
    client = app.app.test_client()
    
    total_run = 0
    passed_run = 0
    failed_run = 0
    bugs_found = []
    generated_files = []
    
    start_time = datetime.datetime.now()
    
    for sys_idx, system_key in enumerate(SYSTEMS, 1):
        print(f"\n--- Testing System [{sys_idx}/23]: {system_key.upper()} (10 Test Cases) ---")
        
        sys_pass = 0
        sys_fail = 0
        
        for t_idx in range(10):
            total_run += 1
            payload = generate_payload_variations(system_key, t_idx)
            
            try:
                # Submit via Flask test client
                resp = client.post("/api/submit", json=payload)
                if resp.status_code != 200:
                    err_msg = f"HTTP {resp.status_code}: {resp.get_data(as_text=True)}"
                    print(f"  [FAIL] Test #{t_idx + 1}: {err_msg}")
                    bugs_found.append({"system": system_key, "test_idx": t_idx + 1, "error": err_msg})
                    failed_run += 1
                    sys_fail += 1
                    continue
                    
                res_json = resp.get_json()
                if not res_json or res_json.get("status") != "success":
                    err_msg = f"API error response: {res_json}"
                    print(f"  [FAIL] Test #{t_idx + 1}: {err_msg}")
                    bugs_found.append({"system": system_key, "test_idx": t_idx + 1, "error": err_msg})
                    failed_run += 1
                    sys_fail += 1
                    continue
                    
                pdf_filename = res_json.get("pdf_filename")
                src_pdf_path = os.path.join(docx_generator.EXPORTS_DIR, pdf_filename)
                
                # Copy PDF to C:\Users\abell\OneDrive\Desktop\testing
                dest_pdf_name = f"{system_key.upper()}_Test_{t_idx + 1:02d}_{pdf_filename}"
                dest_pdf_path = os.path.join(OUTPUT_TARGET_DIR, dest_pdf_name)
                
                if os.path.exists(src_pdf_path):
                    shutil.copy2(src_pdf_path, dest_pdf_path)
                    generated_files.append(dest_pdf_path)
                else:
                    err_msg = f"Generated PDF file missing on disk: {src_pdf_path}"
                    print(f"  [FAIL] Test #{t_idx + 1}: {err_msg}")
                    bugs_found.append({"system": system_key, "test_idx": t_idx + 1, "error": err_msg})
                    failed_run += 1
                    sys_fail += 1
                    continue
                    
                # AST Tag Check on DOCX
                docx_filename = pdf_filename.replace(".pdf", ".docx")
                src_docx_path = os.path.join(docx_generator.EXPORTS_DIR, docx_filename)
                if os.path.exists(src_docx_path):
                    unfilled_tags = check_unfilled_tags(src_docx_path)
                    if unfilled_tags:
                        err_msg = f"Unfilled tags found in AST scan: {unfilled_tags[:3]}"
                        print(f"  [WARN] Test #{t_idx + 1}: {err_msg}")
                        bugs_found.append({"system": system_key, "test_idx": t_idx + 1, "error": err_msg})
                        
                passed_run += 1
                sys_pass += 1
                print(f"  [PASS] Test #{t_idx + 1:02d}/10: {dest_pdf_name}")
                
            except Exception as e:
                import traceback
                err_msg = f"Exception: {str(e)}\n{traceback.format_exc()}"
                print(f"  [EXCEPT] Test #{t_idx + 1}: {str(e)}")
                bugs_found.append({"system": system_key, "test_idx": t_idx + 1, "error": err_msg})
                failed_run += 1
                sys_fail += 1
                
        print(f"-> System [{system_key}]: {sys_pass}/10 Passed, {sys_fail}/10 Failed")

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Write summary audit json
    audit_summary = {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_test_cases": total_run,
        "passed": passed_run,
        "failed": failed_run,
        "duration_seconds": round(duration, 2),
        "target_output_dir": OUTPUT_TARGET_DIR,
        "files_exported_count": len(generated_files),
        "bugs_found": bugs_found
    }

    audit_path = os.path.join(PROJECT_DIR, "mass_test_audit.json")
    with open(audit_path, "w") as f:
        json.dump(audit_summary, f, indent=2)

    print("\n" + "=" * 80)
    print("  MASS STRESS TEST SUMMARY REPORT")
    print("=" * 80)
    print(f"  Total Test Cases Executed : {total_run}")
    print(f"  Passed                    : {passed_run}")
    print(f"  Failed                    : {failed_run}")
    print(f"  Total PDFs Exported       : {len(generated_files)}")
    print(f"  Duration                  : {duration:.2f} seconds")
    print(f"  Audit Report Saved To     : {audit_path}")
    print(f"  Export Folder             : {OUTPUT_TARGET_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    run_mass_test()


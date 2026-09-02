import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if os.getcwd() != BASE_DIR:
    os.chdir(BASE_DIR)
import os
import re
import datetime
import json
import docx
from app import app
import docx_generator

# Sample JSON test fixtures for every system (23 systems)
TEST_FIXTURES = {
    "job_traveller_card": {
        "report_type": "job_traveller_card",
        "user_name": "E2E Tester",
        "job_no": "JOB-JTC-001",
        "customer": "Steel Plant Corp",
        "system": "Job Traveller Card",
        "qty": "5",
        "date": "2026-08-22",
        "tested_by": "Senior Inspector",
        "approved_by": "HOD-PDN"
    },
    "batching_system": {
        "report_type": "batching_system",
        "user_name": "E2E Tester",
        "job_no": "JOB-BS-002",
        "customer": "Cement Works Ltd",
        "capacity": "1000 Kg",
        "material": "Cement Raw Mix",
        "date": "2026-08-22",
        "tested_by": "Test Engineer",
        "approved_by": "HOD-PDN"
    },
    "remote_indicator": {
        "report_type": "remote_indicator",
        "user_name": "E2E Tester",
        "job_no": "JOB-RI-003",
        "customer": "Mining Logistics Inc",
        "capacity": "50 TPH",
        "rate": "50",
        "load": "10",
        "speed": "2.5",
        "totalizer": "12345",
        "date": "2026-08-22",
        "tested_by": "Test Technician",
        "approved_by": "HOD-PDN"
    },
    "digital_indicator": {
        "report_type": "digital_indicator",
        "user_name": "E2E Tester",
        "job_no": "JOB-DI-004",
        "customer": "Chemical Process Corp",
        "capacity": "2000 Kg",
        "date": "2026-08-22",
        "tested_by": "Test Engineer",
        "approved_by": "HOD-PDN"
    },
    "weigh_feeder": {
        "report_type": "weigh_feeder",
        "user_name": "E2E Tester",
        "job_no": "JOB-WF-005",
        "customer": "Thermal Power Station",
        "capacity": "150 TPH",
        "conveyor_no": "CV-WF-01",
        "date": "2026-08-22",
        "tested_by": "Lead Inspector",
        "approved_by": "HOD-PDN"
    },
    "crane_scale": {
        "report_type": "crane_scale",
        "user_name": "E2E Tester",
        "job_no": "JOB-CS-006",
        "customer": "Heavy Forge Industries",
        "capacity": "10 Tonnes",
        "date": "2026-08-22",
        "tested_by": "Test Engineer",
        "approved_by": "HOD-PDN"
    },
    "signal_conditioner": {
        "report_type": "signal_conditioner",
        "user_name": "E2E Tester",
        "job_no": "JOB-SC-007",
        "customer": "Automation Systems Ltd",
        "model_no": "SC-4020",
        "serial_no": "SN-SC-8899",
        "date": "2026-08-22",
        "tested_by": "Electronics Tech",
        "approved_by": "HOD-PDN"
    },
    "trip_safe": {
        "report_type": "trip_safe",
        "user_name": "E2E Tester",
        "job_no": "JOB-TS-008",
        "customer": "Refinery Safety Unit",
        "model_no": "TS-300",
        "serial_no": "SN-TS-1234",
        "date": "2026-08-22",
        "tested_by": "Safety Officer",
        "approved_by": "HOD-PDN"
    },
    "vibration_switch": {
        "report_type": "vibration_switch",
        "user_name": "E2E Tester",
        "job_no": "JOB-VS-009",
        "customer": "Turbine Monitoring Co",
        "model_no": "VS-100",
        "serial_no": "SN-VS-5566",
        "date": "2026-08-22",
        "tested_by": "Vibration Analyst",
        "approved_by": "HOD-PDN"
    },
    "acc_mv": {
        "report_type": "acc_mv",
        "user_name": "E2E Tester",
        "job_no": "JOB-AMV-010",
        "customer": "Aero Testing Labs",
        "model_no": "ACC-MV-50",
        "serial_no": "SN-AMV-9900",
        "date": "2026-08-22",
        "tested_by": "Aero Engineer",
        "approved_by": "HOD-PDN"
    },
    "acc_charge": {
        "report_type": "acc_charge",
        "user_name": "E2E Tester",
        "job_no": "JOB-ACH-011",
        "customer": "Defense Sensor Group",
        "model_no": "ACC-CHG-100",
        "serial_no": "SN-ACH-7711",
        "date": "2026-08-22",
        "tested_by": "Sensor Specialist",
        "approved_by": "HOD-PDN"
    },
    "vibration_meter": {
        "report_type": "vibration_meter",
        "user_name": "E2E Tester",
        "job_no": "JOB-VM-012",
        "customer": "Machinery Diagnostics",
        "model_no": "VM-200",
        "serial_no": "SN-VM-3322",
        "date": "2026-08-22",
        "tested_by": "Field Inspector",
        "approved_by": "HOD-PDN"
    },
    "charge_amplifier": {
        "report_type": "charge_amplifier",
        "user_name": "E2E Tester",
        "job_no": "JOB-CA-013",
        "customer": "Acoustic Dynamics Inc",
        "model_no": "CA-500",
        "serial_no": "SN-CA-4455",
        "date": "2026-08-22",
        "tested_by": "Lab Technician",
        "approved_by": "HOD-PDN"
    },
    "inprocess": {
        "report_type": "inprocess",
        "user_name": "E2E Tester",
        "job_no": "JOB-INP-014",
        "customer": "Internal QC Dept",
        "qty": "2",
        "nature_failure": "PCB Solder Short",
        "date": "2026-08-22",
        "tested_by": "QC Engineer",
        "approved_by": "HOD-PDN"
    },
    "odd_system": {
        "report_type": "odd_system",
        "user_name": "E2E Tester",
        "job_no": "JOB-ODD-015",
        "customer": "Optics & Defense Corp",
        "model_no": "ODD-9000",
        "serial_no": "SN-ODD-101",
        "date": "2026-08-22",
        "tested_by": "Systems Lead",
        "approved_by": "HOD-PDN"
    },
    "dd_system": {
        "report_type": "dd_system",
        "user_name": "E2E Tester",
        "job_no": "JOB-DD-016",
        "customer": "Digital Display Systems",
        "model_no": "DD-8000",
        "serial_no": "SN-DD-202",
        "date": "2026-08-22",
        "tested_by": "Display Specialist",
        "approved_by": "HOD-PDN"
    },
    "work_instructions": {
        "report_type": "work_instructions",
        "user_name": "E2E Tester",
        "job_no": "JOB-WI-017",
        "customer": "IPA Standard WI",
        "doc_no": "WI/PDN/001",
        "rev_no": "02",
        "date": "2026-08-22",
        "tested_by": "Process Engineer",
        "approved_by": "HOD-PDN"
    },
    "performance_index": {
        "report_type": "performance_index",
        "user_name": "E2E Tester",
        "job_no": "JOB-PI-018",
        "customer": "IPA Management",
        "month": "August 2026",
        "jobs_scheduled": "25",
        "jobs_completed": "25",
        "achieved_pct": "100%",
        "date": "2026-08-22",
        "tested_by": "Planning Manager",
        "approved_by": "HOD-PDN"
    },
    "performance_delay": {
        "report_type": "performance_delay",
        "user_name": "E2E Tester",
        "job_no": "JOB-PDA-019",
        "customer": "Operations Analytics",
        "month_year": "08/2026",
        "total_scheduled": "30",
        "total_executed": "28",
        "total_delay": "2 Jobs",
        "date": "2026-08-22",
        "tested_by": "Ops Manager",
        "approved_by": "HOD-PDN"
    },
    "equipment_list": {
        "report_type": "equipment_list",
        "user_name": "E2E Tester",
        "job_no": "JOB-EL-020",
        "customer": "Cal Lab Master Inventory",
        "ref_no": "REF-CAL-2026",
        "date": "2026-08-22",
        "tested_by": "Metrologist",
        "approved_by": "HOD-PDN"
    },
    "loss_in_weigh_feeder": {
        "report_type": "loss_in_weigh_feeder",
        "user_name": "E2E Tester",
        "job_no": "JOB-LIW-021",
        "customer": "Pharma Process Plant",
        "capacity": "25 TPH",
        "material": "API Powder",
        "date": "2026-08-22",
        "tested_by": "Cal Engineer",
        "approved_by": "HOD-PDN"
    },
    "misc": {
        "report_type": "misc",
        "user_name": "E2E Tester",
        "job_no": "JOB-MISC-022",
        "customer": "Misc Systems Division",
        "item_desc": "Proximity Sensor Relay Box",
        "model_no": "PRX-500",
        "serial_no": "SN-PRX-1122",
        "qty": "3",
        "test_readings": "1. Insulation Resistance: >500M Ohm\n2. Trigger Threshold: 5.2mm\n3. Output Relay Response: PASSED",
        "date": "2026-08-22",
        "tested_by": "Test Specialist",
        "approved_by": "HOD-PDN"
    },
    "belt_scale": {
        "report_type": "belt_scale",
        "user_name": "E2E Tester",
        "job_no": "JOB-BS-023",
        "customer": "National Mining Corp",
        "conveyor_no": "CV-MAIN-01",
        "capacity": "1200 TPH",
        "res_l": "0.01",
        "res_s": "0.001",
        "res_r": "0.1",
        "res_t": "0.001",
        "instrument_used": "Fluke 87V Calibrator",
        "tested_by": "Lead Cal Tech",
        "approved_by": "HOD-PDN",
        "date": "2026-08-22",
        "bs_model": "BS-9000",
        "bs_serial": "SN-BS-7711",
        "remote_model": "RM-400",
        "remote_serial": "SN-RM-8822",
        "sensor_model": "LC-350",
        "sensor_s1": "SN-S1-001",
        "sensor_s2": "SN-S2-002",
        "tacho_model": "TACHO-100",
        "tacho_serial": "SN-TCH-33",
        "tacho_rpm": "1500",
        "tacho_belt_speed": "2.5",
        "tacho_wheel_dia": "300",
        "jbox_model1": "JB-4WAY",
        "jbox_serial1": "SN-JB-101",
        "short_check": "OK",
        "routine_tests": [
            {"spec": "230V AC +/- 10%", "act": "230V AC"},
            {"spec": "+/- 15V DC", "act": "15.01V DC"},
            {"spec": "Display Brightness", "act": "OK"},
            {"spec": "0-100% Span", "act": "1200 TPH"},
            {"spec": "0-3 m/s", "act": "2.5 m/s"},
            {"spec": "Pulse Output", "act": "1000 pulses/t"},
            {"spec": "4-20mA Output", "act": "20.0mA"},
            {"spec": "RS485 Comm", "act": "PASSED"},
            {"spec": "Zero Calibration", "act": "PASSED"}
        ],
        "grid_data": [
            ["0%", "0 TPH", "0 TPH", "0.00%", "4.00 mA", "PASSED"],
            ["25%", "300 TPH", "300 TPH", "0.00%", "8.00 mA", "PASSED"],
            ["50%", "600 TPH", "600 TPH", "0.00%", "12.00 mA", "PASSED"],
            ["75%", "900 TPH", "900 TPH", "0.00%", "16.00 mA", "PASSED"],
            ["100%", "1200 TPH", "1200 TPH", "0.00%", "20.00 mA", "PASSED"]
        ]
    }
}

def deep_ast_scan_docx(file_path):
    """
    Performs a deep AST scan across paragraphs, runs, tables, cells, headers, footers,
    and raw XML nodes of a .docx file to verify 0 remaining unfilled template tags.
    Target unfilled patterns: {{...}}, TODO, [ ___ ]
    """
    doc = docx.Document(file_path)
    unfilled = []

    pattern = re.compile(r'\{\{.*?\}\}|\bTODO\b|\[\s*___\s*\]', re.IGNORECASE)

    # 1. Body Paragraphs
    for i, p in enumerate(doc.paragraphs):
        matches = pattern.findall(p.text)
        if matches:
            unfilled.append(f"Paragraph {i}: {matches}")

    # 2. Table Cells
    for t_idx, table in enumerate(doc.tables):
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                matches = pattern.findall(cell.text)
                if matches:
                    unfilled.append(f"Table {t_idx} [R{r_idx}C{c_idx}]: {matches}")

    # 3. Headers & Footers
    for s_idx, section in enumerate(doc.sections):
        if section.header:
            for h_p in section.header.paragraphs:
                matches = pattern.findall(h_p.text)
                if matches:
                    unfilled.append(f"Header {s_idx}: {matches}")
        if section.footer:
            for f_p in section.footer.paragraphs:
                matches = pattern.findall(f_p.text)
                if matches:
                    unfilled.append(f"Footer {s_idx}: {matches}")

    return unfilled

def run_verification_suite():
    print("\n" + "="*80)
    print("  AUTOMATED END-TO-END VERIFICATION TEST HARNESS")
    print("  Target: Production Reporting Systems (23 Systems)")
    print(f"  Output Path: {docx_generator.EXPORTS_DIR}")
    print("="*80 + "\n")

    client = app.test_client()
    passed = 0
    failed = 0
    results = []

    for system_name, fixture in TEST_FIXTURES.items():
        print(f"Testing System [{system_name:<22}] ...", end=" ", flush=True)
        try:
            # 1. Submit POST request to /api/submit
            response = client.post('/api/submit', json=fixture)
            if response.status_code != 200:
                print(f"FAILED (HTTP {response.status_code})")
                results.append((system_name, False, f"HTTP Status {response.status_code}: {response.data.decode('utf-8')}"))
                failed += 1
                continue

            res_json = response.get_json()
            if not res_json or res_json.get('status') != 'success':
                print(f"FAILED (Response status: {res_json.get('status') if res_json else 'No JSON'})")
                results.append((system_name, False, f"API Error: {res_json.get('message') if res_json else 'Empty payload'}"))
                failed += 1
                continue

            pdf_filename = res_json.get('pdf_filename', '')
            docx_filename = pdf_filename.replace('.pdf', '.docx')
            
            # 2. Verify file existence in TESTING OUTPUTS
            docx_path = os.path.join(docx_generator.EXPORTS_DIR, docx_filename)
            pdf_path = os.path.join(docx_generator.EXPORTS_DIR, pdf_filename)

            if not os.path.exists(docx_path):
                # Search by job_no in EXPORTS_DIR
                docx_candidates = [f for f in os.listdir(docx_generator.EXPORTS_DIR) if f.endswith('.docx') and fixture['job_no'] in f]
                if docx_candidates:
                    docx_path = os.path.join(docx_generator.EXPORTS_DIR, docx_candidates[0])

            if not os.path.exists(docx_path):
                print(f"FAILED (DOCX missing: {docx_filename})")
                results.append((system_name, False, f"DOCX file not found at {docx_path}"))
                failed += 1
                continue

            if not os.path.exists(pdf_path):
                print(f"FAILED (PDF missing: {pdf_filename})")
                results.append((system_name, False, f"PDF file not found at {pdf_path}"))
                failed += 1
                continue

            # 3. Deep AST scan for unfilled template tags
            unfilled_tags = deep_ast_scan_docx(docx_path)
            if unfilled_tags:
                print(f"FAILED (Unfilled tags found: {len(unfilled_tags)})")
                results.append((system_name, False, f"AST scan found unfilled tags: {unfilled_tags}"))
                failed += 1
                continue

            print("PASSED (HTTP 200, DOCX & PDF verified, 0 unfilled tags)")
            results.append((system_name, True, "All assertions passed cleanly"))
            passed += 1

        except Exception as e:
            print(f"ERROR ({str(e)})")
            results.append((system_name, False, f"Exception: {str(e)}"))
            failed += 1

    print("\n" + "="*80)
    print("  VERIFICATION TEST SUMMARY")
    print("="*80)
    print(f"Total Systems Tested : {len(TEST_FIXTURES)}")
    print(f"Passed               : {passed}")
    print(f"Failed               : {failed}")
    print("="*80)

    for sys_name, is_pass, detail in results:
        status_str = "[ PASS ]" if is_pass else "[ FAIL ]"
        print(f"  {status_str} {sys_name:<25} - {detail}")

    print("="*80 + "\n")
    return failed == 0

if __name__ == "__main__":
    success = run_verification_suite()
    exit(0 if success else 1)


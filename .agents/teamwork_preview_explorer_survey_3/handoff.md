# Handoff Report: Integration, Mapping, and Automated Testing Architecture for 20+ Reporting Systems

**Author**: Explorer 3 (Integration, Mapping & Testing Architect)  
**Working Directory**: `C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\.agents\teamwork_preview_explorer_survey_3`  
**Date**: 2026-08-22  
**Status**: Complete  

---

## 1. Observation

Direct observations from inspection of the codebase and workspace:

### 1.1 Template Inventory in `New folder`
Scanning `C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\New folder` revealed 35 files (24 `.docx`, 1 `.doc`, 1 `.xlsx`, 9 `.pdf`):
- **Already Active in `templates_docx/`** (2 systems):
  1. `PP-05_03 Belt Scale.docx` (41,190 bytes) -> `/belt-scale`
  2. `PP-05_17 Miscellaneous Items.docx` (20,690 bytes) -> `/misc-report`
- **Master Reference / Non-System Files** (4 files):
  1. `PP - 05 PRODUCTION RECORDS 14_11_2024.docx` (1,772,105 bytes, 1436 paragraphs, 73 tables — master manual)
  2. `PP - 05 PRODUCTION RECORDS.doc` (2,195,456 bytes — legacy binary manual)
  3. `PP-05_01 Production Plan.xlsx` (39,968 bytes — Excel spreadsheet)
  4. `PP-05_23 Job Card.pdf` (36,874 bytes — PDF only without standalone docx)
- **New Standalone `.docx` Reporting Templates to Migrate & Implement** (21 templates):
  1. `PP-05_02 Job Traveller Card.docx` (30,272 bytes, 7 paras, 1 table)
  2. `PP-05_04 Batching System.docx` (31,315 bytes, 18 paras, 5 tables)
  3. `PP-05_05 Remote Indicator.docx` (31,764 bytes, 29 paras, 2 tables)
  4. `PP-05_06 Digital Indicator.docx` (42,203 bytes, 42 paras, 5 tables)
  5. `PP-05_07 Weigh Feeder.docx` (31,488 bytes, 41 paras, 7 tables)
  6. `PP-05_08 Crane Scale.docx` (26,380 bytes, 35 paras, 2 tables)
  7. `PP-05_09 Signal Conditioner.docx` (22,803 bytes, 41 paras, 1 table)
  8. `PP-05_10 tRIP sAFE.docx` (23,694 bytes, 32 paras, 1 table)
  9. `PP-05_11 Vibration Switch.docx` (19,674 bytes, 13 paras, 3 tables)
  10. `PP-05_12 ACC mV.docx` (24,125 bytes, 31 paras, 5 tables)
  11. `PP-05_13 ACC Charge.docx` (26,021 bytes, 26 paras, 5 tables)
  12. `PP-05_14 Vibration Meter.docx` (24,667 bytes, 9 paras, 2 tables)
  13. `PP-05_15 Charge Amplifier.docx` (30,788 bytes, 11 paras, 3 tables)
  14. `PP-05_16 Inprocess.docx` (19,373 bytes, 2 paras, 1 table)
  15. `PP-05_18_A ODD System.docx` (22,493 bytes, 1 para, 1 table)
  16. `PP-05_18_B DD System.docx` (22,049 bytes, 1 para, 1 table)
  17. `PP-05_19 Work Instructions.docx` (16,745 bytes, 24 paras, 2 tables)
  18. `PP-05_20 Performance Index.docx` (23,784 bytes, 8 paras, 1 table)
  19. `PP-05_21 Performance Delay Analysis.docx` (33,337 bytes, 19 paras, 2 tables)
  20. `PP-05_22 Equipment List.docx` (28,610 bytes, 2 paras, 1 table)
  21. `PP-05_24 Loss in Weigh Feeder.docx` (34,149 bytes, 32 paras, 5 tables)

### 1.2 Portal & Application Structure
- `templates/portal.html`: Contains 24 system cards. 2 are active (`Belt Scale`, `Miscellaneous Report`), while 22 cards are styled with "Coming Soon" badges.
- `app.py`:
  - Flask web app with SQLite database (`belt_scale.db`).
  - Auth routes: `/login`, `/logout`, with session-based role checks (`admin`, `tech`).
  - Submission route: `/api/submit` (POST) parses JSON payload, invokes `docx_generator.generate_docx_record(data, docx_path)`, converts to PDF via `docx_generator.convert_docx_to_pdf(docx_path, pdf_path)`, saves record to database, and returns `{ 'status': 'success', 'record_id': ..., 'pdf_filename': ..., 'pdf_download_url': ... }`.
  - Download route: `/download/<filename>` serves generated documents from `docx_generator.EXPORTS_DIR` (`TESTING OUTPUTS`).
- `docx_generator.py`:
  - Implements `generate_belt_scale_docx` and `generate_misc_report_docx` using `python-docx`.
  - PDF conversion uses MS Word COM automation (`win32com.client.DispatchEx("Word.Application")`).
- **COM Verification**: Verified live MS Word COM Automation (`Word Version: 16.0`) with clean `word.Quit()` execution.

---

## 2. Logic Chain

From the observed templates, architecture, and requirements, we deduce the following integration blueprint:

### 2.1 Complete Systems Mapping & Route Table

| ID | Source Filename (`New folder`) | Destination Filename (`templates_docx/`) | System Key (`report_type`) | Route URL | Template HTML | System Title / Type |
|---|---|---|---|---|---|---|
| 1 | `PP-05_02 Job Traveller Card.docx` | `PP-05_02 Job Traveller Card.docx` | `job_traveller_card` | `/job-traveller-card` | `job_traveller_card.html` | Job Traveller Card |
| 2 | `PP-05_04 Batching System.docx` | `PP-05_04 Batching System.docx` | `batching_system` | `/batching-system` | `batching_system.html` | Batching / Bagging System |
| 3 | `PP-05_05 Remote Indicator.docx` | `PP-05_05 Remote Indicator.docx` | `remote_indicator` | `/remote-indicator` | `remote_indicator.html` | Remote Indicator |
| 4 | `PP-05_06 Digital Indicator.docx` | `PP-05_06 Digital Indicator.docx` | `digital_indicator` | `/digital-indicator` | `digital_indicator.html` | Digital Indicator / Weighing System |
| 5 | `PP-05_07 Weigh Feeder.docx` | `PP-05_07 Weigh Feeder.docx` | `weigh_feeder` | `/weigh-feeder` | `weigh_feeder.html` | Weigh Feeder / Screw Feeder |
| 6 | `PP-05_08 Crane Scale.docx` | `PP-05_08 Crane Scale.docx` | `crane_scale` | `/crane-scale` | `crane_scale.html` | Crane Scale |
| 7 | `PP-05_09 Signal Conditioner.docx` | `PP-05_09 Signal Conditioner.docx` | `signal_conditioner` | `/signal-conditioner` | `signal_conditioner.html` | Signal Conditioner |
| 8 | `PP-05_10 tRIP sAFE.docx` | `PP-05_10 tRIP sAFE.docx` | `trip_safe` | `/trip-safe` | `trip_safe.html` | Trip Safe |
| 9 | `PP-05_11 Vibration Switch.docx` | `PP-05_11 Vibration Switch.docx` | `vibration_switch` | `/vibration-switch` | `vibration_switch.html` | Vibration Switch |
| 10 | `PP-05_12 ACC mV.docx` | `PP-05_12 ACC mV.docx` | `acc_mv` | `/acc-mv` | `acc_mv.html` | Accelerometer mV (PG503M9/PG045M0) |
| 11 | `PP-05_13 ACC Charge.docx` | `PP-05_13 ACC Charge.docx` | `acc_charge` | `/acc-charge` | `acc_charge.html` | Accelerometer Charge (PG109M0/PG114M0) |
| 12 | `PP-05_14 Vibration Meter.docx` | `PP-05_14 Vibration Meter.docx` | `vibration_meter` | `/vibration-meter` | `vibration_meter.html` | Vibration Meter |
| 13 | `PP-05_15 Charge Amplifier.docx` | `PP-05_15 Charge Amplifier.docx` | `charge_amplifier` | `/charge-amplifier` | `charge_amplifier.html` | Charge Amplifier / Converter |
| 14 | `PP-05_16 Inprocess.docx` | `PP-05_16 Inprocess.docx` | `inprocess` | `/inprocess` | `inprocess.html` | In-Process Rejection Register |
| 15 | `PP-05_18_A ODD System.docx` | `PP-05_18_A ODD System.docx` | `odd_system` | `/odd-system` | `odd_system.html` | ODD System (Obstacle Detection) |
| 16 | `PP-05_18_B DD System.docx` | `PP-05_18_B DD System.docx` | `dd_system` | `/dd-system` | `dd_system.html` | DD System (Derailment Detection) |
| 17 | `PP-05_19 Work Instructions.docx` | `PP-05_19 Work Instructions.docx` | `work_instructions` | `/work-instructions` | `work_instructions.html` | Work Instructions Document |
| 18 | `PP-05_20 Performance Index.docx` | `PP-05_20 Performance Index.docx` | `performance_index` | `/performance-index` | `performance_index.html` | Performance Index Record |
| 19 | `PP-05_21 Performance Delay Analysis.docx` | `PP-05_21 Performance Delay Analysis.docx` | `performance_delay_analysis` | `/performance-delay-analysis` | `performance_delay_analysis.html` | Performance Delay Analysis |
| 20 | `PP-05_22 Equipment List.docx` | `PP-05_22 Equipment List.docx` | `equipment_list` | `/equipment-list` | `equipment_list.html` | Equipment / Instruments List |
| 21 | `PP-05_24 Loss in Weigh Feeder.docx` | `PP-05_24 Loss in Weigh Feeder.docx` | `loss_in_weigh_feeder` | `/loss-in-weigh-feeder` | `loss_in_weigh_feeder.html` | Loss in Weight Feeder |

*(Plus existing active systems: `PP-05_03 Belt Scale.docx` -> `/belt-scale` and `PP-05_17 Miscellaneous Items.docx` -> `/misc-report`)*

---

### 2.2 Form Field Schemas & Payload Specification

Each reporting system follows a structured JSON payload submitted to `/api/submit`:

```json
{
  "report_type": "<system_key>",
  "user_name": "Field Technician",
  "job_no": "JOB-2026-001",
  "customer": "Steel Dynamics Ltd",
  "capacity": "500 TPH",
  "date": "2026-08-22",
  "tested_by": "John Doe",
  "approved_by": "Jane Smith (HOD PDN)",
  ...system_specific_fields
}
```

#### Detailed System Field Specifications:
1. **`job_traveller_card`**:
   - Header: `job_no`, `customer`, `item_desc`, `qty`, `order_ref`, `delivery_date`.
   - Process Steps Table: Array of rows with `sl_no`, `operation_desc`, `target_date`, `qty_passed`, `qty_rejected`, `operator_sign`, `qc_sign`, `remarks`.
   - Signatures: `prepared_by`, `approved_by`, `date`.
2. **`batching_system`**:
   - Header: `job_no`, `customer`, `system_desc`, `capacity`, `batch_cycle_time`.
   - Equipment Specs Table: Controller Model/Serial, Load Cell Model/Serial, Junction Box, Power Supply, Display.
   - Tests Table: Supply Voltage, Reference Voltage, Calibration (Zero, Span, Repeatability), Relay / Valve Actuation, Error %.
   - Signatures: `tested_by`, `approved_by`, `date`, `instrument_used`.
3. **`remote_indicator`**:
   - Header: `job_no`, `customer`, `capacity`, `rate`, `load`, `speed`, `totalizer`.
   - Table 0: `short_check` (Line & Neutral, Neutral & Earth, Line & Earth).
   - Table 1 (Routine Tests 1-9): Specified vs Actual values for Power Supply, Display, Baud Rate, Comm Protocol, Range Check, Data Integrity.
   - Signatures: `instrument_used`, `tested_by`, `approved_by`, `date`.
4. **`digital_indicator`**:
   - Header: `job_no`, `customer`, `system`, `capacity`, `tag_no`, `resolution_l`.
   - Table 0: Load Indicator specs, Sensor specs, Remote specs, Junction Box specs.
   - Table 1: `short_check`.
   - Table 2: Routine tests (Supply voltage, Excitation voltage, Display test, Zero/Span, Repeatability).
   - Table 3: Calibration Load Matrix (13 load levels: 0 to 110% capacity, Load Cell mV readings 1 to 4).
   - Table 4: Functional checks (Tare, Net/Gross, Peak Hold, Comm, Relay outputs).
   - Signatures: `instrument_used`, `tested_by`, `approved_by`, `date`, `remarks`.
5. **`weigh_feeder`**:
   - Header: `job_no`, `customer`, `capacity`, `material`, `resolution_l`, `resolution_s`, `resolution_r`, `resolution_t`, `chain_weight`, `operating_range`.
   - Table 0: Equipment specs (Feeder, Controller, Load Cell, Tacho/Proximity, Junction Box).
   - Table 1: Drive, Motor, Gearbox, RAL details.
   - Table 2: Electrical & Safety tests.
   - Table 3: Belt Dimensions (`belt_length`, `belt_width`).
   - Table 4: Speed Calibration Matrix (Drive % vs Calc Speed vs Measured Speed).
   - Table 5: Volumetric & Gravimetric Rate Tests (Set Rate, Actual Min/Max/Avg, Load Kg/m, Totalizer 6min).
   - Table 6: Functionality checks (Local/Remote, Digital inputs, PF contacts, Analog I/O, Comm).
   - Signatures: `tested_by`, `approved_by`, `date`.
6. **`crane_scale`**:
   - Header: `job_no`, `customer`, `capacity`, `stamp_no`, `load_cell_model`, `load_cell_serial`, `resolution`, `battery_voltage`, `low_batt_cutoff`, `remote_range`.
   - Table 0: Crane scale, Battery charger, Remote, Hook, Bow shackle specs.
   - Table 1: Linearity and load test results.
   - Signatures: `tested_by`, `approved_by`, `date`.
7. **`signal_conditioner`**:
   - Header: `job_order_no`, `customer`, `sc_model`, `sc_serial`, `lc_model`, `lc_serial`, `power_annunciation`, `error_pct`, `multimeter_used`.
   - Table 0: Linearity Test Matrix (7 load points: Input Load kg/T or mV vs Output Current/Voltage 4-20mA / 0-10V).
   - Signatures: `tested_by`, `approved_by`, `date`.
8. **`trip_safe`**:
   - Header: `job_order_no`, `customer`, `ts_model`, `ts_serial`, `lc_model`, `lc_serial`, `trip_error_pct`, `pf_contact_check`, `led_annunciation`.
   - Table 0: Linearity & Trip Test Matrix (8 points: Load %, Load kg/T, Loadcell output mV, LED level, Relay state).
   - Signatures: `tested_by`, `approved_by`, `date`.
9. **`vibration_switch`**:
   - Header: `job_order_no`, `customer`, `error_pct`.
   - Table 0: Vibration Switch Model/Serial & Accelerometer Model/Serial.
   - Table 1: Linearity Test at 50 Hz (5 set points: Set Level Velocity vs Trip Level Velocity).
   - Table 2: Frequency Response Matrix (Frequencies 10Hz to 1000Hz across 3 set levels).
   - Signatures: `tested_by`, `approved_by`, `date`.
10. **`acc_mv`**:
    - Header: `job_no`, `customer`, `serial_no`, `test1_mean`, `freq_mean`, `charge_sens`, `trans_sens`.
    - Table 0: Axial Sensitivity Linearity Test (10 Acceleration levels: g vs V mV pk-pk vs Sensitivity mV/g).
    - Table 1: Frequency Response (10Hz to 10kHz).
    - Table 2: Transverse Sensitivity.
    - Table 3: Summary table.
    - Signatures: `tested_by`, `approved_by`, `date`.
11. **`acc_charge`**:
    - Header: `job_no`, `customer`, `serial_no`, `charge_amp_gain` (default `1.022 mV/pC`), `axial_mean`, `freq_mean`, `charge_sens`.
    - Table 0: Axial Sensitivity Linearity (g vs V1 mV vs Charge pC vs Sensitivity pC/g).
    - Table 1: Frequency Response (10Hz to 10kHz).
    - Table 2: Transverse Sensitivity.
    - Table 3: Summary.
    - Signatures: `tested_by`, `approved_by`, `date`.
12. **`vibration_meter`**:
    - Header: `job_order_no`, `customer`.
    - Table 0: Equipment specs.
    - Table 1: Full Calibration Matrix across Acceleration (m/s²), Velocity (cm/s), Displacement (mm) across multiple frequencies.
    - Signatures: `tested_by`, `approved_by`, `date`.
13. **`charge_amplifier`**:
    - Header: `job_order_no`, `customer`, `ca_model`, `ca_serial`, `acc_model`, `acc_serial`, `spec_freq_range`, `spec_max_input`, `spec_max_output`, `conversion_factor`, `error_pct`.
    - Table 0: Unit specs.
    - Table 1: Linearity Test at 50Hz (Input Signal g vs Vo mV vs Conversion Factor Vo/g).
    - Table 2: Frequency Response (Frequencies 10Hz to 10kHz).
    - Signatures: `tested_by`, `approved_by`, `date`.
14. **`inprocess`**:
    - Header: `title`, `register_period`.
    - Table 0: In-Process Rejection Table (Rows: `date`, `job_no`, `customer`, `item_desc`, `qty`, `failure_nature`, `pdn_engineer`, `hod_pdn_sign`, `qc_sign`).
15. **`odd_system`**:
    - Header: `job_no`, `customer`, `system` ("Obstacle Detection Derailment Detection System").
    - Narrative Table: ODD Trip Check, DDD Trip Check, Functionality Check (ODDD Trip Output Y/N, DDD Trip Output Y/N, Load Cell Failure Card Y/N, Power Supply Failure Card Y/N), Remarks.
    - Signatures: `tested_by`, `approved_by`, `date`.
16. **`dd_system`**:
    - Header: `job_no`, `customer`, `system` ("Derailment Detection System").
    - Narrative Table: DD1 Trip Check, DD2 Trip Check, Functionality Check (DD1 Trip Output Y/N, DD2 Trip Output Y/N, Loadcell Failure Card Y/N, Power Supply Failure Card Y/N), Remarks.
    - Signatures: `tested_by`, `approved_by`, `date`.
17. **`work_instructions`**:
    - Header: `doc_no`, `rev_no`, `date`, `page_no`, `instruction_title`, `scope`, `procedure_steps`.
    - Table 0: Doc Control Header.
    - Table 1: Sign-off (Prepared by, Verified by, Approved by).
18. **`performance_index`**:
    - Header: `month_year`, `prepared_by`, `approved_by`, `date`.
    - Table 0: Monthly Metrics (`month`, `jobs_scheduled`, `jobs_completed`, `pct_achieved`).
19. **`performance_delay_analysis`**:
    - Header: `month_year`, `total_scheduled`, `total_executed`, `total_delay`, `prepared_by`, `approved_by`, `date`.
    - Table 0: Delay Breakdown (`rework_rejections_pct`, `manpower_pct`, `shortage_pct`, `other_pct`).
    - Table 1: Delay Itemization (`sl_no`, `jo_no`, `customer`, `department`, `reason`).
20. **`equipment_list`**:
    - Header: `title`, `revision_date`.
    - Table 0: Equipment Inventory (`sl_no`, `item_desc`, `ref_no`, `calib_date`, `due_date`, `calib_agency`, `remarks`).
21. **`loss_in_weigh_feeder`**:
    - Header: `job_no`, `customer`, `capacity`, `material`, `resolution_load`, `resolution_rate`, `resolution_totalizer`, `span_rate`, `p_val`, `i_val`, `d_val`, `ff_time`, `interval_time`, `remarks`, `instrument_used`.
    - Table 0: Equipment specs (Feeder, Controller, Load Cell, Junction Box).
    - Table 1: AC/DC Drive, Screw Motor & Gearbox, Agitator Motor & Gearbox.
    - Table 2: Electrical and Accuracy tests.
    - Table 3: Rate Accuracy Matrix (Set Rate vs Achieved Rate vs Error % vs Current mA).
    - Table 4: Control mode & comm functionality checks.
    - Signatures: `tested_by`, `approved_by`, `date`.

---

### 2.3 DOCX Generation Architecture & Blank Replacement Engine

Existing templates rely on tabular structures, colon delimiters (`:`), tab indentations, and blank cells.

```
+-------------------------------------------------------------------------+
|                  Client POST JSON Payload                               |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                docx_generator.generate_docx_record(data, path)          |
|                                                                         |
|  Dispatcher:                                                            |
|    - 'belt_scale'                  -> generate_belt_scale_docx          |
|    - 'misc'                        -> generate_misc_report_docx         |
|    - 'batching_system'             -> generate_batching_system_docx     |
|    - 'digital_indicator'           -> generate_digital_indicator_docx   |
|    - 'weigh_feeder'                -> generate_weigh_feeder_docx        |
|    - ... [21 dedicated generator functions or modular generators]       |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|         python-docx Run & Cell Injection Engine                         |
|  - Safe run text substitution preserving bold / font size (8.5 - 10pt)  |
|  - Dynamic / fixed row table population with cell padding               |
|  - XML trailing empty paragraph removal for strict 1-page PDF layout    |
|  - Saved to TESTING OUTPUTS/<safe_filename>.docx                        |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|         win32com MS Word COM Automation (convert_docx_to_pdf)           |
|  - pythoncom.CoInitialize()                                             |
|  - word = win32com.client.DispatchEx("Word.Application")                |
|  - word.DisplayAlerts = 0, Visible = False                              |
|  - doc = word.Documents.Open(abs_docx)                                  |
|  - doc.SaveAs(abs_pdf, FileFormat=17)                                   |
|  - doc.Close(False), word.Quit(), pythoncom.CoUninitialize()            |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|         SQLite Database Record & Client Download Response               |
|  - database.save_record(...)                                            |
|  - Return JSON { status: 'success', pdf_filename, pdf_download_url }    |
+-------------------------------------------------------------------------+
```

---

### 2.4 Automated Testing Architecture (`verify_systems.py`)

The automated testing script `verify_systems.py` must run autonomously and validate all 20+ systems without manual intervention.

#### Key Architectural Components of `verify_systems.py`:
1. **Execution Dual-Mode**:
   - **Mode A (Live Server)**: If Flask is running on `http://127.0.0.1:5000`, test via `requests.Session()` after authenticating at `/login`.
   - **Mode B (In-Process Test Client)**: If no live server is running, instantiate `app.test_client()` with an authenticated session (`session['user'] = {'username': 'admin', 'role': 'Admin', 'full_name': 'System Admin'}`).
2. **Comprehensive Fixture Library**:
   - Pre-configured valid mock payloads for each of the 21 new systems (+ 2 existing systems).
3. **Multi-Stage Verification Per System**:
   - **Stage 1 (HTTP Response)**: Assert HTTP 200 OK and JSON `{ "status": "success", "pdf_filename": "..." }`.
   - **Stage 2 (DOCX Disk Verification)**: Assert `.docx` file exists in `EXPORTS_DIR` and `size > 5,000 bytes`.
   - **Stage 3 (PDF Disk Verification)**: Assert `.pdf` file exists in `EXPORTS_DIR` and `size > 10,000 bytes`.
   - **Stage 4 (Zero Unfilled Placeholders Scan)**:
     - Load generated `.docx` via `python-docx`.
     - Scan all paragraph texts, table cells, and header/footer runs against forbidden placeholder patterns:
       - Jinja tags: `r'\{\{.*?\}\}'`
       - Form underlines / blanks: `r'\[\s*_{2,}\s*\]'`, `r'_{3,}'`
       - Placeholder keywords: `r'\b(TODO|TBD|PLACEHOLDER|NULL|UNDEFINED|XXX)\b'`
       - Unfilled label colons: checking if field prefixes (e.g. `JOB No.:`, `CUSTOMER:`) are immediately followed by empty strings or only whitespace.
     - Assert count of matched unpopulated placeholders == 0.
4. **Structured Console Reporting**:
   - Formatted table displaying each test case, status, file paths, and placeholder check result.
   - Clean summary footer and return code (`sys.exit(0)` on 100% pass, `sys.exit(1)` on any failure).

---

## 3. Caveats

1. **Master Document Distinction**: `PP - 05 PRODUCTION RECORDS 14_11_2024.docx` is a combined quality system compilation and should remain in `New folder` as an archive, rather than an interactive form.
2. **Non-DOCX Files**: `PP-05_01 Production Plan.xlsx` and `PP-05_23 Job Card.pdf` do not have `.docx` templates in `New folder`. If required later, `.docx` templates would need to be synthesized or Excel/PDF generators implemented.
3. **COM Automation Concurrency**: MS Word COM is single-threaded per process. In production / test scripts, `pythoncom.CoInitialize()` and `pythoncom.CoUninitialize()` must wrap each conversion, and `DisplayAlerts=0` must prevent modal popups from blocking the process.
4. **Narrative Table Formatting (ODD/DD Systems)**: `PP-05_18_A` and `PP-05_18_B` contain single-cell narrative tables rather than standard grid tables. Generator logic for these systems must reconstruct the cell's paragraphs or replace exact run tokens rather than iterating over grid rows.

---

## 4. Conclusion

- **Migration Ready**: All 21 new `.docx` templates are validated and ready to be copied into `templates_docx/`.
- **System Routing**: Clean 1-to-1 mapping established for all 21 new systems + 2 existing systems (total 23 functional reporting systems) matching `portal.html`.
- **Unified Backend API**: Retaining `/api/submit` with `report_type` routing ensures seamless client-side submission and backwards compatibility.
- **Automated Verification**: The proposed `verify_systems.py` architecture provides full coverage: HTTP 200 checks, dual DOCX/PDF export verification, and deep AST-level zero-unfilled placeholder validation.

---

## 5. Verification Method

To independently verify this architectural specification:

1. **Template Integrity & Structure**:
   ```bash
   python -c "import docx, os; [docx.Document(os.path.join('New folder', f)) for f in os.listdir('New folder') if f.endswith('.docx')]"
   ```
2. **MS Word COM Conversion**:
   ```bash
   python -c "import win32com.client, pythoncom; pythoncom.CoInitialize(); w = win32com.client.DispatchEx('Word.Application'); print('Word version:', w.Version); w.Quit(); pythoncom.CoUninitialize()"
   ```
3. **Automated Systems Test Execution**:
   Once implemented by the development team, run:
   ```bash
   python verify_systems.py
   ```
   **Invalidation Conditions**:
   - Any POST request returns non-200 or `status != 'success'`.
   - Any `.docx` or `.pdf` file is missing or has 0 bytes.
   - Any unpopulated placeholder token (e.g. `{{...}}`, `_____`, `TODO`) is detected in the generated `.docx` files.

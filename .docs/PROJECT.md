# Project: 20 New Reporting Systems in Flask Web Application

## Architecture
- **Web Framework**: Flask 3.1.3 on Python 3.12+ (Windows Desktop Application environment with MS Word COM automation).
- **Backend Document Pipeline**:
  - `templates_docx/`: Directory containing canonical Word (.docx) templates.
  - `docx_generator.py`: Module responsible for loading `.docx` templates, performing AST run and table cell replacement, preserving Pt font sizes and formatting, trimming trailing empty paragraphs, and invoking MS Word COM (`win32com.client.DispatchEx("Word.Application")`) via `convert_docx_to_pdf` to produce pixel-perfect single-page/multi-page PDFs.
  - `TESTING OUTPUTS/` (`EXPORTS_DIR`): Disk location for all generated `.docx` and `.pdf` files.
  - `database.py`: SQLite 3 database (`production_reports.db`) tracking user sessions, permissions, and audit log records with raw JSON payloads.
- **Frontend UI Architecture**:
  - `static/css/style.css`: Unified Pristine Light Enterprise theme (`--bg-canvas: #f8fafc`, `--card-bg: #ffffff`, `--blue-primary: #0284c7`, Outfit + Plus Jakarta Sans fonts).
  - `templates/portal.html`: Navigation hub featuring 24 interactive cards for all production systems.
  - `templates/<system_name>.html`: Individual reporting form templates featuring responsive styling, header metadata, system-specific test tables, "Fill Sample Data" button, AJAX submission to `/api/submit`, and real-time PDF download.
- **Automated Verification Harness**:
  - `verify_systems.py`: Independent automated test suite executing POST submissions across all 23 systems, verifying HTTP 200 responses, confirming dual DOCX and PDF disk exports, and performing deep AST scans to guarantee zero remaining unfilled placeholders (`{{...}}`, `_____`, `TODO`, `[ ___ ]`).

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Template Migration | Move 20+ `.docx` templates from `New folder` to `templates_docx` | M1 | Survey |
| 2 | Backend Docx Population Engine | Implement python-docx population logic for all 20 new systems | M1 | Survey |
| 3 | Backend PDF Conversion Pipeline | Integrate win32com MS Word COM PDF generation for all 20 systems | M1 | Survey |
| 4 | Job Traveller Card Form & Route | Route `/job-traveller-card`, HTML `job_traveller_card.html`, generator logic | M2 | Survey |
| 5 | Batching System Form & Route | Route `/batching-system`, HTML `batching_system.html`, generator logic | M2 | Survey |
| 6 | Remote Indicator Form & Route | Route `/remote-indicator`, HTML `remote_indicator.html`, generator logic | M2 | Survey |
| 7 | Digital Indicator Form & Route | Route `/digital-indicator`, HTML `digital_indicator.html`, generator logic | M2 | Survey |
| 8 | Weigh Feeder Form & Route | Route `/weigh-feeder`, HTML `weigh_feeder.html`, generator logic | M2 | Survey |
| 9 | Crane Scale Form & Route | Route `/crane-scale`, HTML `crane_scale.html`, generator logic | M2 | Survey |
| 10 | Signal Conditioner Form & Route | Route `/signal-conditioner`, HTML `signal_conditioner.html`, generator logic | M2 | Survey |
| 11 | Trip Safe Form & Route | Route `/trip-safe`, HTML `trip_safe.html`, generator logic | M2 | Survey |
| 12 | Vibration Switch Form & Route | Route `/vibration-switch`, HTML `vibration_switch.html`, generator logic | M2 | Survey |
| 13 | ACC mV Form & Route | Route `/acc-mv`, HTML `acc_mv.html`, generator logic | M2 | Survey |
| 14 | ACC Charge Form & Route | Route `/acc-charge`, HTML `acc_charge.html`, generator logic | M2 | Survey |
| 15 | Vibration Meter Form & Route | Route `/vibration-meter`, HTML `vibration_meter.html`, generator logic | M2 | Survey |
| 16 | Charge Amplifier Form & Route | Route `/charge-amplifier`, HTML `charge_amplifier.html`, generator logic | M2 | Survey |
| 17 | Inprocess Register Form & Route | Route `/inprocess-register`, HTML `inprocess.html`, generator logic | M2 | Survey |
| 18 | ODD System Form & Route | Route `/odd-system`, HTML `odd_system.html`, generator logic | M2 | Survey |
| 19 | DD System Form & Route | Route `/dd-system`, HTML `dd_system.html`, generator logic | M2 | Survey |
| 20 | Work Instructions Form & Route | Route `/work-instructions`, HTML `work_instructions.html`, generator logic | M2 | Survey |
| 21 | Performance Index Form & Route | Route `/performance-index`, HTML `performance_index.html`, generator logic | M2 | Survey |
| 22 | Performance Delay Analysis Form & Route | Route `/performance-delay-analysis`, HTML `performance_delay_analysis.html`, generator logic | M2 | Survey |
| 23 | Equipment List Form & Route | Route `/equipment-list`, HTML `equipment_list.html`, generator logic | M2 | Survey |
| 24 | Loss in Weigh Feeder Form & Route | Route `/loss-in-weigh-feeder`, HTML `loss_in_weigh_feeder.html`, generator logic | M2 | Survey |
| 25 | Portal Hub Navigation Updates | Update `portal.html` cards from 'Coming Soon' to active links for all 20 systems | M2 | Survey |
| 26 | Automated Verification Script (`verify_systems.py`) | Autonomous end-to-end test suite testing all 20 systems for HTTP 200, DOCX/PDF export, and 0 unfilled placeholders | E2E / M3 | Survey |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Suite | Develop `verify_systems.py` test harness, fixture library for all 23 systems, and test assertions | none | COMPLETED |
| M1 | Backend Template Migration & Generation Logic | Move templates to `templates_docx/`, implement generator functions in `docx_generator.py` for all 23 systems, verify COM PDF generation | none | COMPLETED |
| M2 | Frontend Forms, Portal Hub & Flask Routing | Create 23 HTML templates matching `misc_report.html`, register 23 routes in `app.py`, update `portal.html` | M1 | COMPLETED |
| M3 | End-to-End Integration, Testing Pass & Verification Gate | Run full test suite (`verify_systems.py`), pass 100% of tests (23/23 PASSED) | E2E, M1, M2 | COMPLETED |

---

## Interface Contracts

### POST `/api/submit` Request & Response Contract
- **Request Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "report_type": "<system_key>",
  "user_name": "Field Technician",
  "job_no": "JOB-2026-001",
  "customer": "Customer Name",
  "capacity": "500 TPH",
  "date": "2026-08-22",
  "tested_by": "Operator Name",
  "approved_by": "Approver Name",
  "...": "system-specific fields and tables"
}
```
- **Response Headers**: `Content-Type: application/json`
- **Response Body (Success)**:
```json
{
  "status": "success",
  "record_id": 123,
  "docx_filename": "System_Name_JOB01_User_20260822_120000.docx",
  "pdf_filename": "System_Name_JOB01_User_20260822_120000.pdf",
  "pdf_download_url": "/download/System_Name_JOB01_User_20260822_120000.pdf"
}
```

### Generator Dispatcher Contract (`docx_generator.py`)
- `generate_docx_record(data: dict, output_path: str) -> str`:
  - Inspects `data.get("report_type")`.
  - Dispatches to corresponding system generator function.
  - Fills all runs, paragraphs, and tables in the respective template from `templates_docx/`.
  - Preserves formatting, font sizing (Pt 8.5 to 10.0), alignment, and strips trailing empty paragraphs.
  - Writes populated document to `output_path`.
- `convert_docx_to_pdf(docx_path: str, pdf_path: str) -> str`:
  - Invokes `win32com.client.DispatchEx("Word.Application")` wrapped with `pythoncom.CoInitialize()` / `CoUninitialize()`.
  - Exports PDF format (wdFormatPDF = 17) to `pdf_path`.

---

## Code Layout
- `app.py`: Route definitions for portal, individual system views (`GET /<system-route>`), authentication, and REST endpoints (`POST /api/submit`, `GET /api/records`, `GET /download/<filename>`).
- `docx_generator.py`: Central document generation and PDF conversion engine.
- `database.py`: SQLite persistence and query helper methods.
- `templates_docx/`: Storage directory for all 20+ `.docx` templates.
- `templates/`: HTML Jinja templates for all systems (`portal.html`, `login.html`, `admin_users.html`, `index.html`, `misc_report.html`, and 20 new system HTML files).
- `static/`:
  - `static/css/style.css`: Global dark theme styling.
  - `static/js/app.js`: Client side utilities.
- `verify_systems.py`: Automated end-to-end verification script for all systems.
- `TESTING OUTPUTS/`: Output directory for generated `.docx` and `.pdf` files.


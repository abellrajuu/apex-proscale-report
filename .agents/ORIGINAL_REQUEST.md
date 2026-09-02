# Original User Request

## Initial Request — 2026-08-22T16:50:20+05:30

Implement frontend forms and backend PDF/Docx generation logic for 20 new reporting systems in the existing Flask application. The new systems are based on provided Word (.docx) templates located in the "New folder".

Requirements:
- R1. Backend Document Mapping: Move 20 `.docx` templates from "New folder" to "templates_docx" directory. Implement Python logic to populate all placeholders/blank lines.
- R2. Frontend Forms and Routes: Create individual HTML templates and Flask routes (in app.py) for all 20 systems matching template fields, styled consistently with misc_report.html (dark theme).
- R3. Automated Testing Script: Create `verify_systems.py` testing all 20 POST endpoints, confirming HTTP 200 OK, exports of both `.docx` and `.pdf` for each system, and zero remaining unfilled placeholders.

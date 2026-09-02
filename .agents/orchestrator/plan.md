# Project Orchestration Plan: 20 New Reporting Systems

## Objective
Implement backend document generation (DOCX/PDF) and frontend dark-themed forms/routes in the existing Flask application for 20 new reporting systems based on Word templates in "New folder", verified via automated testing with `verify_systems.py`.

## Phases

### Phase 0: Survey & Architecture
1. Dispatch 3 parallel Explorers:
   - Explorer 1: Inspect existing Flask application architecture (`app.py`, helper modules, PDF/DOCX generation mechanism, LibreOffice/docx2pdf/weasyprint/etc. integration, and `misc_report.html` styling).
   - Explorer 2: Inspect all 20 `.docx` files in "New folder", extract placeholders, table structures, blank lines, and system names.
   - Explorer 3: Analyze template moving/mapping requirements, input field requirements for all 20 systems, route naming conventions, and test requirements for `verify_systems.py`.
2. Synthesize findings into `PROJECT.md` with full Feature Inventory, Module Boundaries, Code Layout, Interface Contracts, and Milestones.

### Phase 1: Dual Track Execution
- **E2E Testing Track**: Build `verify_systems.py` test harness & test cases testing all 20 POST endpoints for HTTP 200, valid .docx and .pdf output, and 0 unfilled placeholders.
- **Implementation Track**:
  - Milestone 1: Template Migration & Backend Document Generation Logic for the 20 systems.
  - Milestone 2: Frontend HTML Templates & Flask Route Definitions for all 20 systems matching `misc_report.html` styling.
  - Milestone 3: Integration, PDF Generation, and Verification with `verify_systems.py`.

### Phase 2: Verification & Review Gates
- Reviewers, Challengers, and Forensic Auditors verify code, test passes, absence of unfilled placeholders, and integrity.
- Final Acceptance: 100% of E2E tests passing and clean audit.

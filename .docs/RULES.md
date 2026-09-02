# Production Report & Documentation System - Project Rules & Specifications

> **File Location**: [`RULES.md`](file:///C:/Users/abell/OneDrive/Desktop/TEST%20REPORT%20PRODUCTION%20final/RULES.md) / [`RULES.txt`](file:///C:/Users/abell/OneDrive/Desktop/TEST%20REPORT%20PRODUCTION%20final/RULES.txt)  
> **Last Updated**: August 23, 2026

---

## 0. Mandatory Pre-Submit Verification Protocol

- **Rule Review Before Submission**:  
  Before completing any task or delivering final outputs, the assistant **MUST** run through all rules in [`RULES.txt`](file:///C:/Users/abell/OneDrive/Desktop/TEST%20REPORT%20PRODUCTION%20final/RULES.txt) / [`RULES.md`](file:///C:/Users/abell/OneDrive/Desktop/TEST%20REPORT%20PRODUCTION%20final/RULES.md) and verify that **none are missed or violated**.
  
- **Continuous Rule Maintenance**:  
  Every time the user shares new ideas, directives, or updates, the assistant **MUST** immediately record and update [`RULES.txt`](file:///C:/Users/abell/OneDrive/Desktop/TEST%20REPORT%20PRODUCTION%20final/RULES.txt) and [`RULES.md`](file:///C:/Users/abell/OneDrive/Desktop/TEST%20REPORT%20PRODUCTION%20final/RULES.md) to keep them current.

---

## 1. Alstom vs Production System Categorization

- **Alstom / Controllers Category (Exactly 2 Controllers Only)**:
  - Under the ALSTOM / Controllers category, include **ONLY**:
    1. **ODD System Controller** (`PP-05_18_A ODD System` / `/odd-system`)
    2. **DD System Controller** (`PP-05_18_B DD System` / `/dd-system`)

- **Production Systems Category (All Other Production Systems)**:
  - **ALL other production reporting systems** (Weighing System, Belt Scale, Weigh Feeder, Digital Indicator, Remote Indicator, Signal Conditioner, Crane Scale CWS, Batching System, Loss in Weigh Feeder, Miscellaneous Report, Trip Safe, Vibration Switch, ACC mV, ACC Charge, Vibration Meter, Charge Amplifier) belong under **PRODUCTION SYSTEMS**.

---

## 2. Mobile Stepper Bar & Table Container Responsiveness (Zero Overflow Cut-Off)

- **Mobile Stepper Bar Scroll & Wrap**:
  - On mobile screens (max-width 768px), the top wizard stepper bar (`.stepper-bar`) **MUST** allow smooth horizontal touch scrolling (`overflow-x: auto; flex-wrap: nowrap;`) so all steps fit cleanly without being clipped.

- **Inner Table Touch-Swiping Containment**:
  - The parent card **MUST** remain 100% contained within mobile screen boundaries, while the table container (`.table-responsive`) enables smooth horizontal touch scrolling inside.

---

## 3. Premium Android Native Mobile App UI & Bottom Navigation Bar

- **Native Mobile App Top Header & Bottom Tab Bar**:
  - Floating top navigation bar and fixed native Android bottom tab bar (`Home`, `Reports`, `Get APK`, `Log Out`) for 1-tap mobile navigation.

---

## 4. CWS (Crane Scale System) Single-Page Form Specification

- **Single-Page All-in-One Layout for CWS**:
  - CWS (Crane Scale System / `crane_scale.html`) **MUST** be displayed on a **SINGLE PAGE**.
  - All section boxes and data inputs are shown together on one single scrolling page without breaking into multi-step wizard screens.

---

## 5. Universal Step-by-Step Multi-Page Form Wizard (Multi-Section Systems)

- **One Section Box Per Screen**:
  - Multi-section system forms **MUST** use the Step-by-Step Multi-Page Wizard Engine.
  - Each screen/step displays **ONLY ONE clean section box** at a time with `← Previous Step` / `Next Step →` buttons.

---

## 6. Android Modern Target SDK Compatibility (Android 14 / 15 Support)

- **Latest Android OS Target SDK Requirement**:
  - The compiled Android APK **MUST** target modern Android OS versions (`targetSdkVersion 34` for Android 14 / Android 15, `minSdkVersion 26`).

---

## 7. Admin & Dashboard Status Grid Layout (Horizontal 4-Card Row)

- **Horizontal Side-by-Side Alignment**:
  - The top dashboard status summary cards **MUST** render in a clean 4-column horizontal row (`repeat(4, 1fr)`).

---

## 8. Template Formatting Integrity (Strict Font, Size & Layout Preservation)

- **Preserve Original Template Fonts & Sizes**:
  - The generated output document **MUST** preserve the original input Word template's exact font family, font size (Pt), font color, line spacing, table cell padding, and layout structure without global font shrinking.

---

## 9. Portal Header Branding & Subtitle Specifications

- **Portal Main Header Title**:
  - The main portal heading (`/portal`) **MUST** be set to `PRODUCTION REPORTS`.
- **Portal Subtitle Removal**:
  - Do NOT display any subtext paragraph below the portal main title.

## 10. Portal Card Subtitles & Admin Labeling Specifications

- **Admin Banner Title**:
  - The admin banner heading (`/portal`) **MUST** be set to `Admin Panel` (not "Administrator Control Panel").
- **Section Heading Title**:
  - Main portal category header **MUST** be set to `REPORTS`.
## 11. System Card Badging & Report View Layout Specifications

- **PP Code Badge Removal**:
  - Do NOT show `PP-05_*` document code badges on system cards in `/portal`.
- **Card Action Buttons**:
  - System card action buttons on `/portal` **MUST** be labeled `Open System` (not "Generate PDF").
- **Report Form Clean Layout**:
  - Individual system report form pages (`/weighing-system`, `/belt-scale`, etc.) **MUST** contain only the report input form and approval controls — history tables are strictly reserved for the Admin Portal.

---

## 12. Complete Elimination of Report Archive Tables from Form Templates

- **Zero Archive Tables on System Form Pages**:
  - **ALL** system report form templates (`index.html`, `weighing_system.html`, `belt_scale.html`, `inprocess.html`, etc.) **MUST NOT** display any bottom history or report archive tables.
  - Report records and history tables are managed exclusively within the Admin Portal (`/admin/portal`).

---

## 13. System Report Form Input Visibility & Active-Step Initialization

- **Mandatory Active-Step Initialization**:
  - **EVERY** system report form template (`vibration_switch.html`, `belt_scale.html`, `weighing_system.html`, etc.) **MUST** initialize Section Box 1 with `class="section-box active-step"` so that form inputs and data entry fields are 100% visible on page load.

---

## 14. Complete Elimination of Document Code Badges (PP-05) from Headings and Titles

- **Zero PP-05 Document Codes in Titles & Forms**:
  - **ALL** template page headers, form card titles (`<h2>`), sub-headings, badges, and system cards **MUST NOT** contain any internal `PP-05` document code numbers (e.g. `PP-05/11 Form`, `PP-05/03`, etc.).
  - Titles must display clean, human-readable system names (e.g., `Vibration Switch Test Record`, `Belt Scale Test Record`, etc.).

---

### 6. Reference Material & Screenshots
- **User Reference Images:** Any screenshots or image mockups provided by the user must be saved in the `SCREENSHOTS/` directory within the network drive (`\\192.168.100.248\prdndata\ABEL\SOFTWARE BUGS\TEST REPORT\SCREENSHOTS`) for future reference and documentation tracking.
- **Naming Convention:** Use clear, descriptive names for the saved images (e.g., TRAVLLER CARD DEMO.png).

- **Recorded Screenshot**: [`SCREENSHOT_belt-scale_20260825_002947.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_belt-scale_20260825_002947.png) | Page: `/belt-scale` | Note: Automated screenshot capture test


### Screenshot Rule Directive [20260825_003129]
- **Live Screenshot**: [`SCREENSHOT_belt-scale_20260825_003129.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_belt-scale_20260825_003129.png)
- **Reference Image**: [`SCREENSHOT_belt-scale_20260825_003129.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_belt-scale_20260825_003129.png)
- **Page URL**: `/belt-scale`
- **User Feedback Directive**: Make the submit button green and increase font size to 16px


### Screenshot Rule Directive [20260825_003801]
- **Live Screenshot**: [`SCREENSHOT_portal_20260825_003801.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_portal_20260825_003801.png)
- **Reference Image**: [`SCREENSHOT_portal_20260825_003801.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_portal_20260825_003801.png)
- **Page URL**: `/portal`
- **User Feedback Directive**: CHANGE NAME TO PRODUCTION REPORTS AND REMOVE THE SELECT A CATEEOGRY TO ACESS SYSTEM REPROTS


### Screenshot Rule Directive [20260825_003948]
- **Live Screenshot**: [`SCREENSHOT_portal_20260825_003948.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_portal_20260825_003948.png)
- **Reference Image**: [`SCREENSHOT_portal_20260825_003948.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_portal_20260825_003948.png)
- **Page URL**: `/portal`
- **User Feedback Directive**: CHANGE THIS TO ADMIN PANEL


### Screenshot Rule Directive [20260825_004008]
- **Live Screenshot**: [`SCREENSHOT_portal_20260825_004008.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_portal_20260825_004008.png)
- **Reference Image**: [`SCREENSHOT_portal_20260825_004008.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_portal_20260825_004008.png)
- **Page URL**: `/portal`
- **User Feedback Directive**: REMOVE THIS


### Screenshot Rule Directive [20260825_004047]
- **Live Screenshot**: [`SCREENSHOT_portal_20260825_004047.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_portal_20260825_004047.png)
- **Reference Image**: [`SCREENSHOT_portal_20260825_004047.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_portal_20260825_004047.png)
- **Page URL**: `/portal`
- **User Feedback Directive**: CHANGE THIS TO REPORT


### Screenshot Rule Directive [20260825_004108]
- **Live Screenshot**: [`SCREENSHOT_portal_20260825_004108.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_portal_20260825_004108.png)
- **Reference Image**: [`SCREENSHOT_portal_20260825_004108.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_portal_20260825_004108.png)
- **Page URL**: `/portal`
- **User Feedback Directive**: REMOVE THESE TEXTS


### Screenshot Rule Directive [20260825_004348]
- **Live Screenshot**: [`SCREENSHOT_portal_20260825_004348.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_portal_20260825_004348.png)
- **Reference Image**: [`SCREENSHOT_portal_20260825_004348.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_portal_20260825_004348.png)
- **Page URL**: `/portal`
- **User Feedback Directive**: REMOVE THE PP STUF AND INSTED OF GENERATE PDF MAKE IT  OPEN SYSTEM


### Screenshot Rule Directive [20260825_004429]
- **Live Screenshot**: [`SCREENSHOT_weighing-system_20260825_004429.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_weighing-system_20260825_004429.png)
- **Reference Image**: [`SCREENSHOT_weighing-system_20260825_004429.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_weighing-system_20260825_004429.png)
- **Page URL**: `/weighing-system`
- **User Feedback Directive**: NO NEED TO SHOW THIS INSDE THE TEST REPROT PALCES WHO NEED ITS BRUHH AVOOD THIS FROM ALL


### Screenshot Rule Directive [20260825_012354]
- **Live Screenshot**: [`SCREENSHOT_home_20260825_012354.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_home_20260825_012354.png)
- **Reference Image**: [`SCREENSHOT_home_20260825_012354.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_home_20260825_012354.png)
- **Page URL**: `/`
- **User Feedback Directive**: I AM STILL SEEING THESE UNDER EACH REPORT I TILD U I DON ENEED THIS


### Screenshot Rule Directive [20260825_013230]
- **Live Screenshot**: [`SCREENSHOT_vibration-switch_20260825_013230.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_vibration-switch_20260825_013230.png)
- **Reference Image**: [`SCREENSHOT_vibration-switch_20260825_013230.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_vibration-switch_20260825_013230.png)
- **Page URL**: `/vibration-switch`
- **User Feedback Directive**: WHERE OS THE USER ENTRY DATA U MF FOR LOT OF SYSTEMS ITS LIKE THATTT UPDATE ITTTT


### Screenshot Rule Directive [20260825_013735]
- **Live Screenshot**: [`SCREENSHOT_vibration-switch_20260825_013735.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_vibration-switch_20260825_013735.png)
- **Reference Image**: [`SCREENSHOT_vibration-switch_20260825_013735.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_vibration-switch_20260825_013735.png)
- **Page URL**: `/vibration-switch`
- **User Feedback Directive**: WHY THIS


### Screenshot Rule Directive [20260826_180415]
- **Live Screenshot**: [`SCREENSHOT_weighing-system_20260826_180415.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_weighing-system_20260826_180415.png)
- **Reference Image**: [`SCREENSHOT_weighing-system_20260826_180415.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_weighing-system_20260826_180415.png)
- **Page URL**: `/weighing-system`
- **User Feedback Directive**: remove this


### Screenshot Rule Directive [20260826_180429]
- **Live Screenshot**: [`SCREENSHOT_weighing-system_20260826_180429.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_weighing-system_20260826_180429.png)
- **Reference Image**: [`SCREENSHOT_weighing-system_20260826_180429.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_weighing-system_20260826_180429.png)
- **Page URL**: `/weighing-system`
- **User Feedback Directive**: remove tecjinmcan in brackerts


### Screenshot Rule Directive [20260826_180444]
- **Live Screenshot**: [`SCREENSHOT_weighing-system_20260826_180444.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_weighing-system_20260826_180444.png)
- **Reference Image**: [`SCREENSHOT_weighing-system_20260826_180444.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_weighing-system_20260826_180444.png)
- **Page URL**: `/weighing-system`
- **User Feedback Directive**: no need of quality lead


### Screenshot Rule Directive [20260826_180521]
- **Live Screenshot**: [`SCREENSHOT_belt-scale_20260826_180521.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/LIVE TESTING/SCREENSHOT_belt-scale_20260826_180521.png)
- **Reference Image**: [`SCREENSHOT_belt-scale_20260826_180521.png`](file:///C:/Users/abell/OneDrive/Desktop/TEST REPORT PRODUCTION final/SCREENSHOTS/SCREENSHOT_belt-scale_20260826_180521.png)
- **Page URL**: `/belt-scale`
- **User Feedback Directive**: avpid this


### Screenshot Rule Directive [20260831_094546]
- **Live Screenshot**: [`SCREENSHOT_portal_20260831_094546.png`](file://///192.168.100.248/prdndata/ABEL/SOFTWARE BUGS/TEST REPORT/LIVE TESTING/SCREENSHOT_portal_20260831_094546.png)
- **Reference Image**: [`SCREENSHOT_portal_20260831_094546.png`](file://///192.168.100.248/prdndata/ABEL/SOFTWARE BUGS/TEST REPORT/SCREENSHOTS/SCREENSHOT_portal_20260831_094546.png)
- **Page URL**: `/portal`
- **User Feedback Directive**: no need this


### Screenshot Rule Directive [20260831_094937]
- **Live Screenshot**: [`SCREENSHOT_weighing-system_20260831_094937.png`](file://///192.168.100.248/prdndata/ABEL/SOFTWARE BUGS/TEST REPORT/LIVE TESTING/SCREENSHOT_weighing-system_20260831_094937.png)
- **Reference Image**: [`SCREENSHOT_weighing-system_20260831_094937.png`](file://///192.168.100.248/prdndata/ABEL/SOFTWARE BUGS/TEST REPORT/SCREENSHOTS/SCREENSHOT_weighing-system_20260831_094937.png)
- **Page URL**: `/weighing-system`
- **User Feedback Directive**: spelling mistake

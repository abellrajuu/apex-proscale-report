# ITEM TEMPLATE MASTER DIRECTORY

This folder contains the standardized master data templates and field requirement specifications for the 3 core industrial testing systems:

1. **Belt Scale** (`Belt_Scale_Template.xlsx` / `Belt_Scale_Data_Requirements.txt`)
2. **Digital Indicator** (`Digital_Indicator_Template.xlsx` / `Digital_Indicator_Data_Requirements.txt`)
3. **Signal Conditioner** (`Signal_Conditioner_Template.xlsx` / `Signal_Conditioner_Data_Requirements.txt`)

---

## How It Works

1. **Auto-Fetch Integration**:
   - The test report backend reads these exact parameter keys from GA drawings (`.dwg`) and Excel job cards (`.xlsx`).
   - When a user enters the **Job No** and presses **Enter**, all parameters match these field keys and auto-populate into the report.

2. **File Structure**:
   - **Column A (`PARAMETER / FIELD KEY`)**: Standardized parameter name recognized by the parser.
   - **Column B (`SAMPLE / DEFAULT VALUE`)**: Concrete, production-tested sample values.
   - **Column C (`UNIT / FORMAT`)**: Engineering units (TPH, m/s, mV/V, V DC, etc.).
   - **Column D (`DATA DESCRIPTION / AUTOMATION SOURCE`)**: Explains whether the field comes from GA drawing, ERP, factory standard, or test bench.

3. **100% Automation Goal**:
   - By feeding these parameters via Excel or GA drawing, **100% of technical specifications, calibration matrices, and checklist defaults are automated**, requiring the test engineer to only scan/type physical hardware **Serial Numbers** on the bench.

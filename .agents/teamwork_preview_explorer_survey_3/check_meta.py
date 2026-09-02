import os

templates_meta = [
    {
        "id": 1,
        "filename": "PP-05_02 Job Traveller Card.docx",
        "key": "job_traveller_card",
        "route": "/job-traveller-card",
        "template_html": "job_traveller_card.html",
        "title": "Job Traveller Card",
        "type": "Production Process Card"
    },
    {
        "id": 2,
        "filename": "PP-05_04 Batching System.docx",
        "key": "batching_system",
        "route": "/batching-system",
        "template_html": "batching_system.html",
        "title": "Batching System",
        "type": "Routine Test Record"
    },
    {
        "id": 3,
        "filename": "PP-05_05 Remote Indicator.docx",
        "key": "remote_indicator",
        "route": "/remote-indicator",
        "template_html": "remote_indicator.html",
        "title": "Remote Indicator",
        "type": "Routine Test Record"
    },
    {
        "id": 4,
        "filename": "PP-05_06 Digital Indicator.docx",
        "key": "digital_indicator",
        "route": "/digital-indicator",
        "template_html": "digital_indicator.html",
        "title": "Digital Indicator / Weighing System",
        "type": "Routine Test Record"
    },
    {
        "id": 5,
        "filename": "PP-05_07 Weigh Feeder.docx",
        "key": "weigh_feeder",
        "route": "/weigh-feeder",
        "template_html": "weigh_feeder.html",
        "title": "Weigh Feeder / Screw Feeder",
        "type": "Routine Test Record"
    },
    {
        "id": 6,
        "filename": "PP-05_08 Crane Scale.docx",
        "key": "crane_scale",
        "route": "/crane-scale",
        "template_html": "crane_scale.html",
        "title": "Crane Scale",
        "type": "Routine Test Record"
    },
    {
        "id": 7,
        "filename": "PP-05_09 Signal Conditioner.docx",
        "key": "signal_conditioner",
        "route": "/signal-conditioner",
        "template_html": "signal_conditioner.html",
        "title": "Signal Conditioner",
        "type": "Routine Test Record"
    },
    {
        "id": 8,
        "filename": "PP-05_10 tRIP sAFE.docx",
        "key": "trip_safe",
        "route": "/trip-safe",
        "template_html": "trip_safe.html",
        "title": "Trip Safe",
        "type": "Routine Test Record"
    },
    {
        "id": 9,
        "filename": "PP-05_11 Vibration Switch.docx",
        "key": "vibration_switch",
        "route": "/vibration-switch",
        "template_html": "vibration_switch.html",
        "title": "Vibration Switch",
        "type": "Test Record"
    },
    {
        "id": 10,
        "filename": "PP-05_12 ACC mV.docx",
        "key": "acc_mv",
        "route": "/acc-mv",
        "template_html": "acc_mv.html",
        "title": "Accelerometer mV (PG503M9/PG045M0)",
        "type": "Test Report"
    },
    {
        "id": 11,
        "filename": "PP-05_13 ACC Charge.docx",
        "key": "acc_charge",
        "route": "/acc-charge",
        "template_html": "acc_charge.html",
        "title": "Accelerometer Charge (PG109M0/PG114M0)",
        "type": "Test Report"
    },
    {
        "id": 12,
        "filename": "PP-05_14 Vibration Meter.docx",
        "key": "vibration_meter",
        "route": "/vibration-meter",
        "template_html": "vibration_meter.html",
        "title": "Vibration Meter",
        "type": "Test Report"
    },
    {
        "id": 13,
        "filename": "PP-05_15 Charge Amplifier.docx",
        "key": "charge_amplifier",
        "route": "/charge-amplifier",
        "template_html": "charge_amplifier.html",
        "title": "Charge Amplifier / Converter",
        "type": "Test Record"
    },
    {
        "id": 14,
        "filename": "PP-05_16 Inprocess.docx",
        "key": "inprocess",
        "route": "/inprocess",
        "template_html": "inprocess.html",
        "title": "In-Process Rejection Register",
        "type": "Register"
    },
    {
        "id": 15,
        "filename": "PP-05_18_A ODD System.docx",
        "key": "odd_system",
        "route": "/odd-system",
        "template_html": "odd_system.html",
        "title": "ODD System (Obstacle Detection Derailment Detection)",
        "type": "Test Report"
    },
    {
        "id": 16,
        "filename": "PP-05_18_B DD System.docx",
        "key": "dd_system",
        "route": "/dd-system",
        "template_html": "dd_system.html",
        "title": "DD System (Derailment Detection System)",
        "type": "Test Report"
    },
    {
        "id": 17,
        "filename": "PP-05_19 Work Instructions.docx",
        "key": "work_instructions",
        "route": "/work-instructions",
        "template_html": "work_instructions.html",
        "title": "Work Instructions",
        "type": "Process Document"
    },
    {
        "id": 18,
        "filename": "PP-05_20 Performance Index.docx",
        "key": "performance_index",
        "route": "/performance-index",
        "template_html": "performance_index.html",
        "title": "Performance Index",
        "type": "Performance Report"
    },
    {
        "id": 19,
        "filename": "PP-05_21 Performance Delay Analysis.docx",
        "key": "performance_delay_analysis",
        "route": "/performance-delay-analysis",
        "template_html": "performance_delay_analysis.html",
        "title": "Performance Delay Analysis",
        "type": "Analysis Report"
    },
    {
        "id": 20,
        "filename": "PP-05_22 Equipment List.docx",
        "key": "equipment_list",
        "route": "/equipment-list",
        "template_html": "equipment_list.html",
        "title": "List of Instruments / Equipment List",
        "type": "Inventory Register"
    },
    {
        "id": 21,
        "filename": "PP-05_24 Loss in Weigh Feeder.docx",
        "key": "loss_in_weigh_feeder",
        "route": "/loss-in-weigh-feeder",
        "template_html": "loss_in_weigh_feeder.html",
        "title": "Loss in Weight Feeder",
        "type": "Routine Test Record"
    }
]

print(f"Total new templates mapped: {len(templates_meta)}")
for t in templates_meta:
    print(f"{t['id']:2d}. {t['filename']} -> Route: {t['route']} | Key: {t['key']} | HTML: {t['template_html']}")

# DISPATCH: Milestone 1 - Backend Template Migration & Generation Logic

## 2026-08-22T16:54:58+05:30
- Working Directory: C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\.agents\teamwork_preview_worker_m1
- Original Request: C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\.agents\ORIGINAL_REQUEST.md
- Project Scope: C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\PROJECT.md

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Assigned Scope & Tasks:
1. **Template Migration**:
   - Copy/move all 21 target `.docx` templates from `New folder/` to `templates_docx/`.
   - Verify that all 21 templates exist in `templates_docx/` with exact matching names.
2. **Backend Document Generation (`docx_generator.py`)**:
   - Implement complete, genuine `python-docx` population logic for all 21 new reporting systems:
     1. `job_traveller_card` (`PP-05_02 Job Traveller Card.docx`)
     2. `batching_system` (`PP-05_04 Batching System.docx`)
     3. `remote_indicator` (`PP-05_05 Remote Indicator.docx`)
     4. `digital_indicator` (`PP-05_06 Digital Indicator.docx`)
     5. `weigh_feeder` (`PP-05_07 Weigh Feeder.docx`)
     6. `crane_scale` (`PP-05_08 Crane Scale.docx`)
     7. `signal_conditioner` (`PP-05_09 Signal Conditioner.docx`)
     8. `trip_safe` (`PP-05_10 tRIP sAFE.docx`)
     9. `vibration_switch` (`PP-05_11 Vibration Switch.docx`)
     10. `acc_mv` (`PP-05_12 ACC mV.docx`)
     11. `acc_charge` (`PP-05_13 ACC Charge.docx`)
     12. `vibration_meter` (`PP-05_14 Vibration Meter.docx`)
     13. `charge_amplifier` (`PP-05_15 Charge Amplifier.docx`)
     14. `inprocess` / `inprocess_register` (`PP-05_16 Inprocess.docx`)
     15. `odd_system` (`PP-05_18_A ODD System.docx`)
     16. `dd_system` (`PP-05_18_B DD System.docx`)
     17. `work_instructions` (`PP-05_19 Work Instructions.docx`)
     18. `performance_index` (`PP-05_20 Performance Index.docx`)
     19. `performance_delay_analysis` (`PP-05_21 Performance Delay Analysis.docx`)
     20. `equipment_list` (`PP-05_22 Equipment List.docx`)
     21. `loss_in_weigh_feeder` (`PP-05_24 Loss in Weigh Feeder.docx`)
   - Ensure every field, run, table cell, and placeholder is cleanly populated without leaving raw `_____` or `{{...}}` tokens.
   - Update `generate_docx_record(data, output_path)` to dispatch to all system generators.
   - Ensure `convert_docx_to_pdf` generates valid PDF outputs for each generated docx.
3. **Verification**:
   - Write and run a test script to generate sample DOCX and PDF files for all 21 systems in `TESTING OUTPUTS/` and verify that the files are valid and all fields are filled.
4. Report results in `handoff.md` in your working directory.

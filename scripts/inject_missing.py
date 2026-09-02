import re
import os

injections = {
    'weigh_feeder.html': ['ctrl_serial', 'lc_model', 's1', 's2'],
    'crane_scale.html': ['crane_model', 'crane_serial', 'hook_serial', 'shackle_serial', 'charger_details', 'remote_details', 'stamp_no', 'remarks', 'capacity', 'accuracy', 'resolution'],
    'job_traveller_card.html': ['chassis_start_date', 'chassis_end_date', 'chassis_inspector', 'assembly_start_date', 'assembly_end_date', 'assembly_inspector', 'wiring_start_date', 'wiring_end_date', 'wiring_inspector', 'testing_start_date', 'testing_end_date', 'testing_inspector', 'final_qc_inspector'],
    'batching_system.html': ['bch_model', 'bch_serial'],
    'loss_in_weigh_feeder.html': ['ctrl_serial']
}

for html_file, missing in injections.items():
    html_path = os.path.join('templates', html_file)
    if not os.path.exists(html_path): continue
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    injection = '<div class="section-box" style="display:block;"><div class="section-box-title"><i class="fa-solid fa-plus"></i> Auto-Injected Fields</div><div class="grid-col-2">\n'
    for m in missing:
        if f'name="{m}"' not in html and f"name='{m}'" not in html:
            injection += f'<div class="input-group"><label>{m.replace("_", " ").title()}</label><input type="text" name="{m}" id="{m}"></div>\n'
    injection += '</div></div>\n'
    
    if "Auto-Injected Fields" not in html:
        # Insert before btnSubmitForm
        html = re.sub(r'(<button[^>]+id="btnSubmitForm")', injection + r'\1', html, count=1)
        if injection not in html: # Fallback if btnSubmitForm not found
            html = re.sub(r'(<button[^>]+id="btnSubmitPDF")', injection + r'\1', html, count=1)
            
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Injected into {html_file}")

import re
import os

missing_fields = {
    'batching_system': ['bch_model', 'bch_serial'],
    'crane_scale': ['act_1', 'act_2', 'act_3', 'charger_details', 'crane_model', 'crane_serial', 'hook_serial', 'remarks', 'remote_details', 'shackle_serial', 'stamp_no'],
    'job_traveller_card': ['assembly_doc_no', 'assembly_feedback', 'assembly_inspector', 'chassis_end', 'chassis_name', 'chassis_start', 'customer_name', 'final_assembly_end', 'final_assembly_name', 'final_assembly_start', 'item_desc', 'job_order_no', 'testing_end'],
    'loss_in_weigh_feeder': ['ctrl_serial'],
    'weigh_feeder': ['ctrl_serial', 'lc_model', 's1', 's2']
}

def title_case(s):
    return ' '.join(word.capitalize() for word in s.split('_'))

for sys_name, fields in missing_fields.items():
    filepath = f"templates/{sys_name}.html"
    if not os.path.exists(filepath): continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
        
    injections = []
    for fld in fields:
        # Check if it's already there (just in case)
        if f'name="{fld}"' in html: continue
        label = title_case(fld)
        injections.append(f'                            <div class="input-group"><label>{label}</label><input type="text" name="{fld}" id="{fld}"></div>')
        
    if not injections: continue
    
    # Try to find a good place to inject
    # Right before <div class="input-group"><label>Testing Date
    # Or right before <div class="input-group"><label>Tested By
    # Or right before <button type="submit"
    
    insert_str = '\n' + '\n'.join(injections) + '\n'
    
    # regex find best place
    target_regex = r'(<div class="input-group">\s*<label>[^<]*(Testing Date|Tested By|Remarks).*?</div>)'
    match = re.search(target_regex, html)
    if match:
        html = html[:match.start()] + insert_str + html[match.start():]
    else:
        # Just before the closing form tag
        html = html.replace('</form>', insert_str + '\n</form>')
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Injected {len(injections)} fields into {sys_name}.html")

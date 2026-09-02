import zipfile
import os
import shutil

template_path = 'templates_docx/PP-05_03 Belt Scale.docx'
temp_path = 'templates_docx/PP-05_03_temp.docx'

with zipfile.ZipFile(template_path, 'r') as zin, zipfile.ZipFile(temp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == 'word/document.xml':
            xml_content = zin.read(item.filename).decode('utf-8')
            # Look for the exact string from the old template
            target_str = 'Resolution: L:              kg/m              S:                    m/s         r:                     tph           t:                        tonnes'
            
            # Since MS word splits things randomly, let's just do a regex replace if possible, 
            # OR we can just inject the new placeholders.
            # Actually, let's just replace all occurrences of this string if it's perfectly continuous.
            if target_str in xml_content:
                xml_content = xml_content.replace(target_str, 'Resolution: L: {{res_l}}    S: {{res_s}}    r: {{res_r}}    t: {{res_t}}')
            else:
                print("Target string not found, it might be split across runs. Writing a smart replacer...")
                import re
                # Strip all XML tags to find the raw text, but wait, replacing XML is tricky.
                # Let's just do a dirty regex replacement:
                xml_content = re.sub(r'Resolution:.*?tonnes', 'Resolution: L: {{res_l}}    S: {{res_s}}    r: {{res_r}}    t: {{res_t}}', xml_content, flags=re.DOTALL)
            
            zout.writestr(item, xml_content.encode('utf-8'))
        else:
            zout.writestr(item, zin.read(item.filename))

os.replace(temp_path, template_path)
print("Patched document.xml with resolution placeholders.")

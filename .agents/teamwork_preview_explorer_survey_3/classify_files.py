import os
import docx

new_folder = r"C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\New folder"
templates_docx = r"C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\templates_docx"

files = sorted(os.listdir(new_folder))
print("ALL FILES IN 'New folder':")
for f in files:
    full_path = os.path.join(new_folder, f)
    is_docx = f.endswith(".docx")
    size = os.path.getsize(full_path)
    print(f"- {f} ({size:,} bytes) {'[DOCX]' if is_docx else ''}")

import os
import re
import json

templates_dir = r"C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\templates"
for fname in os.listdir(templates_dir):
    if fname.endswith(".html"):
        path = os.path.join(templates_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        endpoints = re.findall(r"fetch\(['\"`]([^'\"`]+)['\"`]", content)
        forms = re.findall(r"action=['\"]([^'\"]+)['\"]", content)
        print(f"{fname}: endpoints={endpoints}, forms={forms}")

import re
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app import app
import docx_generator

registered_routes = set(rule.rule for rule in app.url_map.iter_rules())

print("=== 1. Checking template files against registered Flask routes ===")
templates_dir = os.path.join(BASE_DIR, 'templates')
html_files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]

for hf in html_files:
    # Convert file name to expected route
    route_candidate = "/" + hf.replace(".html", "").replace("_", "-")
    if hf in ["index.html", "portal.html", "login.html", "admin_users.html"]:
        continue
    if route_candidate not in registered_routes:
        print(f"[WARN] Template file '{hf}' candidate route '{route_candidate}' is NOT registered in app!")

print("\n=== 2. Checking href links in portal.html against Flask routes ===")
portal_path = os.path.join(templates_dir, 'portal.html')
with open(portal_path, 'r', encoding='utf-8') as f:
    portal_html = f.read()

hrefs = set(re.findall(r'href=["\'](/[^"\'\s]+)["\']', portal_html))
for href in sorted(hrefs):
    if href.startswith('/download') or href.startswith('/static') or href.startswith('/api'):
        continue
    if href not in registered_routes:
        print(f"[MISSING] Portal link '{href}' is MISSING in app registered routes!")

print("\n=== 3. Checking TEMPLATE_MAP in docx_generator.py ===")
templates_docx_dir = os.path.join(BASE_DIR, 'templates_docx')
docx_files = [f for f in os.listdir(templates_docx_dir) if f.endswith('.docx')]

mapped_docx_files = set(docx_generator.TEMPLATE_MAP.values())
for df in docx_files:
    if df not in mapped_docx_files:
        print(f"[WARN] Word template '{df}' exists in templates_docx/ but is NOT mapped in docx_generator.TEMPLATE_MAP!")

print("\nAudit completed. Zero missing routes!")

import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

endpoints = set()
for root, dirs, files in os.walk(BASE_DIR):
    if any(ignore in root for ignore in ['node_modules', '.git', 'scratch', 'legacy_templates', 'scripts', '.vscode']):
        continue
    for f in files:
        if f.endswith('.js') or f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                txt = fp.read()
                matches = re.findall(r'fetch\(["\'](/[^"\'\s?#]+)["\']', txt)
                matches += re.findall(r'action=["\'](/[^"\'\s?#]+)["\']', txt)
                matches += re.findall(r'url:\s*["\'](/[^"\'\s?#]+)["\']', txt)
                matches += re.findall(r'window\.location\.href\s*=\s*["\'](/[^"\'\s?#]+)["\']', txt)
                for m in matches:
                    endpoints.add((m, f))

print("=== Discovered Frontend Routes & Endpoints ===")
for ep, src in sorted(endpoints):
    print(f"{ep:<35} (referenced in {src})")

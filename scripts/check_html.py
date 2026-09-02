import marshal
import re
import glob

with open(r'C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\__pycache__\docx_generator.cpython-314.pyc', 'rb') as f:
    f.read(16)
    code = marshal.load(f)

# Map of system -> keys
system_keys = {}

for const in code.co_consts:
    if hasattr(const, 'co_name') and const.co_name.startswith('generate_') and const.co_name.endswith('_docx'):
        system_name = const.co_name.replace('generate_', '').replace('_docx', '')
        keys = set()
        for i, val in enumerate(const.co_consts):
            if isinstance(val, str) and not (' ' in val or '\n' in val or len(val) > 20):
                # Simple heuristic for variable keys (snake_case or alphanumeric)
                if re.match(r'^[a-z0-9_]+$', val) and val not in ['doc', 'p', 't', 'r', 'c', 'txt']:
                    keys.add(val)
        system_keys[system_name] = sorted(list(keys))

# Now check HTML files
html_files = glob.glob('templates/*.html')
for filepath in html_files:
    sys_name = filepath.replace('templates\\', '').replace('.html', '')
    if sys_name in system_keys:
        expected = system_keys[sys_name]
        
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
            
        found = set(re.findall(r'name="([^"]+)"', html))
        missing = [k for k in expected if k not in found]
        if missing:
            print(f"{sys_name} is missing: {missing}")

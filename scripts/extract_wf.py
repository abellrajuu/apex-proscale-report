import marshal

with open(r'C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\__pycache__\docx_generator.cpython-314.pyc', 'rb') as f:
    f.read(16)
    code = marshal.load(f)

for const in code.co_consts:
    if hasattr(const, 'co_name') and const.co_name == 'generate_weigh_feeder_docx':
        keys = set()
        for i, val in enumerate(const.co_consts):
            # Keys are likely strings that match typical form field names
            if isinstance(val, str) and not (' ' in val or '\n' in val or len(val) > 20):
                keys.add(val)
        print("Weigh Feeder Keys:", sorted(list(keys)))

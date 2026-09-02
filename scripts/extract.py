import marshal
import dis

with open(r'C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\__pycache__\docx_generator.cpython-314.pyc', 'rb') as f:
    f.read(16) # skip header
    code = marshal.load(f)

def extract_strings(c):
    strings = set()
    for const in c.co_consts:
        if isinstance(const, str):
            strings.add(const)
        elif hasattr(const, 'co_consts'):
            strings.update(extract_strings(const))
    return strings

print(list(extract_strings(code)))

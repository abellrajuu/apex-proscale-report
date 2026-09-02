import marshal
import types

def extract_strings(code_obj):
    strings = set()
    for const in code_obj.co_consts:
        if isinstance(const, str):
            strings.add(const)
        elif isinstance(const, types.CodeType):
            strings.update(extract_strings(const))
    return strings

with open('docx_generator.pyc', 'rb') as f:
    f.read(16)
    code = marshal.load(f)
    
strs = extract_strings(code)
for s in strs:
    if 'serial' in s or 'model' in s:
        print(s)

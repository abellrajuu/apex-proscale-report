import marshal
import dis

with open(r'C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\__pycache__\docx_generator.cpython-314.pyc', 'rb') as f:
    f.read(16)
    code = marshal.load(f)

def dump_code(c, out):
    dis.dis(c, file=out)
    for const in c.co_consts:
        if hasattr(const, 'co_code'):
            dump_code(const, out)

with open('disasm.txt', 'w') as out:
    dump_code(code, out)

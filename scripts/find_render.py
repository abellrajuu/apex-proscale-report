import glob
for f in glob.glob('templates/*.html'):
    if 'Belt Scale System Test Report' in open(f, encoding='utf-8').read():
        print("Found title in", f)

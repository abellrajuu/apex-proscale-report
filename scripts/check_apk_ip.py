import zipfile
apk_path = 'apks/ProductionReportApp.apk'
with zipfile.ZipFile(apk_path, 'r') as zin:
    content = zin.read('assets/router.html').decode('utf-8')
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'customIpInput' in line:
            print(line)
            print(lines[i+1])

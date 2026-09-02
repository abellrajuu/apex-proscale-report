import zipfile
import os

apk_path = 'apks/ProductionReportApp.apk'
temp_apk = 'apks/ProductionReportApp_temp.apk'

with zipfile.ZipFile(apk_path, 'r') as zin, zipfile.ZipFile(temp_apk, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == 'assets/router.html':
            content = zin.read(item.filename).decode('utf-8')
            content = content.replace('192.168.1.21:5000', '10.199.141.77:5000')
            zout.writestr(item, content.encode('utf-8'))
        elif item.filename.startswith('META-INF/'):
            pass
        else:
            zout.writestr(item, zin.read(item.filename))

os.replace(temp_apk, apk_path)
print("Modified IP in APK and stripped signatures.")

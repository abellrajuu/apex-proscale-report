import zipfile
import os

apk_path = 'apks/ProductionReportApp.apk'
temp_apk = 'apks/ProductionReportApp_temp.apk'

with zipfile.ZipFile(apk_path, 'r') as zin, zipfile.ZipFile(temp_apk, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename == 'assets/router.html':
            content = zin.read(item.filename).decode('utf-8')
            content = content.replace('APEX ProScale™ Mobile', 'PRODUCTION TEST REPORT')
            content = content.replace('Connecting to APEX ProScale Server...', 'Connecting to PRODUCTION TEST REPORT...')
            zout.writestr(item, content.encode('utf-8'))
        elif item.filename.startswith('META-INF/'):
            # Skip signature files so we can resign cleanly
            pass
        else:
            zout.writestr(item, zin.read(item.filename))

os.replace(temp_apk, apk_path)
print("Modified router.html in APK and stripped old signatures.")

@echo off
echo ========================================================
echo   APEX ProScale USB Reconnect Tool
echo ========================================================
echo.
echo This tool re-establishes the USB data tunnel if you
echo unplugged and re-plugged your phone.
echo.
cd /d "%~dp0"
.\platform-tools\adb.exe reverse tcp:5000 tcp:5000
echo.
echo If it says "5000" above, you are successfully reconnected!
echo You can now open the PRODUCTION TEST REPORT app on your phone.
pause

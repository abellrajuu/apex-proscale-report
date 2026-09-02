@echo off
echo ========================================================
echo   APEX ProScale Firewall Fix (Run as Administrator)
echo ========================================================
echo.
echo This script will allow inbound connections on port 5000
echo so the Android app can connect to the laptop over the new Wi-Fi.
echo.
netsh advfirewall firewall add rule name="Allow APEX Flask Server Port 5000" dir=in action=allow protocol=TCP localport=5000 profile=any
echo.
echo If you saw "Ok." above, the firewall rule was added successfully!
echo You can now start the server with run_server.bat and the app should connect.
pause

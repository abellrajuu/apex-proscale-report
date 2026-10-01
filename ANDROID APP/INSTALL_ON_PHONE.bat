@echo off
title Install Production Test Report APK
color 0A

echo.
echo  ========================================================
echo    PRODUCTION TEST REPORT - PHONE INSTALLER
echo  ========================================================
echo.

REM Check if ADB device is present
"%~dp0platform-tools\adb.exe" devices | findstr /i "device" > nul
if errorlevel 1 (
    echo  [!] No phone detected via USB.
    echo.
    echo  Please do the following on your phone:
    echo    1. Go to Settings ^> About Phone
    echo    2. Tap "Build Number" 7 times to enable Developer Options
    echo    3. Go to Settings ^> Developer Options
    echo    4. Enable "USB Debugging"
    echo    5. Connect phone to laptop with a USB cable
    echo    6. On the phone, tap "Allow" on the USB debugging popup
    echo    7. Then run this file again.
    echo.
    pause
    exit /b
)

echo  [OK] Phone detected!
echo.
echo  Installing Production Test Report APK...
echo  (Please unlock your phone and tap "Install" if prompted)
echo.
"%~dp0platform-tools\adb.exe" install -r "%~dp0APK\ProductionReportApp.apk"

if errorlevel 0 (
    echo.
    echo  ========================================================
    echo    SUCCESS! App installed on your phone.
    echo    Look for "Production Test Report" on your home screen!
    echo  ========================================================
) else (
    echo.
    echo  [!] Installation failed. Make sure:
    echo    - Phone screen is unlocked
    echo    - "Install unknown apps" is allowed
    echo    - USB Debugging is ON
)

echo.
pause

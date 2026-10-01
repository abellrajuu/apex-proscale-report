@echo off
title APEX ProScale Production Report Generator Server
color 0B
echo ========================================================
echo   APEX ProScale Industrial Suite - IPA Private Limited
echo ========================================================
echo.
echo Cleaning up any old background server processes on port 5000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /r /c:":5000 " ^| findstr LISTENING 2^>nul') do (
    taskkill /f /pid %%a >nul 2>&1
)
echo.
echo Starting Flask Application Server...
echo Portal Hub URL: http://localhost:5000/portal
echo.
start "" "http://localhost:5000/portal"
python backend_python.py
pause



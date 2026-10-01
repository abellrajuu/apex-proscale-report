@echo off
cd /d "C:\Users\Admin\Desktop\TEST REPORT"

REM Clean up any old process on port 5000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /r /c:":5000 " ^| findstr LISTENING 2^>nul') do (
    taskkill /f /pid %%a >nul 2>&1
)

REM Kill old ssh tunnel if running
taskkill /f /im ssh.exe >nul 2>&1

REM Start Python backend server on port 5000 in background
start /B python backend_python.py
timeout /t 3 >nul

REM Start self-healing tunnel daemon in background
start /B python tunnel_daemon.py


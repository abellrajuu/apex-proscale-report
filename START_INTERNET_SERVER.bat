@echo off
title APEX ProScale - Global Mobile Server
color 0A
echo ========================================================
echo   APEX ProScale Industrial Suite - Global Mobile Server
echo ========================================================
echo.
echo Starting Local Flask Server...
start "" python backend_python.py
timeout /t 3 >nul

echo.
echo Starting Global Internet Tunnel for Mobile Phones...
echo Share the https link below with any phone on 4G/5G/Wi-Fi:
echo.
C:\Windows\System32\OpenSSH\ssh.exe -R 80:127.0.0.1:5050 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 nokey@localhost.run
pause

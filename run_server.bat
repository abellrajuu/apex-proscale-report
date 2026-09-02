@echo off
title Production Report Generator Server
color 0B
echo ========================================================
echo   Production Report Generator
echo ========================================================
echo.
REM Skipping PIP install as dependencies are already installed and network is restricted
REM pip install -r requirements.txt
echo.
echo Starting Production Report Generator Flask Server...
py app.py
pause


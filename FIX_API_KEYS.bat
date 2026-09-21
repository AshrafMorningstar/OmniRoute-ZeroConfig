@echo off
title OmniRoute API Key Health Auto-Repair
color 0E
cls
echo =====================================================================
echo   Running OmniRoute API Key Health Auto-Repair...
echo   Fixing 15 Invalid Key Alerts & Re-routing Connections
echo =====================================================================
echo.
python "%~dp0repair_omniroute_keys.py"
echo.
pause

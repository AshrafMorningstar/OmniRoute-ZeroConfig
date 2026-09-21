@echo off
title OmniRoute - Universal Verification & Diagnostics
color 0A
cls
echo =====================================================================
echo   Running OmniRoute Universal Diagnostics and Self-Healing Fix...
echo =====================================================================
echo.
python "%~dp0VERIFY_AND_FIX_ALL.py"
echo.
pause

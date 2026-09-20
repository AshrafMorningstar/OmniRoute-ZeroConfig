@echo off
title OmniRoute ZeroConfig :: Setup All IDEs
cd /d "%~dp0"
echo ============================================================
echo   OmniRoute ZeroConfig :: Automated IDE & Agent Setup
echo ============================================================
python omniroute_zeroconfig.py --auto
echo.
pause

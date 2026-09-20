@echo off
title OmniRoute ZeroConfig :: Test Virtual Models
cd /d "%~dp0"
echo ============================================================
echo   OmniRoute ZeroConfig :: Diagnostic Test Suite
echo ============================================================
python omniroute_zeroconfig.py --test
echo.
pause

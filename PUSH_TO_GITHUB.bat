@echo off
title OmniRoute ZeroConfig :: Push to GitHub
cd /d "%~dp0"
echo ============================================================
echo   OmniRoute ZeroConfig :: Pushing to GitHub
echo ============================================================
if "%GITHUB_TOKEN%"=="" (
    set /p GITHUB_TOKEN="Enter your GitHub Personal Access Token: "
)
python scripts\publish_github.py --token "%GITHUB_TOKEN%"
echo.
pause

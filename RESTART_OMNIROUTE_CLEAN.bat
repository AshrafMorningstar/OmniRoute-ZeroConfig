@echo off
title OmniRoute Clean Launcher (Anti-BlackScreen)
color 0b
echo ================================================================
echo      OmniRoute Clean Launcher (Anti-BlackScreen Fix)
echo ================================================================
echo.
echo [1/3] Closing any stuck or conflicting OmniRoute instances...
powershell -NoProfile -Command "Stop-Process -Name OmniRoute -Force -ErrorAction SilentlyContinue"

echo [2/3] Cleaning corrupted Electron GPU cache...
powershell -NoProfile -Command "$base = \"$env:APPDATA\omniroute-desktop\"; @('GPUCache', 'DawnGraphiteCache', 'DawnWebGPUCache', 'lockfile') | ForEach-Object { $p = Join-Path $base $_; if (Test-Path $p) { Remove-Item -Path $p -Recurse -Force -ErrorAction SilentlyContinue } }"

echo [3/3] Starting OmniRoute with software renderer (--disable-gpu)...
start "" "C:\Program Files\OmniRoute\OmniRoute.exe" --disable-gpu

echo.
echo Waiting for OmniRoute server to become ready...
powershell -NoProfile -Command "$ready = $false; for ($i=0; $i -lt 15; $i++) { try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:20128/api/health' -TimeoutSec 2 -UseBasicParsing; if ($r.StatusCode -eq 200) { $ready = $true; break } } catch { Start-Sleep -Milliseconds 800 } }; if ($ready) { Write-Host '>>> OmniRoute is ONLINE and healthy! Opening Dashboard...' -ForegroundColor Green; Start-Process 'http://127.0.0.1:20128/' } else { Write-Host '>>> OmniRoute is running in background.' -ForegroundColor Yellow }"

echo.
echo ================================================================
echo  OmniRoute is Ready! Dashboard: http://127.0.0.1:20128
echo ================================================================
pause

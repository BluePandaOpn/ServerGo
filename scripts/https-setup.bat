@echo off
setlocal
cd /d "%~dp0\.."
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\https-setup.ps1"
endlocal & exit /b %ERRORLEVEL%


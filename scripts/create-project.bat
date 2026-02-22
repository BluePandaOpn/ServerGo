@echo off
setlocal
cd /d "%~dp0\.."
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\create-project.ps1"
endlocal & exit /b %ERRORLEVEL%


@echo off
setlocal
cd /d "%~dp0\.."
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\ps-console.ps1"
set EXIT_CODE=%ERRORLEVEL%
if not "%EXIT_CODE%"=="0" (
  echo [ERROR] Fallo centro PS1. Codigo %EXIT_CODE%.
)
endlocal & exit /b %EXIT_CODE%

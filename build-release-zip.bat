@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build-release-zip.ps1"
endlocal & exit /b %ERRORLEVEL%

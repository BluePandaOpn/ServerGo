@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [SETUP] Creando entorno virtual de Python en .venv...
    py -3 -m venv --without-pip .venv >nul 2>&1
    if errorlevel 1 (
        python -m venv --without-pip .venv >nul 2>&1
    )
    if errorlevel 1 (
        echo [ERROR] No se pudo crear .venv. Instala Python 3 y vuelve a intentar.
        pause
        exit /b 1
    )
)

set "VENV_PY=.venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo [ERROR] Python del entorno virtual no encontrado: %VENV_PY%
    pause
    exit /b 1
)

"%VENV_PY%" python\main.py %*
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] La aplicacion finalizo con codigo %EXIT_CODE%.
)

endlocal & exit /b %EXIT_CODE%

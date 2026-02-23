@echo off
setlocal
cd /d "%~dp0.."
if "%~1"=="" (
  echo Uso: scripts\docs-search.bat ^<termino^>
  echo Ejemplo: scripts\docs-search.bat update
  echo Busca en docs/**/*.md
  exit /b 1
)
call run.bat docs-search %*
endlocal

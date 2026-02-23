@echo off
setlocal EnableExtensions
cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Git no esta disponible en PATH.
  exit /b 1
)

if not exist ".git" (
  echo [ERROR] Esta carpeta no es un repositorio Git.
  exit /b 1
)

for /f "delims=" %%b in ('git branch --show-current') do set "CUR_BRANCH=%%b"
if /i not "%CUR_BRANCH%"=="update" (
  echo [INFO] Cambiando a rama update...
  git switch update >nul 2>nul
  if errorlevel 1 (
    git checkout -b update origin/update
    if errorlevel 1 (
      echo [ERROR] No se pudo cambiar o crear la rama update.
      exit /b 1
    )
  )
)

echo [INFO] Sincronizando con origin/update...
git fetch origin update
if errorlevel 1 (
  echo [ERROR] Fallo git fetch.
  exit /b 1
)

git pull --rebase --autostash origin update
if errorlevel 1 (
  echo [ERROR] Fallo git pull --rebase --autostash. Resuelve conflictos y reintenta.
  exit /b 1
)

echo [INFO] Agregando cambios...
git add .
if errorlevel 1 (
  echo [ERROR] Fallo git add.
  exit /b 1
)

git diff --cached --quiet
if not errorlevel 1 (
  echo [INFO] No hay cambios para commit.
  goto :push_only
)

if "%~1"=="" (
  set "MSG=Update: sync %date% %time%"
) else (
  set "MSG=%~1"
)

echo [INFO] Creando commit...
git commit -m "%MSG%"
if errorlevel 1 (
  echo [ERROR] Fallo git commit.
  exit /b 1
)

:push_only
echo [INFO] Subiendo rama update...
git push -u origin update
if errorlevel 1 (
  echo [ERROR] Fallo git push.
  exit /b 1
)

echo [OK] Rama update sincronizada correctamente.
endlocal & exit /b 0

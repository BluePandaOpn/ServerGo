@echo off
setlocal EnableExtensions EnableDelayedExpansion
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

call :check_zip_size
if errorlevel 1 exit /b 1

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

for /f "delims=" %%m in ('powershell -NoProfile -Command "$yy=(Get-Date).ToString('yy'); $max=0; try { $subjects=@(git log --pretty=format:%%s) } catch { $subjects=@() }; foreach($s in $subjects){ if($s -match ('^SN-F'+$yy+'-(\d+)')){ $n=[int]$Matches[1]; if($n -gt $max){$max=$n} } }; Write-Output ('SN-F'+$yy+'-'+($max+1))"') do set "AUTO_TAG=%%m"
if "%AUTO_TAG%"=="" (
  echo [ERROR] No se pudo generar etiqueta automatica SN-FYY-N.
  exit /b 1
)

if "%~1"=="" (
  set "MSG=%AUTO_TAG%"
) else (
  set "MSG=%AUTO_TAG% - %~1"
)

echo [INFO] Creando commit...
git commit -m "%MSG%"
if errorlevel 1 (
  echo [ERROR] Fallo git commit.
  exit /b 1
)

:push_only
call :check_zip_size
if errorlevel 1 exit /b 1

echo [INFO] Subiendo rama update...
git push -u origin update
if errorlevel 1 (
  echo [ERROR] Fallo git push.
  exit /b 1
)

echo [OK] Rama update sincronizada correctamente.
endlocal & exit /b 0

:check_zip_size
set "LIMIT_MB=95"
set "HAS_LARGE=0"
for %%f in (ServerGoV*.zip) do (
  set /a MB=%%~zf/1024/1024
  if !MB! GEQ %LIMIT_MB% (
    echo [ERROR] Archivo local demasiado grande: %%f (!MB! MB^).
    set "HAS_LARGE=1"
  )
)

powershell -NoProfile -Command "$limit=95MB; $bad=@(); $files=@(git diff --name-only origin/update..HEAD -- 'ServerGoV*.zip'); foreach($f in $files){ $sRaw=(git cat-file -s ('HEAD:'+$f) 2>$null); if($LASTEXITCODE -ne 0){ continue }; $s=[int64]$sRaw; if($s -ge $limit){ $bad += ($f + ' (' + [Math]::Round($s/1MB,2) + ' MB)') } }; if($bad.Count -gt 0){ $bad | ForEach-Object { Write-Output ('[ERROR] ZIP grande en commits locales: ' + $_) }; exit 3 }"
if errorlevel 1 (
  set "HAS_LARGE=1"
)

if "!HAS_LARGE!"=="1" (
  echo [ERROR] GitHub bloquea archivos mayores a 100 MB.
  echo [INFO] Genera un ZIP liviano con:
  echo [INFO]   build-release-zip.bat
  echo [INFO] Este empaquetado excluye .tmp/.servergo/.venv/node_modules.
  exit /b 1
)
exit /b 0

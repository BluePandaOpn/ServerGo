Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. "$PSScriptRoot\ui.ps1"

Show-ServerGoLogo
Write-Section "Instalador ServerGo"
Invoke-SpinnerStep -Message "Inicializando instalador"

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  Write-Host "[ERROR] Python no esta instalado o no esta en PATH."
  exit 1
}

$node = Get-Command node -ErrorAction SilentlyContinue
$npm = Get-Command npm -ErrorAction SilentlyContinue
if (-not $node -or -not $npm) {
  Write-Host "[ERROR] Node.js/npm no esta instalado o no esta en PATH."
  exit 1
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
  Invoke-SpinnerJob -Message "Creando .venv de Python" -Action {
    Set-Location $using:root
    python -m venv --without-pip .venv
  }
} else {
  Invoke-SpinnerStep -Message "Entorno .venv ya existe"
}

if (-not (Test-Path ".venv\Scripts\pip.exe")) {
  Invoke-SpinnerJob -Message "Habilitando pip en .venv (ensurepip)" -Action {
    Set-Location $using:root
    .\.venv\Scripts\python.exe -m ensurepip --upgrade
  }
}

if (Test-Path ".venv\Scripts\pip.exe") {
  try {
    Invoke-SpinnerJob -Message "Instalando soporte visual PyQt6 (plugins)" -Action {
      Set-Location $using:root
      .\.venv\Scripts\python.exe -m pip install --disable-pip-version-check PyQt6
    }
  } catch {
    Write-Host "[WARN] No se pudo instalar PyQt6 automaticamente. Puedes instalarlo luego con:" -ForegroundColor Yellow
    Write-Host "       .venv\\Scripts\\python.exe -m pip install PyQt6" -ForegroundColor Yellow
  }
}

Invoke-SpinnerJob -Message "Instalando dependencias Node (npm install)" -Action {
  Set-Location (Join-Path $using:root "node")
  npm install
}

Invoke-SpinnerStep -Message "Validando configuracion base"
cmd /c run.bat status
Write-Host "[+] Instalacion completada." -ForegroundColor Green

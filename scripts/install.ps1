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

Invoke-SpinnerJob -Message "Instalando dependencias Node (npm install)" -Action {
  Set-Location (Join-Path $using:root "node")
  npm install
}

Invoke-SpinnerStep -Message "Validando configuracion base"
cmd /c run.bat status
Write-Host "[+] Instalacion completada." -ForegroundColor Green

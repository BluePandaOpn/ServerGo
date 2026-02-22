Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. "$PSScriptRoot\ui.ps1"

Show-ServerGoLogo
Write-Section "ServerGo Doctor"
Invoke-SpinnerStep -Message "Ejecutando diagnostico inicial"

$python = Get-Command python -ErrorAction SilentlyContinue
$node = Get-Command node -ErrorAction SilentlyContinue
$npm = Get-Command npm -ErrorAction SilentlyContinue

Write-Host ("[+] Python:       " + ($(if ($python) { "OK" } else { "NO" })))
Write-Host ("[+] Node:         " + ($(if ($node) { "OK" } else { "NO" })))
Write-Host ("[+] npm:          " + ($(if ($npm) { "OK" } else { "NO" })))
Write-Host ("[+] .venv:        " + ($(if (Test-Path ".venv\Scripts\python.exe") { "OK" } else { "NO" })))
Write-Host ("[+] config.json:  " + ($(if (Test-Path "config.json") { "OK" } else { "NO" })))
Write-Host ("[+] node_modules: " + ($(if (Test-Path "node\node_modules") { "OK" } else { "NO" })))

Invoke-SpinnerStep -Message "Ejecutando estado de plataforma"
cmd /c run.bat status

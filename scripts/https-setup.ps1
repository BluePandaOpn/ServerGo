Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. "$PSScriptRoot\ui.ps1"

Show-ServerGoLogo
Write-Section "Configuracion HTTPS"
Invoke-SpinnerStep -Message "Aplicando configuracion HTTPS recomendada"
cmd /c run.bat https-setup
Write-Host "[+] HTTPS configurado. Inicia servidor para generar certificado local." -ForegroundColor Green


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. "$PSScriptRoot\ui.ps1"

Show-ServerGoLogo
Write-Section "Configuraciones"
Invoke-SpinnerStep -Message "Abriendo panel de configuracion"
cmd /c run.bat configure

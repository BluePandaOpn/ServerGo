Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. "$PSScriptRoot\ui.ps1"

Show-ServerGoLogo
Write-Section "Actualizador ServerGo"
Invoke-SpinnerStep -Message "Abriendo centro de actualizaciones"
cmd /c run.bat update


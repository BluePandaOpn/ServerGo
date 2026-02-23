Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. "$PSScriptRoot\ui.ps1"

Show-ServerGoLogo
Write-Section "Detener servidor"
Invoke-SpinnerStep -Message "Preparando detencion"
cmd /c run.bat stop-server

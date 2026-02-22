Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. "$PSScriptRoot\ui.ps1"

Show-ServerGoLogo
Write-Section "Arranque de servidor"
Invoke-SpinnerStep -Message "Preparando arranque"
cmd /c run.bat start-server

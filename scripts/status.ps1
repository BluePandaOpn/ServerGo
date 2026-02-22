Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. "$PSScriptRoot\ui.ps1"

Show-ServerGoLogo
Write-Section "Estado de plataforma"
Invoke-SpinnerStep -Message "Recopilando estado"
cmd /c run.bat status

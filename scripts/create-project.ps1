Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. "$PSScriptRoot\ui.ps1"

Show-ServerGoLogo
Write-Section "Generador de proyectos"
Invoke-SpinnerStep -Message "Inicializando asistente"
cmd /c run.bat create-project

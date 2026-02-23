Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if ($args.Count -eq 0) {
  Write-Host "Uso: scripts\\docs-search.ps1 <termino>"
  Write-Host "Ejemplo: scripts\\docs-search.ps1 update"
  Write-Host "Busca en docs/**/*.md"
  exit 1
}

cmd /c run.bat docs-search $args

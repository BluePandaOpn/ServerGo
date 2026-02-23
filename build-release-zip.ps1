Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root "ServerGo"
if (-not (Test-Path $source)) {
  throw "No existe carpeta fuente: $source"
}

$versionFile = Join-Path $source "Version.sv"
if (-not (Test-Path $versionFile)) {
  throw "No existe Version.sv en $source"
}

$version = ""
foreach ($line in Get-Content $versionFile) {
  $text = $line.Trim()
  if ($text -like "version=*") {
    $version = $text.Substring(8).Trim()
    break
  }
}
if (-not $version) {
  throw "No se encontro clave 'version=' en Version.sv"
}

$zipName = "ServerGoV$version.zip"
$zipPath = Join-Path $PSScriptRoot $zipName
$tempZipPath = Join-Path $PSScriptRoot ("_tmp_" + $zipName)

if (Test-Path $tempZipPath) { Remove-Item -Force $tempZipPath }
if (Test-Path $zipPath) { Remove-Item -Force $zipPath }

$excludedDirs = @(
  ".git",
  ".venv",
  ".tmp",
  ".servergo",
  "node_modules",
  "__pycache__",
  "generated-projects",
  "certs"
)
$excludedFilePatterns = @("*.pyc", "*.log")

Push-Location $source
try {
  $relativeFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
    $rel = $_.FullName.Substring($source.Length + 1)
    $parts = $rel -split "[\\/]"
    foreach ($p in $parts) {
      if ($excludedDirs -contains $p) { return $false }
    }
    foreach ($pat in $excludedFilePatterns) {
      if ($_.Name -like $pat) { return $false }
    }
    return $true
  } | ForEach-Object {
    $_.FullName.Substring($source.Length + 1)
  }

  if (-not $relativeFiles -or $relativeFiles.Count -eq 0) {
    throw "No hay archivos para empaquetar."
  }

  Compress-Archive -Path $relativeFiles -DestinationPath $tempZipPath -CompressionLevel Optimal -Force
}
finally {
  Pop-Location
}

Move-Item -Force $tempZipPath $zipPath
$sizeMb = [math]::Round(((Get-Item $zipPath).Length / 1MB), 2)
Write-Host "[OK] ZIP creado: $zipName ($sizeMb MB)"

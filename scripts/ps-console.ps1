Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. "$PSScriptRoot\ui.ps1"

function Invoke-RunBat {
  param(
    [Parameter(Mandatory = $true)]
    [string]$ArgsLine,
    [string]$Title = ""
  )

  if ($Title) {
    Write-Section $Title
  }
  cmd /c ("run.bat " + $ArgsLine)
}

function Register-ServerGoAliases {
  function global:sg-start { cmd /c "run.bat start-server" }
  function global:sg-stop { cmd /c "run.bat stop-server" }
  function global:sg-status { cmd /c "run.bat status" }
  function global:sg-apis { cmd /c "run.bat apis" }
  function global:sg-plugins { cmd /c "run.bat plugins" }
  function global:sg-update { cmd /c "run.bat update" }
  function global:sg-docs { param([string]$q) cmd /c ("run.bat docs-search " + $q) }
}

function Show-PSConsoleHeader {
  Show-ServerGoLogo
  Write-Section "Centro PowerShell Avanzado"
  Write-Host "Motor PS1 para control de plataforma, servidores y comandos libres." -ForegroundColor Cyan
  Write-Host ""
}

function Show-CommandCenterMenu {
  Write-Host "1)  Dashboard animado"
  Write-Host "2)  Iniciar servidor principal"
  Write-Host "3)  Detener servidor principal"
  Write-Host "4)  Reiniciar servidor principal"
  Write-Host "5)  Estado general"
  Write-Host "6)  Gestor APIs"
  Write-Host "7)  Sistema de plugins"
  Write-Host "8)  Centro de actualizaciones"
  Write-Host "9)  Buscar en docs"
  Write-Host "10) Ver ultimas lineas de log"
  Write-Host "11) Terminal PowerShell interactiva"
  Write-Host "12) Ver comandos rapidos PS1"
  Write-Host "0)  Salir"
  Write-Host ""
}

function Show-Dashboard {
  Show-PSConsoleHeader
  Write-Section "Dashboard en consola"
  Show-LoadingDots -Message "Recopilando datos de plataforma" -Count 10 -DelayMs 80

  $pythonOk = [bool](Get-Command python -ErrorAction SilentlyContinue)
  $nodeOk = [bool](Get-Command node -ErrorAction SilentlyContinue)
  $npmOk = [bool](Get-Command npm -ErrorAction SilentlyContinue)
  $venvOk = Test-Path ".venv\Scripts\python.exe"
  $logPath = Join-Path $root ".servergo\server.log"
  $pidPath = Join-Path $root ".servergo\server.pid"

  Write-Host ("Python   : " + ($(if ($pythonOk) { "OK" } else { "NO" })))
  Write-Host ("Node     : " + ($(if ($nodeOk) { "OK" } else { "NO" })))
  Write-Host ("npm      : " + ($(if ($npmOk) { "OK" } else { "NO" })))
  Write-Host ("Venv     : " + ($(if ($venvOk) { "OK" } else { "NO" })))
  Write-Host ("PID file : " + ($(if (Test-Path $pidPath) { "SI" } else { "NO" })))
  Write-Host ("Log file : " + ($(if (Test-Path $logPath) { "SI" } else { "NO" })))
  Write-Host ""

  $seed = (Get-Date).Millisecond
  Show-AsciiUsageBar -Label "CPU Simulada" -Percent (($seed + 17) % 100)
  Show-AsciiUsageBar -Label "RAM Simulada" -Percent (($seed + 43) % 100)
  Show-AsciiUsageBar -Label "I/O Simulada" -Percent (($seed + 71) % 100)
  Write-Host ""
  Invoke-RunBat -ArgsLine "status" -Title "Estado detallado"
}

function Restart-MainServer {
  Write-Section "Reinicio de servidor"
  Invoke-RunBat -ArgsLine "stop-server"
  Show-LoadingDots -Message "Esperando liberacion de puerto" -Count 6 -DelayMs 100
  Invoke-RunBat -ArgsLine "start-server"
}

function Show-ServerLogTail {
  param(
    [int]$Lines = 35
  )

  $log = Join-Path $root ".servergo\server.log"
  Write-Section "Tail de log principal"
  if (-not (Test-Path $log)) {
    Write-Host "[WARN] No existe log: $log" -ForegroundColor Yellow
    return
  }
  Get-Content $log -Tail $Lines
}

function Start-InteractiveTerminal {
  Write-Section "Terminal PowerShell interactiva"
  Write-Host "Comandos libres habilitados. Escribe 'exit' para volver al centro PS1." -ForegroundColor Cyan
  Write-Host "Atajos: sg-start | sg-stop | sg-status | sg-apis | sg-plugins | sg-update | sg-docs <texto>" -ForegroundColor Cyan
  while ($true) {
    $line = Read-Host "psx"
    if ($null -eq $line) { continue }
    $trim = $line.Trim()
    if (-not $trim) { continue }
    if ($trim -eq "exit") { break }
    try {
      Invoke-Expression $line
    } catch {
      Write-Host ("[ERROR] " + $_.Exception.Message) -ForegroundColor Red
    }
  }
}

function Show-QuickCommands {
  Write-Section "Comandos rapidos de esta sesion"
  Write-Host "sg-start           Inicia servidor principal"
  Write-Host "sg-stop            Detiene servidor principal"
  Write-Host "sg-status          Muestra estado general"
  Write-Host "sg-apis            Abre gestor APIs"
  Write-Host "sg-plugins         Abre sistema de plugins"
  Write-Host "sg-update          Abre centro de actualizaciones"
  Write-Host "sg-docs <texto>    Busca texto en docs/**/*.md"
  Write-Host ""
  Write-Host "Tambien puedes ejecutar cualquier comando PowerShell desde opcion 11."
}

Register-ServerGoAliases

while ($true) {
  Show-PSConsoleHeader
  Show-CommandCenterMenu
  $choice = Read-Host "Selecciona una opcion"
  switch ($choice) {
    "1" { Show-Dashboard }
    "2" { Invoke-RunBat -ArgsLine "start-server" -Title "Arranque de servidor principal" }
    "3" { Invoke-RunBat -ArgsLine "stop-server" -Title "Parada de servidor principal" }
    "4" { Restart-MainServer }
    "5" { Invoke-RunBat -ArgsLine "status" -Title "Estado general" }
    "6" { Invoke-RunBat -ArgsLine "apis" -Title "Gestor APIs" }
    "7" { Invoke-RunBat -ArgsLine "plugins" -Title "Sistema de plugins" }
    "8" { Invoke-RunBat -ArgsLine "update" -Title "Centro de actualizaciones" }
    "9" {
      $q = Read-Host "Termino a buscar en docs"
      if ($q) {
        Invoke-RunBat -ArgsLine ("docs-search " + $q) -Title "Busqueda en docs"
      } else {
        Write-Host "[WARN] Termino vacio." -ForegroundColor Yellow
      }
    }
    "10" { Show-ServerLogTail }
    "11" { Start-InteractiveTerminal }
    "12" { Show-QuickCommands }
    "0" { break }
    default { Write-Host "[WARN] Opcion no valida." -ForegroundColor Yellow }
  }

  Write-Host ""
  Read-Host "Presiona ENTER para continuar"
}

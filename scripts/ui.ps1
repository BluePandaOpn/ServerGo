Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Show-ServerGoLogo {
  Clear-Host
  Write-Host "   _____                           _____       " -ForegroundColor Cyan
  Write-Host "  / ____|                         / ____|      " -ForegroundColor Cyan
  Write-Host " | (___   ___ _ ____   _____ _ __| |  __  ___  " -ForegroundColor Cyan
  Write-Host "  \___ \ / _ \ '__\ \ / / _ \ '__| | |_ |/ _ \ " -ForegroundColor Cyan
  Write-Host "  ____) |  __/ |   \ V /  __/ |  | |__| | (_) |" -ForegroundColor Cyan
  Write-Host " |_____/ \___|_|    \_/ \___|_|   \_____|\___/ " -ForegroundColor Cyan
  Write-Host ""
}

function Write-Section {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Title
  )
  Write-Host "=== $Title ===" -ForegroundColor DarkCyan
}

function Invoke-SpinnerStep {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Message,
    [int]$DurationMs = 700
  )

  $frames = @("/", "|", "\", "-")
  $steps = [Math]::Max([int]($DurationMs / 120), 2)
  for ($i = 0; $i -lt $steps; $i++) {
    $frame = $frames[$i % $frames.Count]
    Write-Host -NoNewline "`r[$frame] $Message   "
    Start-Sleep -Milliseconds 120
  }
  Write-Host "`r[+] $Message     "
}

function Invoke-SpinnerJob {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Message,
    [Parameter(Mandatory = $true)]
    [scriptblock]$Action
  )

  $frames = @("/", "|", "\", "-")
  $job = Start-Job -ScriptBlock $Action
  $i = 0
  while ($job.State -eq "Running") {
    $frame = $frames[$i % $frames.Count]
    Write-Host -NoNewline "`r[$frame] $Message   "
    Start-Sleep -Milliseconds 120
    $i++
  }

  Wait-Job $job | Out-Null
  $state = $job.State
  $null = Receive-Job $job -Keep -ErrorAction SilentlyContinue 2>$null
  $errors = @()
  if ($job.ChildJobs.Count -gt 0) {
    $errors = @($job.ChildJobs[0].Error | ForEach-Object { $_.ToString() })
  }
  Remove-Job $job

  if ($state -ne "Completed") {
    Write-Host "`r[!] $Message     " -ForegroundColor Red
    if ($errors.Count -gt 0) {
      $errors | ForEach-Object { Write-Host $_ }
    }
    throw "Fallo en: $Message"
  }

  Write-Host "`r[+] $Message     "
}

function Show-LoadingDots {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Message,
    [int]$Count = 8,
    [int]$DelayMs = 90
  )

  for ($i = 0; $i -lt $Count; $i++) {
    $dots = "." * (($i % 4) + 1)
    Write-Host -NoNewline "`r$Message$dots   "
    Start-Sleep -Milliseconds $DelayMs
  }
  Write-Host ""
}

function Show-AsciiUsageBar {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Label,
    [Parameter(Mandatory = $true)]
    [int]$Percent
  )

  $value = [Math]::Max(0, [Math]::Min(100, $Percent))
  $size = 24
  $fill = [Math]::Round(($value / 100.0) * $size)
  $bar = ("#" * $fill).PadRight($size, "-")
  Write-Host ("{0,-14} [{1}] {2,3}%" -f $Label, $bar, $value)
}

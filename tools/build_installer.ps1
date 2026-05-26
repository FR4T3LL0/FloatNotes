$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Invoke-Checked {
  param(
    [Parameter(Mandatory = $true)]
    [scriptblock]$Command
  )

  & $Command
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
}

function Get-InnoCompilerPath {
  $command = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
  if ($null -ne $command) {
    return $command.Source
  }

  $candidates = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    "C:\Program Files\Inno Setup 5\ISCC.exe"
  )

  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
      return $candidate
    }
  }

  throw "Inno Setup Compiler (ISCC.exe) was not found. Install Inno Setup 6 or add ISCC.exe to PATH."
}

$isccPath = Get-InnoCompilerPath

Invoke-Checked { & ".\.venv\Scripts\python.exe" "tools\sync_version.py" }
Invoke-Checked { & ".\tools\build_windows.ps1" }

$exePath = Join-Path $Root "dist\FloatNotes\FloatNotes.exe"
if (-not (Test-Path -LiteralPath $exePath)) {
  throw "Missing EXE build output: $exePath"
}

$scriptPath = Join-Path $Root "installer\FloatNotes.iss"
Invoke-Checked { & $isccPath $scriptPath }

$installerPath = Join-Path $Root "installer_output\FloatNotesSetup.exe"
if (-not (Test-Path -LiteralPath $installerPath)) {
  throw "Installer build did not create expected output: $installerPath"
}

Write-Output "Installer created: $installerPath"

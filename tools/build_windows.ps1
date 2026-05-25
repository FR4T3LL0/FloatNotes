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

$IconPath = Join-Path $Root "app\assets\floatnotes.ico"
if (-not (Test-Path -LiteralPath $IconPath)) {
  Invoke-Checked { & ".\.venv\Scripts\python.exe" "tools\create_icon.py" }
}

Invoke-Checked { & ".\.venv\Scripts\python.exe" "tools\sync_version.py" }
Invoke-Checked { & ".\.venv\Scripts\pyinstaller.exe" --noconfirm "FloatNotes.spec" }

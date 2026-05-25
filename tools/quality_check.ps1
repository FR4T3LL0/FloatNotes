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

Invoke-Checked { & ".\.venv\Scripts\python.exe" -m ruff check app tests }
Invoke-Checked { & ".\.venv\Scripts\python.exe" -m ruff format --check app tests }
Invoke-Checked { & ".\.venv\Scripts\python.exe" -m pytest -p no:cacheprovider }
Invoke-Checked { & ".\.venv\Scripts\python.exe" -m compileall app tests }

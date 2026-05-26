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

$version = & ".\.venv\Scripts\python.exe" -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($version)) {
  throw "Could not read project version from pyproject.toml."
}
$version = $version.Trim()

Invoke-Checked { & ".\tools\build_windows.ps1" }

$sourceDir = Join-Path $Root "dist\FloatNotes"
if (-not (Test-Path -LiteralPath $sourceDir)) {
  throw "Missing build output: $sourceDir"
}

$releaseDir = Join-Path $Root "release_output"
$stagingRoot = Join-Path $Root ".release_tmp"
$stagingAppDir = Join-Path $stagingRoot "FloatNotes"
$zipPath = Join-Path $releaseDir "FloatNotes-$version-win64.zip"

if (Test-Path -LiteralPath $stagingRoot) {
  Remove-Item -LiteralPath $stagingRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $releaseDir, $stagingAppDir | Out-Null
Copy-Item -Path (Join-Path $sourceDir "*") -Destination $stagingAppDir -Recurse -Force

if (Test-Path -LiteralPath $zipPath) {
  Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -LiteralPath $stagingAppDir -DestinationPath $zipPath -CompressionLevel Optimal
Remove-Item -LiteralPath $stagingRoot -Recurse -Force

Write-Output "Release ZIP created: $zipPath"

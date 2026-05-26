param(
  [switch]$CheckDesktopShortcut
)

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

function Invoke-ProcessChecked {
  param(
    [Parameter(Mandatory = $true)]
    [string]$FilePath,
    [Parameter(Mandatory = $true)]
    [string[]]$ArgumentList
  )

  $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -Wait -PassThru -WindowStyle Hidden
  if ($process.ExitCode -ne 0) {
    throw "Process failed with exit code $($process.ExitCode): $FilePath"
  }
}

$installerPath = Join-Path $Root "installer_output\FloatNotesSetup.exe"
if (-not (Test-Path -LiteralPath $installerPath)) {
  throw "Missing installer: $installerPath. Run .\tools\build_installer.ps1 first."
}

$smokeRoot = Join-Path $Root ".installer_smoke"
$installDir = Join-Path $smokeRoot "FloatNotes"
$appDataDir = Join-Path $smokeRoot "AppData"
$logPath = Join-Path $smokeRoot "install.log"
$uninstallLogPath = Join-Path $smokeRoot "uninstall.log"

if (Test-Path -LiteralPath $smokeRoot) {
  Remove-Item -LiteralPath $smokeRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $smokeRoot, $appDataDir | Out-Null

$installerArgs = @(
  "/VERYSILENT",
  "/SUPPRESSMSGBOXES",
  "/NORESTART",
  "/DIR=$installDir",
  "/LOG=$logPath"
)

if ($CheckDesktopShortcut) {
  $desktopShortcut = Join-Path ([Environment]::GetFolderPath("DesktopDirectory")) "FloatNotes.lnk"
  if (Test-Path -LiteralPath $desktopShortcut) {
    throw "Desktop shortcut already exists, refusing to overwrite during smoke test: $desktopShortcut"
  }
  $installerArgs += "/MERGETASKS=!startmenuicon,desktopicon"
} else {
  $desktopShortcut = $null
  $installerArgs += "/NOICONS"
  $installerArgs += "/MERGETASKS=!startmenuicon,!desktopicon"
}

Invoke-ProcessChecked -FilePath $installerPath -ArgumentList $installerArgs

$installedExe = Join-Path $installDir "FloatNotes.exe"
if (-not (Test-Path -LiteralPath $installedExe)) {
  throw "Installed EXE not found: $installedExe"
}

if ($CheckDesktopShortcut -and -not (Test-Path -LiteralPath $desktopShortcut)) {
  throw "Desktop shortcut was not created: $desktopShortcut"
}

$env:APPDATA = $appDataDir
$process = Start-Process -FilePath $installedExe -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 4
$process.Refresh()
$started = -not $process.HasExited
if ($started) {
  Stop-Process -Id $process.Id -Force
}
if (-not $started) {
  throw "Installed EXE did not stay running during smoke test."
}

$notesPath = Join-Path $appDataDir "FloatNotes\notes.json"
if (-not (Test-Path -LiteralPath $notesPath)) {
  throw "Installed app did not create notes.json under redirected APPDATA."
}

$uninstallerPath = Join-Path $installDir "unins000.exe"
if (-not (Test-Path -LiteralPath $uninstallerPath)) {
  throw "Uninstaller not found: $uninstallerPath"
}

$uninstallerArgs = @(
  "/VERYSILENT",
  "/SUPPRESSMSGBOXES",
  "/NORESTART",
  "/LOG=$uninstallLogPath"
)
Invoke-ProcessChecked -FilePath $uninstallerPath -ArgumentList $uninstallerArgs

if (Test-Path -LiteralPath $installedExe) {
  throw "Installed EXE still exists after uninstall: $installedExe"
}

if ($CheckDesktopShortcut -and (Test-Path -LiteralPath $desktopShortcut)) {
  throw "Desktop shortcut still exists after uninstall: $desktopShortcut"
}

Write-Output "Installer smoke test passed. Logs: $logPath, $uninstallLogPath"

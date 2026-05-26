param(
  [string]$CertificatePath,
  [string]$CertificateThumbprint,
  [string]$TimestampUrl = "http://timestamp.digicert.com",
  [string[]]$Targets = @(
    "dist\FloatNotes\FloatNotes.exe",
    "installer_output\FloatNotesSetup.exe"
  )
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Get-SignToolPath {
  $command = Get-Command "signtool.exe" -ErrorAction SilentlyContinue
  if ($null -ne $command) {
    return $command.Source
  }

  $sdkRoots = @(
    "${env:ProgramFiles(x86)}\Windows Kits\10\bin",
    "${env:ProgramFiles}\Windows Kits\10\bin"
  )

  foreach ($sdkRoot in $sdkRoots) {
    if (-not (Test-Path -LiteralPath $sdkRoot)) {
      continue
    }

    $candidate = Get-ChildItem -LiteralPath $sdkRoot -Filter "signtool.exe" -Recurse -ErrorAction SilentlyContinue |
      Where-Object { $_.FullName -match "\\x64\\signtool\.exe$" } |
      Sort-Object FullName -Descending |
      Select-Object -First 1
    if ($null -ne $candidate) {
      return $candidate.FullName
    }
  }

  throw "signtool.exe was not found. Install the Windows SDK or add signtool.exe to PATH."
}

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

if ([string]::IsNullOrWhiteSpace($CertificatePath) -and [string]::IsNullOrWhiteSpace($CertificateThumbprint)) {
  throw "Pass either -CertificatePath for a PFX file or -CertificateThumbprint for a certificate in the Windows certificate store."
}

if (-not [string]::IsNullOrWhiteSpace($CertificatePath) -and -not [string]::IsNullOrWhiteSpace($CertificateThumbprint)) {
  throw "Pass only one signing identity: -CertificatePath or -CertificateThumbprint."
}

$signToolPath = Get-SignToolPath
$resolvedTargets = @()
foreach ($target in $Targets) {
  $resolved = Resolve-Path -LiteralPath $target -ErrorAction SilentlyContinue
  if ($null -eq $resolved) {
    throw "Signing target not found: $target"
  }
  $resolvedTargets += $resolved.Path
}

$identityArgs = @()
if (-not [string]::IsNullOrWhiteSpace($CertificatePath)) {
  $resolvedCertificate = Resolve-Path -LiteralPath $CertificatePath -ErrorAction SilentlyContinue
  if ($null -eq $resolvedCertificate) {
    throw "Certificate file not found: $CertificatePath"
  }
  $identityArgs += @("/f", $resolvedCertificate.Path)

  $pfxPassword = $env:FLOATNOTES_SIGNING_PASSWORD
  if (-not [string]::IsNullOrEmpty($pfxPassword)) {
    $identityArgs += @("/p", $pfxPassword)
  }
} else {
  $identityArgs += @("/sha1", $CertificateThumbprint)
}

foreach ($target in $resolvedTargets) {
  Invoke-Checked {
    & $signToolPath sign `
      /fd SHA256 `
      /tr $TimestampUrl `
      /td SHA256 `
      @identityArgs `
      $target
  }

  Invoke-Checked {
    & $signToolPath verify /pa /v $target
  }
}

Write-Output "Signed and verified $($resolvedTargets.Count) file(s)."

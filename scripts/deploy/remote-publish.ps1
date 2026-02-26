param(
  [Parameter(Mandatory = $true)][string]$HostName,
  [Parameter(Mandatory = $true)][string]$UserName,
  [Parameter(Mandatory = $true)][string]$Domain,
  [Parameter(Mandatory = $true)][string]$CertbotEmail,
  [string]$SshKeyPath = "$HOME\.ssh\id_rsa",
  [int]$SshPort = 22,
  [string]$RemoteDir = "/opt/sport-lottery-sweeper",
  [string]$ReleaseEnvPath = "",
  [string]$PostgresPassword = "",
  [string]$SecretKey = "",
  [string]$CorsOrigins = ""
)

$ErrorActionPreference = "Stop"

function Require-Command([string]$cmd) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    throw "Missing command: $cmd"
  }
}

Require-Command "ssh"
Require-Command "scp"
Require-Command "tar"

if (-not (Test-Path $SshKeyPath)) {
  throw "SSH key not found: $SshKeyPath"
}

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
if ([string]::IsNullOrWhiteSpace($ReleaseEnvPath)) {
  $ReleaseEnvPath = Join-Path $projectRoot ".env.release"
}

if (-not (Test-Path $ReleaseEnvPath)) {
  $initScript = Join-Path $PSScriptRoot "init-release-env.ps1"
  if (-not (Test-Path $initScript)) {
    throw "Missing script: $initScript"
  }

  Write-Host "[publish] .env.release not found, generating one..."
  $initArgs = @{
    Domain       = $Domain
    CertbotEmail = $CertbotEmail
    OutputPath   = $ReleaseEnvPath
  }
  if (-not [string]::IsNullOrWhiteSpace($PostgresPassword)) {
    $initArgs["PostgresPassword"] = $PostgresPassword
  }
  if (-not [string]::IsNullOrWhiteSpace($SecretKey)) {
    $initArgs["SecretKey"] = $SecretKey
  }
  if (-not [string]::IsNullOrWhiteSpace($CorsOrigins)) {
    $initArgs["CorsOrigins"] = $CorsOrigins
  }
  & $initScript @initArgs | Out-Host
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$archiveName = "sls_release_$timestamp.tar.gz"
$archivePath = Join-Path $env:TEMP $archiveName

Write-Host "[publish] Packaging workspace..."
Push-Location $projectRoot
try {
  tar `
    --exclude=".git" `
    --exclude="node_modules" `
    --exclude="frontend/node_modules" `
    --exclude="backend/venv" `
    --exclude="./logs" `
    --exclude="./logs/*" `
    --exclude="data" `
    --exclude="tmp_*" `
    --exclude="frontend/dev-dist" `
    --exclude=".env" `
    --exclude=".env.backup" `
    --exclude=".env.production" `
    --exclude=".env.example" `
    --exclude=".env.llm.example" `
    -czf $archivePath .
} finally {
  Pop-Location
}

Write-Host "[publish] Uploading archive to server..."
$commonSshOptions = @(
  "-o", "BatchMode=yes",
  "-o", "StrictHostKeyChecking=accept-new",
  "-o", "ServerAliveInterval=30",
  "-o", "ServerAliveCountMax=6"
)

$scpArgs = @("-i", $SshKeyPath, "-P", $SshPort) + $commonSshOptions + @(
  $archivePath,
  "$UserName@$HostName`:/tmp/$archiveName"
)
& scp @scpArgs | Out-Host
if ($LASTEXITCODE -ne 0) {
  throw "SCP failed with exit code: $LASTEXITCODE"
}

$remoteScript = @"
set -euo pipefail
mkdir -p $RemoteDir
tar -xzf /tmp/$archiveName -C $RemoteDir
cd $RemoteDir
chmod +x deploy/remote/setup-prod.sh
./deploy/remote/setup-prod.sh '$Domain' '$CertbotEmail' '$RemoteDir'
"@

Write-Host "[publish] Running remote deployment..."
$sshArgs = @("-i", $SshKeyPath, "-p", $SshPort) + $commonSshOptions + @(
  "$UserName@$HostName",
  $remoteScript
)
& ssh @sshArgs | Out-Host
if ($LASTEXITCODE -ne 0) {
  throw "SSH remote deploy failed with exit code: $LASTEXITCODE"
}

Write-Host "[done] Production publish completed: https://$Domain"

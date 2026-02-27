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

$remoteScriptTemplate = @'
set -euo pipefail

REMOTE_DIR='__REMOTE_DIR__'
DEPLOY_DOMAIN='__DEPLOY_DOMAIN__'
DEPLOY_EMAIL='__DEPLOY_EMAIL__'
ARCHIVE_PATH='/tmp/__ARCHIVE_NAME__'
BACKUP_DIR="${REMOTE_DIR%/}_backups"
KEEP_BACKUPS=5
BACKUP_FILE=""

mkdir -p "$REMOTE_DIR" "$BACKUP_DIR"

if [ -d "$REMOTE_DIR" ] && [ "$(ls -A "$REMOTE_DIR" 2>/dev/null)" ]; then
  BACKUP_FILE="$BACKUP_DIR/sls_release_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
  echo "[backup] Creating backup: $BACKUP_FILE"
  tar -czf "$BACKUP_FILE" -C "$REMOTE_DIR" .
else
  echo "[backup] No existing release directory content detected, skipping backup."
fi

cleanup_old_backups() {
  if ! command -v ls >/dev/null 2>&1; then
    return 0
  fi
  mapfile -t backups < <(ls -1t "$BACKUP_DIR"/sls_release_backup_*.tar.gz 2>/dev/null || true)
  if [ "${#backups[@]}" -le "$KEEP_BACKUPS" ]; then
    return 0
  fi

  for old_backup in "${backups[@]:$KEEP_BACKUPS}"; do
    rm -f "$old_backup"
  done
}

deploy_release() {
  echo "[publish] Extracting release archive into $REMOTE_DIR"
  tar -xzf "$ARCHIVE_PATH" -C "$REMOTE_DIR"
  cd "$REMOTE_DIR"
  chmod +x deploy/remote/setup-prod.sh
  ./deploy/remote/setup-prod.sh "$DEPLOY_DOMAIN" "$DEPLOY_EMAIL" "$REMOTE_DIR"
}

rollback_release() {
  if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
    echo "[rollback] No backup file available, cannot rollback automatically."
    return 1
  fi

  echo "[rollback] Restoring previous release from: $BACKUP_FILE"
  find "$REMOTE_DIR" -mindepth 1 -maxdepth 1 ! -name 'deploy' -exec rm -rf {} +
  tar -xzf "$BACKUP_FILE" -C "$REMOTE_DIR"
  cd "$REMOTE_DIR"
  chmod +x deploy/remote/setup-prod.sh
  ./deploy/remote/setup-prod.sh "$DEPLOY_DOMAIN" "$DEPLOY_EMAIL" "$REMOTE_DIR"
}

if deploy_release; then
  cleanup_old_backups
  echo "[done] Remote deployment completed."
  if [ -n "$BACKUP_FILE" ]; then
    echo "[done] Rollback backup retained at: $BACKUP_FILE"
  fi
else
  echo "[error] Remote deployment failed, attempting rollback..."
  if rollback_release; then
    echo "[rollback] Rollback completed."
  else
    echo "[rollback] Rollback failed."
  fi
  exit 1
fi
'@
$remoteScript = $remoteScriptTemplate.Replace("__REMOTE_DIR__", $RemoteDir).
  Replace("__DEPLOY_DOMAIN__", $Domain).
  Replace("__DEPLOY_EMAIL__", $CertbotEmail).
  Replace("__ARCHIVE_NAME__", $archiveName)
$remoteScriptEncoded = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($remoteScript))
$remoteExecCommand = "echo '$remoteScriptEncoded' | base64 -d | bash"

Write-Host "[publish] Running remote deployment..."
$sshArgs = @("-i", $SshKeyPath, "-p", $SshPort) + $commonSshOptions + @(
  "$UserName@$HostName",
  $remoteExecCommand
)
& ssh @sshArgs | Out-Host
if ($LASTEXITCODE -ne 0) {
  throw "SSH remote deploy failed with exit code: $LASTEXITCODE"
}

Write-Host "[done] Production publish completed: https://$Domain"
Write-Host "[done] Remote backups directory: ${RemoteDir}_backups"

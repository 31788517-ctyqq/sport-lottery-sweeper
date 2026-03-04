param(
  [Parameter(Mandatory = $true)][string]$HostName,
  [Parameter(Mandatory = $true)][string]$UserName,
  [Parameter(Mandatory = $true)][string]$RemoteDir,
  [Parameter(Mandatory = $true)][string]$SshKeyPath,
  [int]$SshPort = 22,
  [string]$TargetCommit = "HEAD",
  [string]$BaseCommit = "",
  [string]$InitialBaseCommit = "",
  [int]$KeepBackups = 10,
  [string]$BaselineFile = ".deploy/last_commit",
  [string]$PostDeployCommand = "",
  [string]$HealthCheckUrl = "",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Require-Command([string]$cmd) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    throw "Missing command: $cmd"
  }
}

function ConvertTo-ShellSingleQuoted([string]$value) {
  return "'" + $value.Replace("'", "'""'""'") + "'"
}

function Invoke-CheckedTool([string]$tool, [string[]]$commandArgs) {
  & $tool @commandArgs | Out-Host
  if ($LASTEXITCODE -ne 0) {
    throw "$tool failed with exit code: $LASTEXITCODE"
  }
}

function Get-RemoteBaselineCommit(
  [string]$hostName,
  [string]$user,
  [string]$key,
  [int]$port,
  [string[]]$sshOptions,
  [string]$baselinePath
) {
  $quotedBaselinePath = ConvertTo-ShellSingleQuoted $baselinePath
  $remoteCmd = "if [ -f $quotedBaselinePath ]; then cat $quotedBaselinePath; fi"
  $args = @("-i", $key, "-p", $port) + $sshOptions + @("$user@$hostName", $remoteCmd)
  $result = & ssh @args
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to query remote baseline commit (ssh exit code: $LASTEXITCODE)"
  }
  return ($result | Out-String).Trim()
}

function Wait-For-HealthCheck(
  [string]$hostName,
  [string]$user,
  [string]$key,
  [int]$port,
  [string[]]$sshOptions,
  [string]$url,
  [int]$maxRetries = 10
) {
  if ([string]::IsNullOrWhiteSpace($url)) {
    return
  }

  $quotedUrl = ConvertTo-ShellSingleQuoted $url
  for ($i = 1; $i -le $maxRetries; $i++) {
    Write-Host "[health] Attempt $i/$maxRetries -> $url"
    $checkCmd = "curl -fsS --max-time 15 $quotedUrl >/dev/null"
    $args = @("-i", $key, "-p", $port) + $sshOptions + @("$user@$hostName", $checkCmd)
    & ssh @args | Out-Host
    if ($LASTEXITCODE -eq 0) {
      Write-Host "[health] Healthy: $url"
      return
    }
    Start-Sleep -Seconds 6
  }

  throw "Health check failed after $maxRetries attempts: $url"
}

Require-Command "git"
Require-Command "ssh"
Require-Command "scp"
Require-Command "tar"

if (-not (Test-Path $SshKeyPath)) {
  throw "SSH key not found: $SshKeyPath"
}

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$remoteBaselinePath = "$RemoteDir/$BaselineFile"
$commonSshOptions = @(
  "-o", "BatchMode=yes",
  "-o", "StrictHostKeyChecking=accept-new",
  "-o", "ServerAliveInterval=30",
  "-o", "ServerAliveCountMax=6"
)

Push-Location $projectRoot
try {
  $resolvedTargetCommit = (& git rev-parse $TargetCommit).Trim()
  if ([string]::IsNullOrWhiteSpace($resolvedTargetCommit)) {
    throw "Unable to resolve target commit: $TargetCommit"
  }

  $selectedBaseCommit = $BaseCommit
  if ([string]::IsNullOrWhiteSpace($selectedBaseCommit)) {
    $remoteCommit = Get-RemoteBaselineCommit -hostName $HostName -user $UserName -key $SshKeyPath -port $SshPort -sshOptions $commonSshOptions -baselinePath $remoteBaselinePath
    if (-not [string]::IsNullOrWhiteSpace($remoteCommit)) {
      $selectedBaseCommit = $remoteCommit
      Write-Host "[sync] Using remote baseline commit: $selectedBaseCommit"
    }
  }
  if ([string]::IsNullOrWhiteSpace($selectedBaseCommit)) {
    $selectedBaseCommit = $InitialBaseCommit
    if (-not [string]::IsNullOrWhiteSpace($selectedBaseCommit)) {
      Write-Host "[sync] Using initial baseline commit: $selectedBaseCommit"
    }
  }
  if ([string]::IsNullOrWhiteSpace($selectedBaseCommit)) {
    throw "No baseline commit found. Set -BaseCommit or -InitialBaseCommit, or initialize $remoteBaselinePath on remote."
  }

  & git cat-file -e "$selectedBaseCommit`^{commit}" 2>$null
  if ($LASTEXITCODE -ne 0) {
    throw "Baseline commit not found locally: $selectedBaseCommit"
  }
  & git cat-file -e "$resolvedTargetCommit`^{commit}" 2>$null
  if ($LASTEXITCODE -ne 0) {
    throw "Target commit not found locally: $resolvedTargetCommit"
  }

  if ($selectedBaseCommit -eq $resolvedTargetCommit) {
    Write-Host "[sync] Baseline equals target, no changes to deploy."
    if ($DryRun) {
      return
    }
  }

  $diffLines = & git diff --name-status --find-renames "$selectedBaseCommit..$resolvedTargetCommit"
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to compute git diff: $selectedBaseCommit..$resolvedTargetCommit"
  }

  $uploadSet = New-Object System.Collections.Generic.HashSet[string] ([System.StringComparer]::Ordinal)
  $deleteSet = New-Object System.Collections.Generic.HashSet[string] ([System.StringComparer]::Ordinal)

  foreach ($line in $diffLines) {
    if ([string]::IsNullOrWhiteSpace($line)) {
      continue
    }
    $parts = $line -split "`t"
    $status = $parts[0]
    if ($status.StartsWith("R")) {
      if ($parts.Length -lt 3) {
        continue
      }
      [void]$deleteSet.Add($parts[1])
      [void]$uploadSet.Add($parts[2])
    } elseif ($status -eq "D") {
      if ($parts.Length -lt 2) {
        continue
      }
      [void]$deleteSet.Add($parts[1])
    } else {
      if ($parts.Length -lt 2) {
        continue
      }
      [void]$uploadSet.Add($parts[1])
    }
  }

  $uploadPaths = @($uploadSet | Sort-Object)
  $deletePaths = @($deleteSet | Sort-Object)

  Write-Host "[sync] Target commit : $resolvedTargetCommit"
  Write-Host "[sync] Baseline      : $selectedBaseCommit"
  Write-Host "[sync] Upload files  : $($uploadPaths.Count)"
  Write-Host "[sync] Delete files  : $($deletePaths.Count)"

  if ($DryRun) {
    if ($uploadPaths.Count -gt 0) {
      Write-Host "[dry-run] Upload candidates:"
      $uploadPaths | ForEach-Object { Write-Host "  + $_" }
    }
    if ($deletePaths.Count -gt 0) {
      Write-Host "[dry-run] Delete candidates:"
      $deletePaths | ForEach-Object { Write-Host "  - $_" }
    }
    return
  }

  $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $tempRoot = Join-Path $env:TEMP ("sls_patch_" + [Guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null

  $uploadListPath = Join-Path $tempRoot "upload_files.txt"
  $deleteListPath = Join-Path $tempRoot "delete_files.txt"
  $patchTarPath = Join-Path $tempRoot "patch.tar.gz"

  try {
    Set-Content -Path $uploadListPath -Value ($uploadPaths -join "`n") -Encoding ascii
    Set-Content -Path $deleteListPath -Value ($deletePaths -join "`n") -Encoding ascii

    if ($uploadPaths.Count -gt 0) {
      Invoke-CheckedTool -tool "tar" -commandArgs @("-czf", $patchTarPath, "-C", $projectRoot, "-T", $uploadListPath)
    } else {
      Set-Content -Path $patchTarPath -Value "" -Encoding ascii
    }

    $remotePatchPath = "/tmp/sls_patch_${timestamp}.tar.gz"
    $remoteUploadList = "/tmp/sls_patch_upload_${timestamp}.txt"
    $remoteDeleteList = "/tmp/sls_patch_delete_${timestamp}.txt"

    $scpCommon = @("-i", $SshKeyPath, "-P", $SshPort) + $commonSshOptions

    Invoke-CheckedTool -tool "scp" -commandArgs ($scpCommon + @($uploadListPath, "$UserName@$HostName`:$remoteUploadList"))
    Invoke-CheckedTool -tool "scp" -commandArgs ($scpCommon + @($deleteListPath, "$UserName@$HostName`:$remoteDeleteList"))
    if ($uploadPaths.Count -gt 0) {
      Invoke-CheckedTool -tool "scp" -commandArgs ($scpCommon + @($patchTarPath, "$UserName@$HostName`:$remotePatchPath"))
    }

    $postDeployB64 = ""
    if (-not [string]::IsNullOrWhiteSpace($PostDeployCommand)) {
      $postDeployB64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($PostDeployCommand))
    }

    $remoteScriptTemplate = @'
set -euo pipefail

REMOTE_DIR=__REMOTE_DIR__
BASELINE_PATH=__BASELINE_PATH__
BACKUP_DIR="${REMOTE_DIR%/}_patch_backups"
KEEP_BACKUPS=__KEEP_BACKUPS__
TARGET_COMMIT=__TARGET_COMMIT__
PATCH_FILE=__PATCH_FILE__
UPLOAD_LIST=__UPLOAD_LIST__
DELETE_LIST=__DELETE_LIST__
POST_DEPLOY_B64=__POST_DEPLOY_B64__

mkdir -p "$REMOTE_DIR" "$(dirname "$BASELINE_PATH")" "$BACKUP_DIR"
TMP_BACKUP="$(mktemp -d)"
HAS_BACKUP=0

is_safe_rel_path() {
  local rel="$1"
  if [[ -z "$rel" || "$rel" == /* || "$rel" == *".."* ]]; then
    return 1
  fi
  return 0
}

backup_rel_path_if_exists() {
  local rel="$1"
  local src="$REMOTE_DIR/$rel"
  if [[ -e "$src" ]]; then
    mkdir -p "$TMP_BACKUP/$(dirname "$rel")"
    cp -a "$src" "$TMP_BACKUP/$rel"
    HAS_BACKUP=1
  fi
}

while IFS= read -r rel || [[ -n "$rel" ]]; do
  [[ -z "$rel" ]] && continue
  if is_safe_rel_path "$rel"; then
    backup_rel_path_if_exists "$rel"
  fi
done < "$UPLOAD_LIST"

while IFS= read -r rel || [[ -n "$rel" ]]; do
  [[ -z "$rel" ]] && continue
  if is_safe_rel_path "$rel"; then
    backup_rel_path_if_exists "$rel"
  fi
done < "$DELETE_LIST"

BACKUP_FILE=""
if [[ "$HAS_BACKUP" -eq 1 ]]; then
  BACKUP_FILE="$BACKUP_DIR/sls_patch_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
  tar -czf "$BACKUP_FILE" -C "$TMP_BACKUP" .
  echo "[backup] Patch backup: $BACKUP_FILE"
else
  echo "[backup] No existing files needed backup."
fi

if [[ -s "$PATCH_FILE" ]]; then
  tar -xzf "$PATCH_FILE" -C "$REMOTE_DIR"
fi

while IFS= read -r rel || [[ -n "$rel" ]]; do
  [[ -z "$rel" ]] && continue
  if is_safe_rel_path "$rel"; then
    rm -rf "$REMOTE_DIR/$rel"
  fi
done < "$DELETE_LIST"

if [[ -n "$POST_DEPLOY_B64" ]]; then
  POST_DEPLOY_CMD="$(printf '%s' "$POST_DEPLOY_B64" | base64 -d)"
  echo "[deploy] Running post-deploy command..."
  bash -lc "$POST_DEPLOY_CMD"
fi

echo "$TARGET_COMMIT" > "$BASELINE_PATH"
echo "[deploy] Baseline updated: $BASELINE_PATH -> $TARGET_COMMIT"

mapfile -t backups < <(ls -1t "$BACKUP_DIR"/sls_patch_backup_*.tar.gz 2>/dev/null || true)
if [[ "${#backups[@]}" -gt "$KEEP_BACKUPS" ]]; then
  for old_backup in "${backups[@]:$KEEP_BACKUPS}"; do
    rm -f "$old_backup"
  done
fi

rm -f "$PATCH_FILE" "$UPLOAD_LIST" "$DELETE_LIST"
rm -rf "$TMP_BACKUP"
'@

    $remoteScript = $remoteScriptTemplate.
      Replace("__REMOTE_DIR__", (ConvertTo-ShellSingleQuoted $RemoteDir)).
      Replace("__BASELINE_PATH__", (ConvertTo-ShellSingleQuoted $remoteBaselinePath)).
      Replace("__KEEP_BACKUPS__", $KeepBackups.ToString()).
      Replace("__TARGET_COMMIT__", (ConvertTo-ShellSingleQuoted $resolvedTargetCommit)).
      Replace("__PATCH_FILE__", (ConvertTo-ShellSingleQuoted $remotePatchPath)).
      Replace("__UPLOAD_LIST__", (ConvertTo-ShellSingleQuoted $remoteUploadList)).
      Replace("__DELETE_LIST__", (ConvertTo-ShellSingleQuoted $remoteDeleteList)).
      Replace("__POST_DEPLOY_B64__", (ConvertTo-ShellSingleQuoted $postDeployB64))

    $remoteScriptEncoded = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($remoteScript))
    $remoteExecCmd = "echo '$remoteScriptEncoded' | base64 -d | bash"
    Invoke-CheckedTool -tool "ssh" -commandArgs (@("-i", $SshKeyPath, "-p", $SshPort) + $commonSshOptions + @("$UserName@$HostName", $remoteExecCmd))

    Wait-For-HealthCheck -hostName $HostName -user $UserName -key $SshKeyPath -port $SshPort -sshOptions $commonSshOptions -url $HealthCheckUrl

    Write-Host "[done] Incremental publish completed: $HostName ($resolvedTargetCommit)"
  } finally {
    if (Test-Path $tempRoot) {
      Remove-Item -Path $tempRoot -Force -Recurse
    }
  }
} finally {
  Pop-Location
}

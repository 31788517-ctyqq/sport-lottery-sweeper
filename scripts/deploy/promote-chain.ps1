param(
  [string]$ConfigPath = "",
  [string]$TargetCommit = "HEAD",
  [switch]$SkipLocalChecks,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Require-Command([string]$cmd) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    throw "Missing command: $cmd"
  }
}

function Run-LocalGateChecks([string]$projectRoot) {
  Write-Host "[local] Running local gate checks..."

  Push-Location $projectRoot
  try {
    $commands = @(
      @("python", "scripts/project_health_check.py"),
      @("python", "-m", "pytest"),
      @("npm", "--prefix", "frontend", "run", "lint"),
      @("npm", "--prefix", "frontend", "run", "build")
    )

    foreach ($cmd in $commands) {
      $tool = $cmd[0]
      $args = @()
      if ($cmd.Length -gt 1) {
        $args = $cmd[1..($cmd.Length - 1)]
      }
      Write-Host "[local] > $tool $($args -join ' ')"
      & $tool @args | Out-Host
      if ($LASTEXITCODE -ne 0) {
        throw "Local check failed: $tool $($args -join ' ')"
      }
    }
  } finally {
    Pop-Location
  }
}

Require-Command "git"

$scriptDir = (Resolve-Path $PSScriptRoot).Path
$projectRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path

if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
  $ConfigPath = Join-Path $scriptDir "promotion-pipeline.json"
}
if (-not (Test-Path $ConfigPath)) {
  throw "Config file not found: $ConfigPath"
}

$config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
if ($null -eq $config.stages -or $config.stages.Count -eq 0) {
  throw "Config must define at least one stage under 'stages'."
}

Push-Location $projectRoot
try {
  $resolvedTargetCommit = (& git rev-parse $TargetCommit).Trim()
  if ([string]::IsNullOrWhiteSpace($resolvedTargetCommit)) {
    throw "Unable to resolve target commit: $TargetCommit"
  }
} finally {
  Pop-Location
}

$shouldRunLocalChecks = -not $SkipLocalChecks
if ($config.runLocalChecks -eq $false) {
  $shouldRunLocalChecks = $false
}
if ($shouldRunLocalChecks -and -not $DryRun) {
  Run-LocalGateChecks -projectRoot $projectRoot
} elseif ($DryRun) {
  Write-Host "[dry-run] Skipping local checks in dry-run mode."
}

$incrementalScript = Join-Path $scriptDir "incremental-publish.ps1"
if (-not (Test-Path $incrementalScript)) {
  throw "Missing script: $incrementalScript"
}

$globalSshKeyPath = [string]$config.sshKeyPath
$globalSshPort = 22
if ($null -ne $config.sshPort -and "$($config.sshPort)" -ne "") {
  $globalSshPort = [int]$config.sshPort
}
$globalKeepBackups = 10
if ($null -ne $config.keepBackups -and "$($config.keepBackups)" -ne "") {
  $globalKeepBackups = [int]$config.keepBackups
}

$stageIndex = 0
foreach ($stage in $config.stages) {
  $stageIndex++
  $enabled = $true
  if ($null -ne $stage.enabled) {
    $enabled = [bool]$stage.enabled
  }
  if (-not $enabled) {
    Write-Host "[pipeline] Skipping disabled stage #${stageIndex}: $($stage.name)"
    continue
  }

  $stageName = [string]$stage.name
  if ([string]::IsNullOrWhiteSpace($stageName)) {
    $stageName = "stage-$stageIndex"
  }

  $stageHost = [string]$stage.host
  $user = [string]$stage.user
  $remoteDir = [string]$stage.remoteDir
  if ([string]::IsNullOrWhiteSpace($stageHost) -or [string]::IsNullOrWhiteSpace($user) -or [string]::IsNullOrWhiteSpace($remoteDir)) {
    throw "Stage '$stageName' requires host/user/remoteDir."
  }

  $sshKeyPath = $globalSshKeyPath
  if (-not [string]::IsNullOrWhiteSpace([string]$stage.sshKeyPath)) {
    $sshKeyPath = [string]$stage.sshKeyPath
  }
  if ([string]::IsNullOrWhiteSpace($sshKeyPath)) {
    throw "Stage '$stageName' requires sshKeyPath (stage-level or global)."
  }

  $sshPort = $globalSshPort
  if ($null -ne $stage.sshPort -and "$($stage.sshPort)" -ne "") {
    $sshPort = [int]$stage.sshPort
  }

  $keepBackups = $globalKeepBackups
  if ($null -ne $stage.keepBackups -and "$($stage.keepBackups)" -ne "") {
    $keepBackups = [int]$stage.keepBackups
  }

  Write-Host "[pipeline] Stage #${stageIndex} -> $stageName (${user}@${stageHost}:${remoteDir})"

  $invokeArgs = @{
    HostName = $stageHost
    UserName = $user
    RemoteDir = $remoteDir
    SshKeyPath = $sshKeyPath
    SshPort = $sshPort
    TargetCommit = $resolvedTargetCommit
    KeepBackups = $keepBackups
  }

  if (-not [string]::IsNullOrWhiteSpace([string]$stage.baseCommit)) {
    $invokeArgs["BaseCommit"] = [string]$stage.baseCommit
  }
  if (-not [string]::IsNullOrWhiteSpace([string]$stage.initialBaseCommit)) {
    $invokeArgs["InitialBaseCommit"] = [string]$stage.initialBaseCommit
  }
  if (-not [string]::IsNullOrWhiteSpace([string]$stage.postDeployCommand)) {
    $invokeArgs["PostDeployCommand"] = [string]$stage.postDeployCommand
  }
  if (-not [string]::IsNullOrWhiteSpace([string]$stage.healthCheckUrl)) {
    $invokeArgs["HealthCheckUrl"] = [string]$stage.healthCheckUrl
  }
  if (-not [string]::IsNullOrWhiteSpace([string]$stage.baselineFile)) {
    $invokeArgs["BaselineFile"] = [string]$stage.baselineFile
  }
  if ($DryRun) {
    $invokeArgs["DryRun"] = $true
  }

  & $incrementalScript @invokeArgs
  if ($LASTEXITCODE -ne 0) {
    throw "Stage '$stageName' failed."
  }

  Write-Host "[pipeline] Stage '$stageName' completed."
}

Write-Host "[done] Promotion pipeline completed. Target commit: $resolvedTargetCommit"

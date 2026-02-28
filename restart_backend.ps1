param(
    [int]$Port = 8000,
    [switch]$Reload
)

$ErrorActionPreference = "Stop"

function Get-ListeningPids {
    param([int]$LocalPort)
    $lines = netstat -ano | Select-String -Pattern (":{0}" -f $LocalPort) | Select-String -Pattern "LISTENING"
    $pids = @()
    foreach ($line in $lines) {
        $parts = ($line.ToString() -split "\s+") | Where-Object { $_ -ne "" }
        if ($parts.Count -gt 0) {
            $pidText = $parts[-1]
            if ($pidText -match "^\d+$") {
                $pids += [int]$pidText
            }
        }
    }
    return $pids | Sort-Object -Unique
}

function Stop-ProcessTree {
    param([int]$ProcessId)
    try {
        $children = Get-CimInstance Win32_Process -Filter "ParentProcessId = $ProcessId" -ErrorAction SilentlyContinue
        foreach ($child in $children) {
            Stop-ProcessTree -ProcessId ([int]$child.ProcessId)
        }
        Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
    } catch {
        # Ignore race conditions where process exits between discovery and kill.
    }
}

Write-Host "Stopping backend service on port $Port..." -ForegroundColor Yellow

# 1) Kill known uvicorn launcher trees (cmd/python).
$uvicornLaunchers = Get-CimInstance Win32_Process | Where-Object {
    $cmd = [string]$_.CommandLine
    ($_.Name -in @("python.exe", "cmd.exe")) -and
    $cmd -match "uvicorn\s+backend\.main:app" -and
    $cmd -match ("--port\s+{0}\b" -f $Port)
}

foreach ($proc in $uvicornLaunchers) {
    Write-Host ("Terminating uvicorn process tree PID {0} ({1})" -f $proc.ProcessId, $proc.Name) -ForegroundColor Cyan
    Stop-ProcessTree -ProcessId ([int]$proc.ProcessId)
}

# 2) Kill orphan multiprocessing workers that still hold the port via parent_pid.
$listenerPids = Get-ListeningPids -LocalPort $Port
if ($listenerPids.Count -gt 0) {
    $orphanWorkers = Get-CimInstance Win32_Process | Where-Object {
        $cmd = [string]$_.CommandLine
        $_.Name -eq "python.exe" -and
        $cmd -match "spawn_main\(parent_pid=" -and
        (($listenerPids | Where-Object {
            $pidText = [string]$_
            $pidText -match "^\d+$" -and $cmd -match ("parent_pid=" + [regex]::Escape($pidText) + "\b")
        }).Count -gt 0)
    }

    foreach ($worker in $orphanWorkers) {
        Write-Host ("Terminating orphan worker PID {0}" -f $worker.ProcessId) -ForegroundColor Cyan
        Stop-Process -Id ([int]$worker.ProcessId) -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Seconds 2

$stillListening = Get-ListeningPids -LocalPort $Port
if ($stillListening.Count -gt 0) {
    Write-Host ("Port $Port is still in use by PIDs: " + ($stillListening -join ", ")) -ForegroundColor Red
    Write-Host "Please inspect manually before restart." -ForegroundColor Red
    exit 1
}

Write-Host "Port $Port is free." -ForegroundColor Green

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$reloadFlag = if ($Reload.IsPresent) { "--reload" } else { "" }
$cmdLine = "cd /d `"$projectRoot`" && python -m uvicorn backend.main:app --host 0.0.0.0 --port $Port $reloadFlag"

Write-Host "Starting backend service..." -ForegroundColor Yellow
$proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $cmdLine -PassThru

Start-Sleep -Seconds 2
$checkPids = Get-ListeningPids -LocalPort $Port
if ($checkPids.Count -gt 0) {
    Write-Host ("Backend started. PID(s): " + ($checkPids -join ", ")) -ForegroundColor Green
    Write-Host ("API docs: http://localhost:{0}/docs" -f $Port) -ForegroundColor Green
    if (-not $Reload.IsPresent) {
        Write-Host "Reload is OFF by default to avoid orphan workers. Set BACKEND_RELOAD=1 to enable." -ForegroundColor Gray
    }
} else {
    Write-Host "Backend start command launched, but port is not listening yet. Check the backend console window." -ForegroundColor Yellow
}

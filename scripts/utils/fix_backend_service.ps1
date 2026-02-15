Write-Host "========================================"
Write-Host "?????? - ??????????"
Write-Host "========================================"
Write-Host ""
Set-Location $PSScriptRoot
Write-Host "[1/4] ??????..."
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Write-Host ""
Write-Host "[2/4] ?????..."
if (-Not (Test-Path "../../data/sport_lottery.db")) {
    Write-Host "???????..."
    New-Item -ItemType File -Path "../../data/sport_lottery.db" -Force | Out-Null
}
Write-Host "???????"
Write-Host ""
Write-Host "[3/4] ??????..."
Set-Location "backend"
Start-Process "cmd.exe" -ArgumentList "/k python main.py" -WindowStyle Normal
Set-Location ..
Write-Host "???????????10?..."
Start-Sleep -Seconds 10
Write-Host ""
Write-Host "[4/4] ??API..."
Write-Host "??????..."
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "??????"
} catch {
    Write-Host "????????????"
}
Write-Host ""
Write-Host "========================================"
Write-Host "?????"
Write-Host "????:"
Write-Host "  - ??: http://localhost:3000/admin-users"
Write-Host "  - API: http://localhost:8000/api/v1/admin-users/"
Write-Host "========================================"
Pause

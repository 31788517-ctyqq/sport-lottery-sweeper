# restart_dev.ps1 - 一键重启前端和后端开发服务

Write-Host "==== 正在停止占用端口的进程 ====" -ForegroundColor Yellow

# 停止前端端口 3000
$frontendPid = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($frontendPid) {
    Stop-Process -Id $frontendPid -Force
    Write-Host "已停止前端进程 (PID $frontendPid) 端口 3000" -ForegroundColor Green
}

# 停止后端端口 8000
$backendPid = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($backendPid) {
    Stop-Process -Id $backendPid -Force
    Write-Host "已停止后端进程 (PID $backendPid) 端口 8000" -ForegroundColor Green
}

Start-Sleep -Seconds 2

Write-Host "==== 启动后端服务 ====" -ForegroundColor Yellow
$backendPath = "c:/Users/11581/Downloads/sport-lottery-sweeper/backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$backendPath'; python start_backend.py"
Write-Host "后端已启动，监听 http://localhost:8000" -ForegroundColor Green

Start-Sleep -Seconds 3

Write-Host "==== 启动前端服务 ====" -ForegroundColor Yellow
$frontendPath = "c:/Users/11581/Downloads/sport-lottery-sweeper/frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$frontendPath'; npm run dev"
Write-Host "前端已启动，监听 http://localhost:3000" -ForegroundColor Green

Write-Host "==== 重启完成 ====" -ForegroundColor Cyan
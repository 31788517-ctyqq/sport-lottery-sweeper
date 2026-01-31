# 重启后端服务脚本
Write-Host "正在停止后端服务..." -ForegroundColor Yellow

# 查找并停止占用8000端口的进程
$port = 8000
$listening = netstat -ano | findstr ":$port.*LISTENING"
if ($listening) {
    $pidMatch = $listening -split '\s+'
    $pidToKill = $pidMatch[-1]
    Write-Host "发现占用端口 $port 的进程 PID: $pidToKill" -ForegroundColor Cyan
    taskkill /PID $pidToKill /F
    Start-Sleep -Seconds 2
    Write-Host "进程已终止" -ForegroundColor Green
} else {
    Write-Host "端口 $port 未被占用" -ForegroundColor Gray
}

# 启动后端服务
Write-Host "正在启动后端服务..." -ForegroundColor Yellow
cd backend
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
python main.py
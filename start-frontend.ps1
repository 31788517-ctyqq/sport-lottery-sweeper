Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "   体育彩票扫盘系统前端启动脚本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 切换到frontend目录
Set-Location "$PSScriptRoot\frontend"

# 检查是否安装了npm
try {
    $npmVersion = npm --version 2>$null
    if (-not $npmVersion) {
        Write-Host "错误: 未找到npm，请先安装Node.js" -ForegroundColor Red
        Read-Host "按任意键退出..."
        exit 1
    }
} catch {
    Write-Host "错误: 未找到npm，请先安装Node.js" -ForegroundColor Red
    Read-Host "按任意键退出..."
    exit 1
}

# 检查是否安装了依赖
if (!(Test-Path "node_modules")) {
    Write-Host "检测到未安装依赖，开始安装..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "依赖安装失败，请检查网络连接或npm配置" -ForegroundColor Red
        Read-Host "按任意键退出..."
        exit 1
    }
    Write-Host "依赖安装完成" -ForegroundColor Green
    Write-Host ""
}

# 尝试启动前端开发服务器，如果3004端口被占用，则依次尝试3005, 3006, 3007
$port = 3004
do {
    $portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-Host "端口 $port 已被占用" -ForegroundColor Yellow
        if ($port -ge 3007) {
            Write-Host "所有预设端口都被占用，请手动释放端口后重试" -ForegroundColor Red
            Read-Host "按任意键退出..."
            exit 1
        }
        $port++
        Write-Host "尝试端口 $port" -ForegroundColor Yellow
    } else {
        break
    }
} while ($true)

Write-Host "正在启动前端开发服务器，端口: $port" -ForegroundColor Green
npm run dev -- --port $port

Read-Host "按任意键退出..."
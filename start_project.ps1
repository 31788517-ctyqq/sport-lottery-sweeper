Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   竞彩足球扫盘系统 - 项目启动脚本" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 获取当前脚本目录
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = $ProjectRoot
$FrontendDir = Join-Path $BackendDir "frontend"

Write-Host "时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

Write-Host "📍 后端路径: $BackendDir" -ForegroundColor Yellow
Write-Host "📍 前端路径: $FrontendDir" -ForegroundColor Yellow
Write-Host ""

# 检查环境
Write-Host "🔍 检查环境..." -ForegroundColor Cyan

# 检查Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js 版本: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js 未找到，请安装 Node.js 18 或更高版本" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python 版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 未找到，请安装 Python 3.8 或更高版本" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""
Write-Host "🚀 启动后端服务..." -ForegroundColor Cyan

# 检查并终止占用端口的进程
function Stop-PortProcess {
    param([int]$Port)
    
    $ports = netstat -ano | findstr ":$Port "
    if ($LASTEXITCODE -eq 0) {
        Write-Host "⚠️  端口 $Port 被占用，正在释放..." -ForegroundColor Yellow
        foreach ($line in $ports) {
            $fields = $line -split '\s+'
            if ($fields.Count -ge 5) {
                $pid = $fields[4]
                if ($pid -ne "" -and $pid -ne "PID") {
                    try {
                        Stop-Process -Id $pid -Force
                        Write-Host "✅ 已终止 PID $pid" -ForegroundColor Green
                    } catch {
                        Write-Host "⚠️  无法终止 PID $pid" -ForegroundColor Yellow
                    }
                }
            }
        }
    }
}

Stop-PortProcess -Port 8000
Stop-PortProcess -Port 8001

Write-Host ""
Write-Host "🌐 启动后端服务 (端口 8001)..." -ForegroundColor Cyan

# 启动后端服务
$backendScript = @"
from src.backend.optimized_main import app
import uvicorn
uvicorn.run(app, host='127.0.0.1', port=8001, log_level='info')
"@

# 启动后端服务在后台
$backendProc = Start-Process -FilePath "python" -ArgumentList "-c", $backendScript -WorkingDirectory $BackendDir -PassThru
Write-Host "✅ 后端服务已启动 (端口 8001, PID: $($backendProc.Id))" -ForegroundColor Green

Start-Sleep -Seconds 3

# 启动前端服务
Write-Host ""
Write-Host "🖥️  启动前端服务 (端口 3000)..." -ForegroundColor Cyan

if (Test-Path $FrontendDir) {
    Write-Host "📦 检查前端依赖..." -ForegroundColor Cyan
    
    Push-Location $FrontendDir
    
    # 检查是否已安装依赖
    if (!(Test-Path "node_modules")) {
        Write-Host "📦 安装前端依赖..." -ForegroundColor Cyan
        npm install
    }
    
    # 在后台启动前端开发服务器
    $frontendProc = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory $FrontendDir -PassThru
    Write-Host "✅ 前端开发服务器已启动 (端口 3000, PID: $($frontendProc.Id))" -ForegroundColor Green
    
    Pop-Location
} else {
    Write-Host "⚠️  前端目录不存在: $FrontendDir" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "🎯 访问地址:" -ForegroundColor Cyan
Write-Host "  后端 API: http://127.0.0.1:8001" -ForegroundColor White
Write-Host "  后端文档: http://127.0.0.1:8001/docs" -ForegroundColor White
Write-Host "  前端界面: http://127.0.0.1:3000" -ForegroundColor White
Write-Host "  前端竞彩页面: http://127.0.0.1:3000/jczq" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📝 注意事项:" -ForegroundColor Yellow
Write-Host "  1. 确保防火墙允许相关端口通信"
Write-Host "  2. 如前端无法连接后端，请检查代理配置"
Write-Host "  3. 如果服务启动失败，请查看对应日志"
Write-Host ""

Read-Host "按回车键退出"
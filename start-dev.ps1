#!/usr/bin/env pwsh
# 竞彩足球扫盘系统 - 开发环境启动脚本

Write-Host "🚀 启动竞彩足球扫盘系统开发环境..." -ForegroundColor Green

# 检查Python环境
Write-Host "\n📋 检查Python环境..." -ForegroundColor Yellow
$pythonVersion = python --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python未安装或未添加到PATH" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green

# 检查Node.js环境
Write-Host "\n📋 检查Node.js环境..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js未安装或未添加到PATH" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js $nodeVersion" -ForegroundColor Green

# 创建必要的目录
Write-Host "\n📁 创建必要目录..." -ForegroundColor Yellow
$directories = @(
    "logs",
    "uploads",
    "backend/uploads",
    "frontend/dist"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ 创建目录: $dir" -ForegroundColor Green
    }
}

# 启动后端服务
Write-Host "\n🔧 启动后端服务..." -ForegroundColor Yellow
Start-Job -ScriptBlock {
    Set-Location "$using:PWD\backend"
    python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
} -Name "BackendServer"
Write-Host "  ✅ 后端服务启动中 (http://localhost:8001)" -ForegroundColor Green

# 等待后端服务启动
Write-Host "  ⏳ 等待后端服务就绪..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 启动前端服务
Write-Host "\n🎨 启动前端服务..." -ForegroundColor Yellow
$frontendPath = "frontend"
if (Test-Path $frontendPath) {
    Set-Location $frontendPath
    Start-Job -ScriptBlock {
        Set-Location "$using:PWD"
        npm run dev
    } -Name "FrontendServer"
    Write-Host "  ✅ 前端服务启动中 (http://localhost:3000)" -ForegroundColor Green
    Set-Location ".."
} else {
    Write-Host "  ⚠️  前端目录不存在，跳过前端启动" -ForegroundColor Yellow
}

# 显示服务信息
Write-Host "\n🎉 开发环境启动完成！" -ForegroundColor Green
Write-Host "\n📱 服务地址:" -ForegroundColor Cyan
Write-Host "  后端API: http://localhost:8001" -ForegroundColor White
Write-Host "  前端界面: http://localhost:3000" -ForegroundColor White
Write-Host "  API文档: http://localhost:8001/docs" -ForegroundColor White
Write-Host "  ReDoc文档: http://localhost:8001/redoc" -ForegroundColor White

Write-Host "\n🔧 管理命令:" -ForegroundColor Cyan
Write-Host "  查看后端日志: Get-Job BackendServer | Receive-Job -Keep" -ForegroundColor Gray
Write-Host "  查看前端日志: Get-Job FrontendServer | Receive-Job -Keep" -ForegroundColor Gray
Write-Host "  停止所有服务: Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor Gray
Write-Host "  重启后端: Get-Job BackendServer | Stop-Job; Remove-Job BackendServer" -ForegroundColor Gray

Write-Host "\n💡 提示:" -ForegroundColor Cyan
Write-Host "  - 首次运行请先执行: python backend/init_db.py" -ForegroundColor Yellow
Write-Host "  - 默认管理员账号: superadmin / Admin123456!" -ForegroundColor Yellow
Write-Host "  - 按 Ctrl+C 停止此脚本，使用上面的命令停止服务" -ForegroundColor Yellow

# 保持脚本运行
Write-Host "\n⚡ 按任意键停止所有服务并退出..." -ForegroundColor Magenta
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# 清理后台任务
Write-Host "\n🛑 停止所有服务..." -ForegroundColor Yellow
Get-Job | Stop-Job
Get-Job | Remove-Job
Write-Host "✅ 所有服务已停止" -ForegroundColor Green
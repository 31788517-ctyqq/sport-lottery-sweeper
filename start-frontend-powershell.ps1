# 前端启动脚本 (PowerShell版)
# 使用方法: 在PowerShell中执行 .\start-frontend-powershell.ps1

chcp 65001 | Out-Null
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "前端启动脚本 (PowerShell)" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 切换到frontend目录
$frontendPath = Join-Path $PSScriptRoot "frontend"
Set-Location $frontendPath
Write-Host "当前目录: $PWD" -ForegroundColor Yellow
Write-Host ""

# 检查Node.js
Write-Host "[1/4] 检查Node.js和pnpm..." -ForegroundColor Green
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js未安装!" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}

try {
    $pnpmVersion = pnpm --version
    Write-Host "✅ pnpm: $pnpmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pnpm未安装!" -ForegroundColor Red
    Write-Host "请安装: npm install -g pnpm" -ForegroundColor Yellow
    Read-Host "按回车退出"
    exit 1
}
Write-Host ""

# 检查package.json
Write-Host "[2/4] 检查package.json..." -ForegroundColor Green
if (-not (Test-Path "package.json")) {
    Write-Host "❌ package.json不存在!" -ForegroundColor Red
    Write-Host "当前目录: $PWD" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}
Write-Host "✅ package.json存在" -ForegroundColor Green
Write-Host ""

# 检查依赖
Write-Host "[3/4] 检查依赖..." -ForegroundColor Green
if (-not (Test-Path "node_modules")) {
    Write-Host "⚠️ node_modules不存在" -ForegroundColor Yellow
    Write-Host "正在安装依赖..." -ForegroundColor Yellow
    pnpm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 依赖安装失败!" -ForegroundColor Red
        Read-Host "按回车退出"
        exit 1
    }
    Write-Host "✅ 依赖安装成功" -ForegroundColor Green
} else {
    Write-Host "✅ node_modules已存在" -ForegroundColor Green
}
Write-Host ""

# 启动前端
Write-Host "[4/4] 启动前端开发服务器..." -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "前端将在以下地址运行:" -ForegroundColor White
Write-Host "  - 本地: http://localhost:3000" -ForegroundColor Green
Write-Host "  - 网络: http://0.0.0.0:3000" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

pnpm run dev

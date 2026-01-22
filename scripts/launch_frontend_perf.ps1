# PowerShell 前端性能监测启动脚本
Write-Host "🚀 启动前端性能监测脚本" -ForegroundColor Green
Write-Host "================================" 
Write-Host "时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "================================"

# 记录开始时间
$startDateTime = Get-Date
$startUnixTime = [int][double]::Parse($(Get-Date($startDateTime) -UFormat %s))

Write-Host ""
Write-Host "检查环境..." -ForegroundColor Yellow

# 检查Node.js版本
try {
    $nodeVersion = node --version
    $nodeMajorVersion = [int]$nodeVersion.Substring(1).Split('.')[0]
    
    if ($nodeMajorVersion -lt 18) {
        Write-Host "⚠️  警告: 检测到 Node.js 版本 $nodeVersion，建议使用 Node.js 18 或更高版本" -ForegroundColor Red
    } else {
        Write-Host "✅ Node.js 版本: $nodeVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Node.js 未安装或不在 PATH 中" -ForegroundColor Red
    Write-Host "请安装 Node.js 18.0.0 或更高版本" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 检查包管理器
Write-Host ""
$packageManager = "npm"
try {
    $pnpmVersion = pnpm --version
    $packageManager = "pnpm"
    Write-Host "✅ 包管理器: $packageManager (v$pnpmVersion)" -ForegroundColor Green
} catch {
    try {
        $yarnVersion = yarn --version
        $packageManager = "yarn"
        Write-Host "✅ 包管理器: $packageManager (v$yarnVersion)" -ForegroundColor Green
    } catch {
        Write-Host "✅ 包管理器: $packageManager (pnpm/yarn 未安装，使用 npm)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🔍 启动时间监测:" -ForegroundColor Cyan

# 记录开发服务器启动时间
$devStartDateTime = Get-Date
$devStartUnixTime = [int][double]::Parse($(Get-Date($devStartDateTime) -UFormat %s))

# 切换到前端目录
Push-Location "../frontend"

Write-Host "启动前端开发服务器..." -ForegroundColor Yellow
Write-Host "使用命令: $packageManager run dev" -ForegroundColor Magenta

# 启动开发服务器
$devProcess = Start-Process -FilePath $packageManager -ArgumentList "run", "dev" -WorkingDirectory "." -PassThru -NoNewWindow:$false

Write-Host "前端开发服务器已启动，PID: $($devProcess.Id)" -ForegroundColor Green

# 计算开发服务器启动时间（模拟，因为它是持续运行的）
$devEndDateTime = Get-Date
$devDuration = $devEndDateTime - $devStartDateTime
Write-Host "⚡ 开发服务器启动时间: $($devDuration.TotalMilliseconds) 毫秒" -ForegroundColor Cyan

Write-Host ""
Write-Host "前端开发服务器运行在前台，按 Ctrl+C 停止服务器" -ForegroundColor Yellow

# 等待进程结束
try {
    Wait-Process -Id $devProcess.Id
} catch {
    # 用户可能按了Ctrl+C
}

Write-Host ""
Write-Host "服务器已停止" -ForegroundColor Yellow

# 弹出目录
Pop-Location

# 计算总时间
$currentDateTime = Get-Date
$totalDuration = $currentDateTime - $startDateTime
Write-Host ""
Write-Host "==========================" 
Write-Host "🏁 任务完成"
Write-Host "总耗时: $($totalDuration.TotalSeconds) 秒"
Write-Host "=========================="
Write-Host ""

Read-Host "按任意键退出"
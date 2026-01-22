# start_frontend.ps1
Write-Host "🧹 清理 npm 缓存..." -ForegroundColor Green
npm cache clean --force

Write-Host "🗑️ 删除 node_modules 和 package-lock.json..." -ForegroundColor Green
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue

Write-Host "📦 重新安装依赖（使用 --legacy-peer-deps）..." -ForegroundColor Green
npm install --legacy-peer-deps
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 依赖安装失败，请检查网络或 npm 版本" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 启动前端开发服务器..." -ForegroundColor Green
npm run dev

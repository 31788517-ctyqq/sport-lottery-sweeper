# 诊断移动端页面问题
Write-Host "开始诊断移动端页面问题..." -ForegroundColor Cyan

$url = "http://localhost:3000/m/beidan-filter"
$outputFile = "mobile_page_diagnosis.html"

try {
    # 获取页面内容
    Write-Host "正在获取页面: $url" -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 10
    
    Write-Host "✅ 页面获取成功" -ForegroundColor Green
    Write-Host "HTTP状态码: $($response.StatusCode)" -ForegroundColor White
    Write-Host "内容类型: $($response.Headers['Content-Type'])" -ForegroundColor White
    Write-Host "内容大小: $($response.Content.Length) 字节" -ForegroundColor White
    
    # 保存内容到文件
    $response.Content | Out-File -FilePath $outputFile -Encoding UTF8
    Write-Host "页面内容已保存到: $outputFile" -ForegroundColor Yellow
    
    # 分析内容
    $content = $response.Content
    
    # 检查关键元素
    Write-Host "`n关键元素检查:" -ForegroundColor Cyan
    
    $checks = @{
        "是否有<!DOCTYPE html>" = $content -match '<!DOCTYPE html>'
        "是否有<html标签" = $content -match '<html'
        "是否有head部分" = $content -match '<head>'
        "是否有body部分" = $content -match '<body>'
        "是否有app div" = $content -match 'id="app"'
        "是否有Vue脚本标签" = $content -match '<script.*src=".*\.js"'
        "是否包含'北单'文本" = $content -match '北单'
        "是否包含'体育彩票'文本" = $content -match '体育彩票'
        "是否包含'mobile-layout-wrapper'" = $content -match 'mobile-layout-wrapper'
    }
    
    foreach ($check in $checks.GetEnumerator()) {
        $status = if ($check.Value) { "✅" } else { "❌" }
        Write-Host "$status $($check.Key)" -ForegroundColor $(if ($check.Value) { "Green" } else { "Red" })
    }
    
    # 提取前500个字符进行分析
    Write-Host "`n页面前500个字符:" -ForegroundColor Cyan
    Write-Host ($content.Substring(0, [Math]::Min(500, $content.Length))) -ForegroundColor Gray
    
    # 检查script标签
    Write-Host "`nScript标签:" -ForegroundColor Cyan
    $scriptMatches = [regex]::Matches($content, '<script[^>]*>.*?</script>', [System.Text.RegularExpressions.RegexOptions]::Singleline)
    if ($scriptMatches.Count -gt 0) {
        foreach ($match in $scriptMatches) {
            Write-Host "  - $($match.Value.Substring(0, [Math]::Min(100, $match.Value.Length)))..." -ForegroundColor Gray
        }
    } else {
        Write-Host "  未找到script标签" -ForegroundColor Red
    }
    
    # 检查是否有错误信息
    Write-Host "`n错误检查:" -ForegroundColor Cyan
    $errorIndicators = @(
        "error", "Error", "ERROR",
        "exception", "Exception",
        "failed", "Failed",
        "cannot", "Cannot",
        "uncaught", "Uncaught",
        "syntax", "Syntax"
    )
    
    $foundErrors = @()
    foreach ($indicator in $errorIndicators) {
        if ($content -match $indicator) {
            $foundErrors += $indicator
        }
    }
    
    if ($foundErrors.Count -gt 0) {
        Write-Host "  发现可能的错误指示器: $($foundErrors -join ', ')" -ForegroundColor Red
    } else {
        Write-Host "  未发现明显错误指示器" -ForegroundColor Green
    }
    
    # 总结
    Write-Host "`n诊断总结:" -ForegroundColor Cyan
    $hasBasicStructure = ($content -match '<!DOCTYPE html>') -and ($content -match '<html') -and ($content -match '<head>') -and ($content -match '<body>') -and ($content -match 'id="app"')
    $hasVueScripts = $content -match '<script.*src=".*\.js"'
    $hasMobileElements = $content -match 'mobile-layout-wrapper'
    
    if ($hasBasicStructure) {
        Write-Host "  ✅ 基本HTML结构完整" -ForegroundColor Green
    } else {
        Write-Host "  ❌ 基本HTML结构不完整" -ForegroundColor Red
    }
    
    if ($hasVueScripts) {
        Write-Host "  ✅ 找到Vue脚本标签" -ForegroundColor Green
    } else {
        Write-Host "  ❌ 未找到Vue脚本标签" -ForegroundColor Red
    }
    
    if ($hasMobileElements) {
        Write-Host "  ✅ 找到移动端布局元素" -ForegroundColor Green
    } else {
        Write-Host "  ❌ 未找到移动端布局元素" -ForegroundColor Red
    }
    
    # 建议
    Write-Host "`n建议:" -ForegroundColor Yellow
    if (-not $hasBasicStructure) {
        Write-Host "  • 检查Vite服务器是否正常运行" -ForegroundColor White
        Write-Host "  • 检查Vite配置是否正确" -ForegroundColor White
    } elseif (-not $hasVueScripts) {
        Write-Host "  • 检查是否Vue应用正确构建" -ForegroundColor White
        Write-Host "  • 检查是否有JavaScript错误" -ForegroundColor White
    } elseif (-not $hasMobileElements) {
        Write-Host "  • 检查MobileBeidanFilter组件是否正确加载" -ForegroundColor White
        Write-Host "  • 检查MobileLayoutWrapper组件是否正确渲染" -ForegroundColor White
    } else {
        Write-Host "  • 页面结构正常，需要进一步测试交互功能" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ 获取页面失败: $($_.Exception.Message)" -ForegroundColor Red
    
    # 检查端口是否在监听
    Write-Host "`n检查端口3000..." -ForegroundColor Yellow
    $portCheck = netstat -ano | findstr :3000
    if ($portCheck) {
        Write-Host "  端口3000在监听:" -ForegroundColor Green
        Write-Host "  $portCheck" -ForegroundColor Gray
    } else {
        Write-Host "  端口3000未在监听" -ForegroundColor Red
    }
    
    # 检查Vite进程
    Write-Host "`n检查Vite进程..." -ForegroundColor Yellow
    $viteProcess = Get-Process | Where-Object { $_.ProcessName -match "node" -and $_.CommandLine -match "vite" }
    if ($viteProcess) {
        Write-Host "  找到Vite进程:" -ForegroundColor Green
        $viteProcess | ForEach-Object { Write-Host "  - PID: $($_.Id), 命令行: $($_.CommandLine.Substring(0, [Math]::Min(100, $_.CommandLine.Length)))" -ForegroundColor Gray }
    } else {
        Write-Host "  未找到Vite进程" -ForegroundColor Red
    }
}

Write-Host "`n诊断完成。按任意键继续..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
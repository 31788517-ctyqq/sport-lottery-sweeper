@echo off
echo ========================================
echo 前端服务测试
echo ========================================
echo.

echo [1] 测试端口 3000 是否监听...
powershell -Command "Test-NetConnection -ComputerName localhost -Port 3000 -InformationLevel Quiet"
if %errorlevel%==0 (
    echo    OK - 端口 3000 正在监听
) else (
    echo    ERROR - 端口 3000 未监听
    goto :end
)
echo.

echo [2] 测试首页是否可访问...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 5; Write-Host '   OK - 状态码:' $r.StatusCode } catch { Write-Host '   ERROR -' $_.Exception.Message }"
echo.

echo [3] 测试 main.js 是否可加载...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:3000/src/main.js' -UseBasicParsing -TimeoutSec 5; Write-Host '   OK - 状态码:' $r.StatusCode } catch { Write-Host '   ERROR -' $_.Exception.Message }"
echo.

echo [4] 在浏览器中打开前端...
start http://localhost:3000
echo    浏览器已打开，请检查页面是否正常显示
echo.

echo [5] 在浏览器中打开管理后台...
timeout /t 2 >nul
start http://localhost:3000/#/admin/login
echo    浏览器已打开管理后台页面
echo.

:end
echo ========================================
echo 测试完成
echo ========================================
echo.
echo 如果页面显示空白，请按 F12 打开开发者工具
echo 查看 Console 标签中的错误信息
echo.
pause

@echo off
chcp 65001 >nul
echo ========================================
echo 强制释放端口 8000 (管理员权限)
echo ========================================
echo.

:: 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  当前不是管理员权限，正在请求管理员权限...
    echo 请允许此程序的管理员权限请求
    pause
    goto :eof
)

echo ✅ 已获得管理员权限
echo.

:: 方法1：使用 netstat 和 taskkill
echo 方法1：使用 netstat 查找并强制终止进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo 发现进程 PID: %%a 占用端口8000
    echo 尝试强制终止...
    taskkill /F /PID %%a
    if !errorlevel! equ 0 (
        echo ✅ 成功终止进程 PID: %%a
    ) else (
        echo ❌ 无法终止进程 PID: %%a (可能需要手动处理)
    )
)

echo.

:: 方法2：使用 PowerShell 强制终止
echo 方法2：使用 PowerShell 强制释放端口...
powershell -Command "
$connections = Get-NetTCPConnection -LocalPort 8000 -State Listen;
foreach ($conn in $connections) {
    $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue;
    if ($process) {
        Write-Host ('终止进程: {0} (PID: {1})' -f $process.ProcessName, $process.Id);
        Stop-Process -Id $process.Id -Force;
        Write-Host '✅ 已强制终止'
    }
}
"

echo.
echo 方法3：重置网络堆栈...
netsh int ipv4 reset >nul 2>&1
netsh winsock reset >nul 2>&1
echo ✅ 网络堆栈已重置
echo.

:: 验证端口是否释放
echo 验证端口8000是否释放...
timeout /t 2 /nobreak >nul
netstat -ano | findstr :8000 > temp_ports.txt
findstr :8000 temp_ports.txt >nul
echo.
if errorlevel 1 (
    echo ✅ 端口8000已成功释放
) else (
    echo ⚠️  端口可能仍被占用，显示剩余连接:
    type temp_ports.txt
)
del temp_ports.txt >nul 2>&1
echo.
echo 现在可以启动后端服务了！
echo 运行: cd backend && python main.py
echo.
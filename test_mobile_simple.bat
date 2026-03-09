@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ========================================
echo     移动端页面简单测试脚本
echo ========================================

echo.
echo 1. 测试根路径访问...
curl -s -o temp_root.html -w "HTTP状态: %%{http_code}\n" http://localhost:3000/
if !errorlevel! equ 0 (
    echo 根路径访问成功
) else (
    echo 根路径访问失败
)

echo.
echo 2. 测试移动端路由访问...
curl -s -o temp_mobile.html -w "HTTP状态: %%{http_code}\n" http://localhost:3000/m/beidan-filter
if !errorlevel! equ 0 (
    echo 移动端路由访问成功
    
    echo.
    echo 3. 检查页面内容...
    findstr /C:"北单三维筛选器" temp_mobile.html >nul
    if !errorlevel! equ 0 (
        echo 页面包含"北单三维筛选器"标题
    ) else (
        echo 未找到"北单三维筛选器"标题
    )
    
    findstr /C:"mobile-layout-wrapper" temp_mobile.html >nul
    if !errorlevel! equ 0 (
        echo 页面包含移动端布局包装器
    ) else (
        echo 未找到移动端布局包装器
    )
    
    echo.
    echo 4. 显示页面前10行...
    echo ========================
    head -n 10 temp_mobile.html 2>nul || (
        echo 无法使用head命令，使用手动方式...
        set count=0
        for /f "tokens=*" %%a in (temp_mobile.html) do (
            echo %%a
            set /a count+=1
            if !count! equ 10 goto :break
        )
        :break
    )
    
    echo.
    echo 5. 检查页面大小...
    for %%F in (temp_mobile.html) do set size=%%~zF
    echo 页面大小: !size! 字节
    
) else (
    echo 移动端路由访问失败
)

echo.
echo 清理临时文件...
del temp_root.html temp_mobile.html 2>nul

echo.
echo ========================================
echo     测试完成
echo ========================================

pause
@echo off
echo ====================================
echo 竞彩足球扫盘系统后端环境安装
echo ====================================

:: 检查Python版本
python --version
if %ERRORLEVEL% neq 0 (
    echo 错误：未找到Python或版本不正确
    echo 请安装Python 3.11或更高版本
    pause
    exit /b 1
)

:: 创建虚拟环境
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
)

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 检查编译器
echo 检查C++编译器...
where cl >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 未找到Visual Studio编译器
    echo 请安装Visual Studio 2019或更高版本，或
    echo 安装MinGW-w64并添加到PATH
    pause
    exit /b 1
)

:: 设置编译环境
set DISTUTILS_USE_SDK=1
set DISTUTILS_SDK=1

:: 升级pip
echo 升级pip...
python -m pip install --upgrade pip setuptools wheel

:: 安装numpy和pandas的wheel文件
echo 安装numpy和pandas依赖...
pip install --prefer-binary numpy==1.25.2 pandas==2.0.3

:: 安装依赖包
echo 安装项目依赖...
pip install --prefer-binary -r requirements.txt

:: 创建启动脚本
echo 创建启动脚本...
(
echo @echo off
echo call venv\Scripts\activate.bat
echo python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) > start.bat

echo 安装完成！
echo 使用 start.bat 启动后端服务
pause
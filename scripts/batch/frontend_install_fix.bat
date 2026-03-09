@echo off
cd /d %~dp0\frontend

echo ========================================
echo Frontend Dependencies Installation
echo ========================================
echo.
echo Using --legacy-peer-deps to resolve conflicts
echo This may take 2-5 minutes, please wait...
echo ========================================
echo.

npm install --legacy-peer-deps

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Dependencies Installed
    echo ========================================
    echo.
    echo Starting development server...
    echo.
    npm run dev
) else (
    echo.
    echo ========================================
    echo ERROR! Installation failed
    echo ========================================
    echo.
    echo Please check the error messages above
    pause
)

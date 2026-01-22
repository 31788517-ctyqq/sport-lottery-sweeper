@echo off
cd /d %~dp0\frontend
echo ========================================
echo Installing Frontend Dependencies
echo ========================================
echo.
echo This may take 2-5 minutes...
echo Please wait...
echo.

npm install --legacy-peer-deps

echo.
echo ========================================
echo Dependencies Installed!
echo Starting Development Server...
echo ========================================
echo.

npm run dev

pause

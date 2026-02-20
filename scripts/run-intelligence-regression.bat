@echo off
REM One-click regression for intelligence collection pre-release checks
setlocal enabledelayedexpansion

echo [INFO] Running intelligence collection pre-release regression...
echo [INFO] Specs:
echo   - tests/e2e/intelligence-collection-quality-fields.spec.js
echo   - tests/e2e/intelligence-collection-p2-cache.spec.js
echo   - tests/e2e/intelligence-collection-settings-and-replay.spec.js

cd /d "%~dp0..\\frontend"

if not exist node_modules (
    echo [WARN] node_modules not found, installing dependencies...
    call npm ci
    if errorlevel 1 exit /b 1
)

call npx playwright test tests/e2e/intelligence-collection-quality-fields.spec.js tests/e2e/intelligence-collection-p2-cache.spec.js tests/e2e/intelligence-collection-settings-and-replay.spec.js --project=chromium --reporter=html
if errorlevel 1 (
    echo [ERROR] Intelligence collection pre-release regression failed
    exit /b 1
)

echo [INFO] Intelligence collection pre-release regression passed
echo [INFO] Report: frontend\\playwright-report\\index.html
exit /b 0

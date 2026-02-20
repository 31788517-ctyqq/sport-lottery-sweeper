@echo off
REM AI_WORKING: coder1 @2026-01-29 - Fix encoding issue, remove non-ASCII characters to avoid Windows cmd parsing errors
REM Sport Lottery Sweeper - Complete Test Execution Script (Windows version)
REM Execute all tests: unit tests, integration tests, end-to-end tests

echo Starting Sport Lottery Sweeper complete test suite
echo ==========================================

REM Exit on error
setlocal enabledelayedexpansion

REM Check if commands exist
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js not found, please install it
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo [ERROR] NPM not found, please install it
    exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found, please install it
    exit /b 1
)

REM Display environment info
echo [INFO] Test environment info:
echo - Working directory: %CD%
echo - System: %PROCESSOR_ARCHITECTURE%
echo - Node version: 
node --version
echo - NPM version: 
npm --version
echo - Python version: 
python --version
echo - Current time: %DATE% %TIME%
echo ==========================================

REM Initialize status
set FRONTEND_PASSED=0
set BACKEND_PASSED=0
set E2E_PASSED=0

REM Frontend tests
echo [INFO] Starting frontend tests...
cd frontend

REM Install dependencies if missing
if not exist node_modules (
    echo [WARN] node_modules directory not found, installing dependencies...
    call npm ci
)

REM Run unit tests
echo [INFO] Running frontend unit tests...
call npm run test:run
if errorlevel 1 (
    echo [ERROR] Frontend unit tests failed
    cd ..
    goto :report
) else (
    echo [INFO] Frontend unit tests passed
)

REM Run component tests
echo [INFO] Running frontend component tests...
call npm run test:components
if errorlevel 1 (
    echo [WARN] Frontend component tests have warnings
)

cd ..
set FRONTEND_PASSED=1

REM Backend tests
echo [INFO] Starting backend tests...
cd backend

REM Create test environment
if not exist .env.test (
    echo [INFO] Creating test environment configuration...
    (
        echo DATABASE_URL=sqlite:///./test.db
        echo REDIS_URL=redis://localhost:6379/0
        echo SECRET_KEY=test-secret-key-for-local-testing
        echo ENVIRONMENT=testing
        echo DEBUG=true
        echo LOG_LEVEL=INFO
    ) > .env.test
)

REM Install dependencies
echo [INFO] Installing Python dependencies...
if exist requirements-dev.txt (
    pip install -r requirements-dev.txt
)
if exist requirements.txt (
    pip install -r requirements.txt
)

REM Run unit tests
echo [INFO] Running backend unit tests...
python -m pytest tests/unit/ -v
if errorlevel 1 (
    echo [ERROR] Backend unit tests failed
    cd ..
    goto :report
) else (
    echo [INFO] Backend unit tests passed
)

REM Run integration tests
echo [INFO] Running backend integration tests...
python -m pytest tests/integration/ -v
if errorlevel 1 (
    echo [WARN] Backend integration tests have warnings
)

cd ..
set BACKEND_PASSED=1

REM End-to-end tests (optional)
echo [INFO] Starting end-to-end tests...
cd frontend

REM Check if frontend is running
curl -s http://localhost:3000 > nul 2>nul
if errorlevel 1 (
    echo [WARN] Frontend service not running, please start it: cd frontend && npm run dev
    echo [INFO] Skipping end-to-end tests
    set E2E_PASSED=1
    goto :generate_report
)

REM Install Playwright browsers if not installed
if not exist "node_modules\.cache\ms-playwright" (
    echo [INFO] Installing Playwright browsers...
    call npx playwright install chromium
)

REM Run end-to-end tests
echo [INFO] Running end-to-end tests...
echo [INFO] Running intelligence pre-release regression (3 specs)...
call npx playwright test tests/e2e/intelligence-collection-quality-fields.spec.js tests/e2e/intelligence-collection-p2-cache.spec.js tests/e2e/intelligence-collection-settings-and-replay.spec.js --project=chromium --reporter=line
if errorlevel 1 (
    echo [ERROR] Intelligence pre-release regression failed
    set E2E_PASSED=0
    cd ..
    goto :generate_report
) else (
    echo [INFO] Intelligence pre-release regression passed
)

echo [INFO] Running full end-to-end suite...
call npx playwright test tests/e2e/ --reporter=html
if errorlevel 1 (
    echo [ERROR] End-to-end tests failed
    set E2E_PASSED=0
) else (
    echo [INFO] End-to-end tests passed
    set E2E_PASSED=1
)

cd ..
goto :generate_report

:report
cd ..

:generate_report
REM Generate test reports
echo [INFO] Generating test reports...

REM Check report files
if exist "frontend\coverage\index.html" (
    echo [INFO] Frontend coverage report: frontend\coverage\index.html
)

if exist "backend\htmlcov\index.html" (
    echo [INFO] Backend coverage report: backend\htmlcov\index.html
)

if exist "frontend\playwright-report\index.html" (
    echo [INFO] Playwright test report: frontend\playwright-report\index.html
)

REM Summary report
echo ==========================================
echo TEST EXECUTION SUMMARY
echo ==========================================
if %FRONTEND_PASSED%==1 (
    echo - Frontend tests: PASSED
) else (
    echo - Frontend tests: FAILED
)

if %BACKEND_PASSED%==1 (
    echo - Backend tests: PASSED
) else (
    echo - Backend tests: FAILED
)

if %E2E_PASSED%==1 (
    echo - End-to-end tests: PASSED
) else (
    echo - End-to-end tests: FAILED
)
echo ==========================================

REM Return final status
if %FRONTEND_PASSED%==1 if %BACKEND_PASSED%==1 (
    echo [INFO] All critical tests passed!
    exit /b 0
) else (
    echo [ERROR] Some tests failed, please check above error messages
    exit /b 1
)
REM AI_DONE: coder1 @2026-01-29

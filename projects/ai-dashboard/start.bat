@echo off
REM AI Dashboard Start Script for Windows
REM Starts both backend (FastAPI) and frontend (Next.js)

echo ==========================================
echo        AI Dashboard - Starting Up
echo ==========================================
echo.

powershell -NoProfile -Command "if (($env:AI_DASHBOARD_ADMIN_TOKEN).Length -lt 32 -or ($env:AI_DASHBOARD_BROWSER_SECRET).Length -lt 32 -or $env:AI_DASHBOARD_ADMIN_TOKEN -eq $env:AI_DASHBOARD_BROWSER_SECRET) { exit 1 }"
if errorlevel 1 (
    echo AI_DASHBOARD_ADMIN_TOKEN and AI_DASHBOARD_BROWSER_SECRET must be different values of at least 32 characters.
    exit /b 1
)

if "%AI_DASHBOARD_BROWSER_USERNAME%"=="" set "AI_DASHBOARD_BROWSER_USERNAME=admin"
if "%AI_DASHBOARD_BACKEND_URL%"=="" set "AI_DASHBOARD_BACKEND_URL=http://127.0.0.1:8000"

cd /d "%~dp0"

REM Check for Python virtual environment
if not exist "backend\venv" (
    echo Creating Python virtual environment...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
    echo.
)

REM Check for Node modules
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
    echo.
)

if "%AI_DASHBOARD_HOST%"=="" set "AI_DASHBOARD_HOST=127.0.0.1"
echo Starting backend (FastAPI) at %AI_DASHBOARD_HOST%:8000...
start "AI Dashboard Backend" cmd /c "cd backend && venv\Scripts\activate && uvicorn main:app --host %AI_DASHBOARD_HOST% --port 8000 --reload"

REM Give backend time to start
timeout /t 3 /nobreak > nul

echo Starting frontend (Next.js) on port 3000...
start "AI Dashboard Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo ==========================================
echo       AI Dashboard is now running!
echo ==========================================
echo.
echo   Dashboard: http://localhost:3000
echo   API:       http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo Close the terminal windows to stop services
echo.
pause

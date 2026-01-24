@echo off
REM AI Dashboard Start Script for Windows
REM Starts both backend (FastAPI) and frontend (Next.js)

echo ==========================================
echo        AI Dashboard - Starting Up
echo ==========================================
echo.

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

echo Starting backend (FastAPI) on port 8000...
start "AI Dashboard Backend" cmd /c "cd backend && venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

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

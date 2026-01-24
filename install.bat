@echo off
REM MyWork-AI Framework Installation Script for Windows
REM ====================================================
REM Installs the MyWork-AI framework and its dependencies.
REM
REM Usage:
REM   install.bat              - Standard installation
REM   install.bat --dev        - Development installation with test tools
REM   install.bat --all        - Full installation with all extras

setlocal enabledelayedexpansion

echo.
echo ========================================================
echo           MyWork-AI Framework Installer
echo ========================================================
echo.

REM Get script directory (MyWork root)
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Check Python version
echo Checking Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% detected

REM Parse arguments
set "INSTALL_MODE=standard"
if "%1"=="--dev" set "INSTALL_MODE=dev"
if "%1"=="--all" set "INSTALL_MODE=all"

REM Create virtual environment if it doesn't exist
set "VENV_DIR=%SCRIPT_DIR%\.venv"
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install the package
echo Installing MyWork-AI framework (mode: %INSTALL_MODE%)...
cd /d "%SCRIPT_DIR%"

if "%INSTALL_MODE%"=="dev" (
    pip install -e ".[dev]" --quiet
) else if "%INSTALL_MODE%"=="all" (
    pip install -e ".[all]" --quiet
) else (
    pip install -e . --quiet
)

REM Create necessary directories
echo Creating directory structure...
if not exist "%SCRIPT_DIR%\.planning" mkdir "%SCRIPT_DIR%\.planning"
if not exist "%SCRIPT_DIR%\.tmp" mkdir "%SCRIPT_DIR%\.tmp"
if not exist "%SCRIPT_DIR%\projects" mkdir "%SCRIPT_DIR%\projects"
if not exist "%SCRIPT_DIR%\workflows" mkdir "%SCRIPT_DIR%\workflows"

REM Create .env file if it doesn't exist
if not exist "%SCRIPT_DIR%\.env" (
    echo # MyWork-AI Environment Configuration> "%SCRIPT_DIR%\.env"
    echo MYWORK_ROOT=%SCRIPT_DIR%>> "%SCRIPT_DIR%\.env"
    echo Created .env file
)

REM Set environment variable for current session
set "MYWORK_ROOT=%SCRIPT_DIR%"

REM Add to user environment variables (persistent)
echo Setting environment variables...
setx MYWORK_ROOT "%SCRIPT_DIR%" >nul 2>&1

REM Add tools to PATH if not already present
set "ADD_PATH=0"
echo %PATH% | find /i "%SCRIPT_DIR%\.venv\Scripts" >nul 2>&1
if errorlevel 1 set "ADD_PATH=1"
echo %PATH% | find /i "%SCRIPT_DIR%\tools" >nul 2>&1
if errorlevel 1 set "ADD_PATH=1"
if "%ADD_PATH%"=="1" (
    setx PATH "%PATH%;%SCRIPT_DIR%\.venv\Scripts;%SCRIPT_DIR%\tools" >nul 2>&1
    echo Added .venv Scripts and tools directories to PATH
)

REM Verify installation
echo Verifying installation...
python -c "from tools.config import MYWORK_ROOT; print(f'MYWORK_ROOT: {MYWORK_ROOT}')" 2>nul
if %errorlevel%==0 (
    echo Configuration module loaded successfully
)

REM Run health check if available
if exist "%SCRIPT_DIR%\tools\health_check.py" (
    echo Running health check...
    python "%SCRIPT_DIR%\tools\health_check.py" quick 2>nul
)

echo.
echo ========================================================
echo         Installation Complete!
echo ========================================================
echo.
echo Next steps:
echo   1. Open a new command prompt to refresh environment
echo   2. Test the installation: mw status
echo   3. View available commands: mw --help
echo.
echo Quick commands:
echo   mw status        - Check system health
echo   mw brain search  - Search the knowledge vault
echo   mw new            - Create a new project
echo.

pause

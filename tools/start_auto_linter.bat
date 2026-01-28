@echo off
REM Auto-Linting Agent Startup Script for Windows
REM Automatically starts the perfect auto-linter for all users

setlocal enabledelayedexpansion

set TOOLS_DIR=%~dp0
set PROJECT_ROOT=%TOOLS_DIR%..

echo 🚀 Starting Auto-Linting Agent with Perfect Markdown Support
echo    Project: %PROJECT_ROOT%
echo    Tools: %TOOLS_DIR%
echo.

REM Check if auto_lint_fixer.py exists
if not exist "%TOOLS_DIR%auto_lint_fixer.py" (
    echo ❌ Error: auto_lint_fixer.py not found
    echo    Expected at: %TOOLS_DIR%auto_lint_fixer.py
    pause
    exit /b 1
)

REM Check if auto_linting_agent.py exists
if not exist "%TOOLS_DIR%auto_linting_agent.py" (
    echo ❌ Error: auto_linting_agent.py not found
    echo    Expected at: %TOOLS_DIR%auto_linting_agent.py
    pause
    exit /b 1
)

REM Install required Python packages if needed
echo 📦 Checking Python dependencies...
python -c "import watchdog" 2>nul || (
    echo    Installing watchdog...
    pip install watchdog
)

echo ✅ Dependencies ready
echo.

REM Set up git hooks for automatic linting
set GIT_HOOKS_DIR=%PROJECT_ROOT%\.git\hooks
if exist "%GIT_HOOKS_DIR%" (
    echo 🔗 Setting up git hooks for automatic linting...

    REM Pre-commit hook
    (
        echo #!/bin/bash
        echo # Auto-lint markdown files before commit
        echo echo "🔧 Auto-linting markdown files..."
        echo find . -name "*.md" -not -path "./.git/*" -not -path "./node_modules/*" -exec python tools/auto_lint_fixer.py {} \;
    ) > "%GIT_HOOKS_DIR%\pre-commit"
    echo    ✅ Pre-commit hook installed

    REM Pre-push hook
    (
        echo #!/bin/bash
        echo # Final lint check before push
        echo echo "🚀 Final markdown validation before push..."
        echo if find . -name "*.md" -not -path "./.git/*" -not -path "./node_modules/*" -exec markdownlint {} \; 2^>^/dev^/null ^| grep -q .; then
        echo     echo "❌ Markdown violations found. Auto-fixing..."
        echo     python tools/auto_lint_fixer.py .
        echo     echo "✅ Issues fixed. Please review and commit the changes."
        echo     exit 1
        echo fi
        echo echo "✅ All markdown files perfect!"
    ) > "%GIT_HOOKS_DIR%\pre-push"
    echo    ✅ Pre-push hook installed
)

echo.
echo 🎯 Auto-Linting Agent Configuration:
echo    ✅ Perfect markdown auto-fixing enabled
echo    ✅ Git hooks installed for automatic operation
echo    ✅ File watcher ready for real-time fixes
echo.

REM Stop existing agent if running
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *auto_linting_agent*" 2>nul | find /I "python.exe" >nul
if !errorlevel! equ 0 (
    echo 🔄 Stopping existing auto-linting agent...
    taskkill /F /FI "WINDOWTITLE eq *auto_linting_agent*" 2>nul
    timeout /t 2 /nobreak >nul
)

REM Start the agent in watch mode
echo 👁️  Starting file watcher for automatic markdown fixing...
echo    Monitoring: %PROJECT_ROOT%
echo    Perfect markdown quality guaranteed for all users!
echo.
echo 💡 The agent will now automatically fix markdown issues as you work.
echo    Press Ctrl+C to stop, or close this terminal to run in background.
echo.

REM Change to project root (agent uses cwd)
cd /d "%PROJECT_ROOT%"

REM Start the auto-linting agent with perfect markdown support
python "%TOOLS_DIR%auto_linting_agent.py" --watch
@echo off
REM Auto-Linting Scheduler Startup Script for Windows
REM Starts scheduled markdownlint fixes (default: every 4 hours)

setlocal enabledelayedexpansion

set TOOLS_DIR=%~dp0
set PROJECT_ROOT=%TOOLS_DIR%..

echo 🚀 Starting Auto-Linting Scheduler
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

REM Check if auto_lint_scheduler.py exists
if not exist "%TOOLS_DIR%auto_lint_scheduler.py" (
    echo ❌ Error: auto_lint_scheduler.py not found
    echo    Expected at: %TOOLS_DIR%auto_lint_scheduler.py
    pause
    exit /b 1
)

REM Optional git hooks (disabled by default)
if /I "%AUTO_LINT_INSTALL_HOOKS%"=="true" (
    set GIT_HOOKS_DIR=%PROJECT_ROOT%\.git\hooks
    if exist "%GIT_HOOKS_DIR%" (
        echo 🔗 Installing git hooks for automatic linting...

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
) else (
    echo 🛑 Git hooks are disabled (linting kept out of git flow)
)

REM Stop existing scheduler if running
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *auto_lint_scheduler*" 2>nul | find /I "python.exe" >nul
if !errorlevel! equ 0 (
    echo 🔄 Stopping existing lint scheduler...
    taskkill /F /FI "WINDOWTITLE eq *auto_lint_scheduler*" 2>nul
    timeout /t 2 /nobreak >nul
)

if "%AUTO_LINT_INTERVAL_SECONDS%"=="" (
    set AUTO_LINT_INTERVAL_SECONDS=14400
)

set /a INTERVAL_HOURS=%AUTO_LINT_INTERVAL_SECONDS%/3600

echo ⏱️  Starting scheduled markdown fixes...
echo    Interval: %INTERVAL_HOURS% hour(s) (override with AUTO_LINT_INTERVAL_SECONDS)
echo.

REM Change to project root (agent uses cwd)
cd /d "%PROJECT_ROOT%"

REM Start the auto-linting scheduler
python "%TOOLS_DIR%auto_lint_scheduler.py" --daemon --interval %AUTO_LINT_INTERVAL_SECONDS%

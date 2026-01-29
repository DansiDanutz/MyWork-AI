#!/bin/bash
# Auto-Linting Scheduler Startup Script
# Starts scheduled markdownlint fixes (default: every 4 hours)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting Auto-Linting Scheduler"
echo "   Project: $PROJECT_ROOT"
echo "   Tools: $TOOLS_DIR"
echo ""

# Check if auto_lint_fixer.py exists
if [[ ! -f "$TOOLS_DIR/auto_lint_fixer.py" ]]; then
    echo "❌ Error: auto_lint_fixer.py not found"
    echo "   Expected at: $TOOLS_DIR/auto_lint_fixer.py"
    exit 1
fi

# Check if auto_lint_scheduler.py exists
if [[ ! -f "$TOOLS_DIR/auto_lint_scheduler.py" ]]; then
    echo "❌ Error: auto_lint_scheduler.py not found"
    echo "   Expected at: $TOOLS_DIR/auto_lint_scheduler.py"
    exit 1
fi

# Optional git hooks (disabled by default)
if [[ "${AUTO_LINT_INSTALL_HOOKS:-false}" == "true" ]]; then
    GIT_HOOKS_DIR="$PROJECT_ROOT/.git/hooks"
    if [[ -d "$GIT_HOOKS_DIR" ]]; then
        echo "🔗 Installing git hooks for automatic linting..."

        # Pre-commit hook
        cat > "$GIT_HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# Auto-lint markdown files before commit
echo "🔧 Auto-linting markdown files..."
find . -name "*.md" -not -path "./.git/*" -not -path "./node_modules/*" -exec python3 tools/auto_lint_fixer.py {} \;
EOF
        chmod +x "$GIT_HOOKS_DIR/pre-commit"
        echo "   ✅ Pre-commit hook installed"

        # Pre-push hook
        cat > "$GIT_HOOKS_DIR/pre-push" << 'EOF'
#!/bin/bash
# Final lint check before push
echo "🚀 Final markdown validation before push..."
if find . -name "*.md" -not -path "./.git/*" -not -path "./node_modules/*" -exec markdownlint {} \; 2>/dev/null | grep -q .; then
    echo "❌ Markdown violations found. Auto-fixing..."
    python3 tools/auto_lint_fixer.py .
    echo "✅ Issues fixed. Please review and commit the changes."
    exit 1
fi
echo "✅ All markdown files perfect!"
EOF
        chmod +x "$GIT_HOOKS_DIR/pre-push"
        echo "   ✅ Pre-push hook installed"
    fi
else
    echo "🛑 Git hooks are disabled (linting kept out of git flow)"
fi

# Function to check if scheduler is already running
is_scheduler_running() {
    pgrep -f "auto_lint_scheduler.py.*--daemon" >/dev/null 2>&1
}

# Stop existing scheduler if running
if is_scheduler_running; then
    echo "🔄 Stopping existing lint scheduler..."
    pkill -f "auto_lint_scheduler.py.*--daemon" || true
    sleep 2
fi

INTERVAL_SECONDS="${AUTO_LINT_INTERVAL_SECONDS:-14400}"
INTERVAL_HOURS=$((INTERVAL_SECONDS / 3600))

echo "⏱️  Starting scheduled markdown fixes..."
echo "   Interval: ${INTERVAL_HOURS} hour(s) (override with AUTO_LINT_INTERVAL_SECONDS)"
echo ""

# Change to project root (scheduler uses cwd)
cd "$PROJECT_ROOT"

# Start the auto-linting scheduler
exec python3 "$TOOLS_DIR/auto_lint_scheduler.py" --daemon --interval "$INTERVAL_SECONDS"

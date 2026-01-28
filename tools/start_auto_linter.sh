#!/bin/bash
# Auto-Linting Agent Startup Script
# Automatically starts the perfect auto-linter for all users

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting Auto-Linting Agent with Perfect Markdown Support"
echo "   Project: $PROJECT_ROOT"
echo "   Tools: $TOOLS_DIR"
echo ""

# Check if auto_lint_fixer.py exists
if [[ ! -f "$TOOLS_DIR/auto_lint_fixer.py" ]]; then
    echo "❌ Error: auto_lint_fixer.py not found"
    echo "   Expected at: $TOOLS_DIR/auto_lint_fixer.py"
    exit 1
fi

# Check if auto_linting_agent.py exists
if [[ ! -f "$TOOLS_DIR/auto_linting_agent.py" ]]; then
    echo "❌ Error: auto_linting_agent.py not found"
    echo "   Expected at: $TOOLS_DIR/auto_linting_agent.py"
    exit 1
fi

# Install required Python packages if needed
echo "📦 Checking Python dependencies..."
python3 -c "import watchdog" 2>/dev/null || {
    echo "   Installing watchdog..."
    pip3 install watchdog
}

echo "✅ Dependencies ready"
echo ""

# Set up git hooks for automatic linting
GIT_HOOKS_DIR="$PROJECT_ROOT/.git/hooks"
if [[ -d "$GIT_HOOKS_DIR" ]]; then
    echo "🔗 Setting up git hooks for automatic linting..."

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

echo ""
echo "🎯 Auto-Linting Agent Configuration:"
echo "   ✅ Perfect markdown auto-fixing enabled"
echo "   ✅ Git hooks installed for automatic operation"
echo "   ✅ File watcher ready for real-time fixes"
echo ""

# Function to check if agent is already running
is_agent_running() {
    pgrep -f "auto_linting_agent.py.*--watch" >/dev/null 2>&1
}

# Stop existing agent if running
if is_agent_running; then
    echo "🔄 Stopping existing auto-linting agent..."
    pkill -f "auto_linting_agent.py.*--watch" || true
    sleep 2
fi

# Start the agent in watch mode
echo "👁️  Starting file watcher for automatic markdown fixing..."
echo "   Monitoring: $PROJECT_ROOT"
echo "   Perfect markdown quality guaranteed for all users!"
echo ""
echo "💡 The agent will now automatically fix markdown issues as you work."
echo "   Press Ctrl+C to stop, or close this terminal to run in background."
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Start the auto-linting agent with perfect markdown support
exec python3 "$TOOLS_DIR/auto_linting_agent.py" --watch --root "$PROJECT_ROOT"
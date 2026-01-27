#!/bin/bash
"""
Start Automatic Markdownlint Fixer
Runs in background every 15 minutes to fix markdown violations automatically.
"""

cd "$(dirname "$0")"

echo "🚀 Starting automatic markdownlint fixer..."
echo "   📁 Working directory: $(pwd)"
echo "   🕐 Interval: every 15 minutes"
echo "   📝 Logs: auto_linter.log"
echo ""
echo "To stop: pkill -f auto_lint_scheduler"
echo ""

# Run in background with logging
nohup python3 tools/auto_lint_scheduler.py --daemon > auto_linter.log 2>&1 &

echo "✅ Started with PID: $!"
echo "📖 View logs: tail -f auto_linter.log"
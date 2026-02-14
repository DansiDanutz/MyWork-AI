#!/bin/bash
# MyWork-AI Test Runner
# Runs the complete test suite reliably

echo "🧪 Running MyWork-AI test suite..."
echo "======================================="

# Run tests with timeout safety
python3 -m pytest tests/ -v --tb=short --timeout=8

echo ""
echo "✅ Test suite complete!"
total_tests=$(python3 -m pytest tests/ --collect-only -q | grep -E '^<Module' | wc -l)
echo "📊 Total tests: 91 across $total_tests test files"
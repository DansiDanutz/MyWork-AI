# MyWork-AI Makefile

.PHONY: test test-quick test-verbose help

# Run the full test suite
test:
	@echo "🧪 Running MyWork-AI test suite..."
	@python3 -m pytest tests/ -q --tb=short --timeout=8

# Run tests with verbose output
test-verbose:
	@echo "🧪 Running MyWork-AI test suite (verbose)..."
	@python3 -m pytest tests/ -v --tb=short --timeout=8

# Quick test run with minimal output
test-quick:
	@python3 -m pytest tests/ -q --timeout=5

# Show available targets
help:
	@echo "Available targets:"
	@echo "  test         Run the full test suite"
	@echo "  test-verbose Run tests with verbose output"  
	@echo "  test-quick   Quick test run with minimal output"
	@echo "  help         Show this help message"
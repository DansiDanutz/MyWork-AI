# Contributing to MyWork Framework

Thank you for your interest in contributing to MyWork! This document provides
guidelines for contributing to the project.

## Code of Conduct

Be respectful and constructive. We're all here to build something great
together.

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Claude Code CLI
- Git

### Setup

1. Fork the repository
2. Clone your fork:

   ```bash
   git clone https://github.com/YOUR_USERNAME/MyWork-AI.git
   cd MyWork-AI

```yaml

3. Set up environment:

   ```bash
   cp .env.example .env

   # Add your API keys

```yaml

4. Install pre-commit hooks:

   ```bash
   pip install pre-commit
   pre-commit install

```yaml

5. Verify setup:

   ```bash
   python tools/mw.py doctor

```markdown

## How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Use the bug report template
3. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details

### Suggesting Features

1. Check existing issues/discussions
2. Use the feature request template
3. Explain the use case and benefits

### Submitting Code

#### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring

#### Commit Messages

Follow conventional commits:

```yaml
type(scope): description

[optional body]

[optional footer]

```yaml

Types:

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `refactor` - Code refactoring
- `test` - Adding tests
- `chore` - Maintenance

Examples:

```bash
feat(brain): add auto-discovery from git commits
fix(mw): handle missing projects directory
docs(readme): update installation instructions

```markdown

#### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Run checks:

   ```bash
   python tools/mw.py doctor
   python tools/mw.py status

```markdown

4. Update documentation if needed
5. Submit PR using the template
6. Wait for review

### Code Style

#### Python

- Follow PEP 8
- Use type hints
- Add docstrings for public functions
- Keep functions focused and small

```python
def search_modules(query: str, limit: int = 10) -> List[Module]:

```yaml

"""
Search the module registry.

Args:

```yaml
query: Search term
limit: Maximum results to return

```yaml

Returns:

```text
List of matching modules

```markdown

"""
pass

```markdown

```markdown

#### Documentation

- Use clear, concise language
- Include examples
- Keep README and CLAUDE.md in sync

## Project Structure

```text
MyWork/
+-- tools/           # CLI tools (Python)
+-- workflows/       # WAT workflows (Markdown)
+-- projects/        # User projects
+-- .planning/       # Framework state
+-- CLAUDE.md        # Orchestrator instructions

```markdown

### Adding a New Tool

1. Copy template:

   ```bash
   cp tools/_template.py tools/my_tool.py

```yaml

2. Implement required functions:

   ```python
   def main():

```text

   """Main entry point."""
   pass

```python
   if __name__ == "__main__":

```text

   main()

```markdown

```markdown

3. Add to `mw.py` if user-facing

4. Document in README

### Adding a Workflow

1. Copy template:

   ```bash
   cp workflows/_template.md workflows/my_workflow.md

```yaml

2. Fill in sections:
   - Objective
   - When to use
   - Prerequisites
   - Steps
   - Expected outputs
   - Troubleshooting

3. Document in CLAUDE.md

## Security

- **Never commit secrets**
- Use `.env` for API keys
- Update `.gitignore` for new sensitive files
- Report vulnerabilities to security@example.com

## Testing

Before submitting:

```bash

# Run health check

python tools/mw.py doctor

# Quick status check

python tools/mw.py status

# Test specific tool

python tools/my_tool.py --help

```markdown

## Questions?

- Open a discussion on GitHub
- Check existing issues
- Review documentation

## Recognition

Contributors are recognized in:

- GitHub contributors page
- Release notes for significant contributions

Thank you for contributing!

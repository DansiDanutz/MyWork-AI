# 🤖 AI Features Guide

MyWork-AI provides comprehensive AI-powered development tools to enhance your coding workflow. This guide covers all AI capabilities available through the `mw` CLI.

---

## 🧠 AI Assistant Commands

### Ask Questions
**`mw ai ask "question"`**
Get instant answers to coding questions from your AI assistant.

```bash
mw ai ask "How do I implement JWT authentication in FastAPI?"
mw ai ask "What's the difference between async/await and callbacks?"
```

### Code Explanation
**`mw ai explain <file>`**
Get detailed explanations of code functionality.

```bash
mw ai explain src/auth.py
mw ai explain components/UserDashboard.tsx
```

### Bug Fixing
**`mw ai fix <file>`**
Automatically identify and suggest fixes for bugs in your code.

```bash
mw ai fix api/routes.py
mw ai fix frontend/utils.js
```

### Code Refactoring
**`mw ai refactor <file>`**
Get intelligent refactoring suggestions to improve code quality.

```bash
mw ai refactor legacy/old_module.py
mw ai refactor utils/helpers.js
```

### Test Generation
**`mw ai test <file>`**
Generate comprehensive test cases for your code.

```bash
mw ai test src/calculator.py
mw ai test services/UserService.js
```

### Documentation Generation
**`mw ai doc <file>`**
Automatically generate documentation for your code.

```bash
mw ai doc src/api.py
mw ai doc components/Header.tsx
```

---

## 🔄 Git & Version Control AI

### Smart Commits
**`mw ai commit [--push]`**
Generate meaningful commit messages from your changes.

```bash
mw ai commit                    # Generate commit message
mw ai commit --push            # Commit and push
```

### Code Review
**`mw ai review [--staged]`**
AI-powered code review of your changes.

```bash
mw ai review                   # Review unstaged changes
mw ai review --staged          # Review staged changes
mw ai review --diff            # Review current diff
```

### Changelog Generation
**`mw ai changelog`**
Generate changelogs from your git commit history.

```bash
mw ai changelog                # Generate full changelog
```

---

## 👥 Pair Programming

### Live AI Pair Programming
**`mw pair`**
Start an AI pair programming session that watches your file changes.

```bash
mw pair                        # Start interactive pairing
mw pair --review              # Review all uncommitted changes
mw pair --quiet               # Only flag critical issues
```

### Pair Programming History
**`mw pair history`**
View your past AI pairing sessions and insights.

```bash
mw pair history               # Show session history
```

---

## 📊 Code Quality & Health

### File-Level Code Review
**`mw review <file>`**
Comprehensive AI code review for specific files.

```bash
mw review src/complex_module.py
mw review --diff              # Review current git diff
mw review --staged            # Review staged changes
```

### Project Health Scoring
**`mw health <project>`**
Get a 0-100 health score for your entire project.

```bash
mw health my-project          # Score project health
```

### Documentation Generation
**`mw docs generate <project>`**
Generate comprehensive AI documentation for entire projects.

```bash
mw docs generate my-api       # Generate project docs
```

---

## 🔧 Configuration

### AI Model Selection
MyWork-AI supports multiple AI models:

- **GPT-4** (default) - Best overall performance
- **Claude** - Excellent for code analysis
- **Gemini** - Great for large codebases
- **Local models** - Privacy-focused options

Configure your preferred model:

```bash
mw config set ai.model gpt-4
mw config set ai.model claude-3-sonnet
```

### API Keys
Set up your AI service API keys:

```bash
# OpenAI (required for default features)
export OPENAI_API_KEY="your-key-here"

# Optional: Claude API key
export ANTHROPIC_API_KEY="your-key-here"

# Optional: Google AI key  
export GOOGLE_AI_API_KEY="your-key-here"
```

---

## 💡 Best Practices

### Getting Better AI Responses

1. **Be specific**: Instead of "fix this", use "fix the authentication error in login.py"
2. **Provide context**: Include error messages, expected behavior, and relevant code snippets
3. **Iterative improvement**: Use AI suggestions as starting points, then refine

### Optimal Workflows

1. **Code → Review → Test**: Write code, get AI review, generate tests
2. **Pair Programming**: Use `mw pair` for real-time feedback during development
3. **Commit Intelligence**: Always use `mw ai commit` for better commit messages

### Performance Tips

- Use `--quiet` modes for faster responses on large codebases
- Cache AI responses locally (automatic in MyWork-AI)
- Use `mw ai explain` before modifying unfamiliar code

---

## 🚀 Advanced Features

### Custom AI Prompts
Create custom AI prompts for domain-specific tasks:

```bash
# Create custom prompt template
mw ai prompt create "security-review" "Review this code for security vulnerabilities..."

# Use custom prompt
mw ai prompt use "security-review" src/auth.py
```

### Batch Processing
Process multiple files with AI:

```bash
# Review all Python files
find . -name "*.py" -exec mw ai review {} \;

# Generate tests for all services
mw ai test services/*.js
```

### Integration with IDEs
MyWork-AI integrates with popular development environments:

- **VS Code**: Extension available for inline AI assistance
- **Vim/Neovim**: Plugin for terminal-based AI workflows  
- **Cursor**: Native compatibility with MyWork-AI commands

---

## 🔗 Related Documentation

- **[🔧 CLI Reference](cli-reference.md)** - Complete command documentation
- **[🚀 Deployment Guide](../DEPLOYMENT_GUIDE.md)** - Deploy AI-enhanced projects
- **[📖 Getting Started](quickstart.md)** - Basic setup and first steps

---

## 🆘 Troubleshooting

### Common Issues

**AI responses seem generic or unhelpful:**
- Provide more context in your prompts
- Use specific file paths and error messages
- Try different AI models (`mw config set ai.model claude-3-sonnet`)

**API rate limits exceeded:**
- Implement request throttling: `mw config set ai.rate_limit 10`
- Use local models for development: `mw config set ai.model local`

**Performance is slow:**
- Enable response caching: `mw config set ai.cache true`
- Use `--quiet` mode for large files
- Process files in smaller batches

### Getting Help

```bash
mw ai ask "I'm having trouble with..."
mw doctor                     # Check system health  
mw support                    # Get community support links
```

---

*💡 **Pro Tip**: The AI features learn from your codebase over time. The more you use them, the better they understand your project's patterns and conventions!*
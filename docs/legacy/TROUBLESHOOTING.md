# Troubleshooting Guide

This guide covers common issues and their solutions when using MyWork-AI.

## Installation Issues

### Python Version Error
```bash
Error: Python 3.8+ required, found Python 3.7.3
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.8 python3.8-pip

# macOS (using Homebrew)
brew install python@3.8

# Update alternatives
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
```

### Permission Denied During Installation
```bash
Permission denied: /usr/local/bin/mw
```

**Solution:**
```bash
# Option 1: Install to user directory
curl -fsSL https://mywork-ai.dev/install.sh | bash -s -- --user

# Option 2: Use sudo (not recommended)
curl -fsSL https://mywork-ai.dev/install.sh | sudo bash
```

### Node.js Not Found
```bash
Error: Node.js 16+ required
```

**Solution:**
```bash
# Install Node.js via NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Or use Node Version Manager (NVM)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

## Command Errors

### Command Not Found
```bash
mw: command not found
```

**Solution:**
```bash
# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc

# Or create symlink
sudo ln -s ~/.local/bin/mw /usr/local/bin/mw
```

### Template Not Found
```bash
Error: Template 'saas' not found
```

**Solution:**
```bash
# Update to get latest templates
mw update

# List available templates
mw list templates

# Check template directory
ls ~/.mywork-ai/templates/
```

### Invalid Project Name
```bash
Error: Invalid project name 'my project'
```

**Solution:**
Use valid naming conventions:
- No spaces (use hyphens or underscores)
- Start with letter or underscore
- Only alphanumeric characters, hyphens, underscores

```bash
# Good examples
mw create saas my-project
mw create saas my_project
mw create saas myProject

# Bad examples
mw create saas "my project"    # spaces
mw create saas 123project     # starts with number
mw create saas my@project     # special characters
```

## Project Creation Issues

### Dependency Installation Failure
```bash
npm ERR! peer dep missing
```

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Or use yarn
yarn install
```

### Database Connection Error
```bash
Error: Connection to database failed
```

**Solution:**
```bash
# Check database is running
sudo systemctl status postgresql

# Start database service
sudo systemctl start postgresql

# Check connection details in .env
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Test connection
psql -h localhost -U username -d database_name
```

### Port Already in Use
```bash
Error: Port 3000 already in use
```

**Solution:**
```bash
# Find and kill process using port
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm start

# Or set in .env
PORT=3001
```

## AI & API Issues

### API Key Not Set
```bash
Error: OpenAI API key not configured
```

**Solution:**
```bash
# Set in environment
export OPENAI_API_KEY="your-key-here"

# Or in .env file
echo "OPENAI_API_KEY=your-key-here" >> .env

# Or configure via command
mw config set api.openai.key "your-key-here"
```

### Rate Limit Exceeded
```bash
Error: Rate limit exceeded for API
```

**Solution:**
- Wait and retry (rate limits reset over time)
- Upgrade to higher API tier
- Use different AI provider
- Reduce request frequency

```bash
# Configure different provider
mw config set ai.provider anthropic
mw config set ai.anthropic.key "your-anthropic-key"
```

### AI Generation Failed
```bash
Error: Failed to generate code
```

**Solution:**
```bash
# Enable verbose logging
mw create saas my-app --verbose

# Try different model
mw config set ai.model gpt-3.5-turbo

# Check internet connection
ping api.openai.com

# Regenerate specific component
mw generate component MyComponent --force
```

## Deployment Issues

### Vercel Deployment Failed
```bash
Error: Deployment failed on Vercel
```

**Solution:**
```bash
# Check Vercel CLI
npx vercel --version

# Login to Vercel
npx vercel login

# Deploy with logs
npx vercel --debug

# Check build logs in Vercel dashboard
```

### Environment Variables Missing
```bash
Error: Required environment variable missing
```

**Solution:**
```bash
# Check required variables
cat .env.example

# Copy and configure
cp .env.example .env
nano .env

# For deployment, set in platform
# Vercel: Dashboard > Settings > Environment Variables
# Netlify: Site settings > Environment variables
```

### Build Failure
```bash
Error: Build failed with exit code 1
```

**Solution:**
```bash
# Check build logs
npm run build 2>&1 | tee build.log

# Clear build cache
rm -rf .next dist build

# Rebuild dependencies
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run type-check
```

## Git & Version Control

### Git Not Initialized
```bash
Error: Not a git repository
```

**Solution:**
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Add remote origin
git remote add origin https://github.com/username/repo.git
git push -u origin main
```

### Merge Conflicts
```bash
error: Your local changes to the following files would be overwritten by merge
```

**Solution:**
```bash
# Stash local changes
git stash

# Pull updates
git pull

# Apply stashed changes
git stash pop

# Resolve conflicts manually, then
git add .
git commit -m "Resolve merge conflicts"
```

## Performance Issues

### Slow Generation
- Large templates take time to generate
- AI requests have network latency
- Complex projects need more processing

**Solutions:**
- Use faster AI models (e.g., GPT-3.5 vs GPT-4)
- Generate smaller components incrementally
- Check internet connection speed
- Use local AI models for offline work

### Memory Issues
```bash
Error: JavaScript heap out of memory
```

**Solution:**
```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"

# Or run with more memory
node --max-old-space-size=4096 node_modules/.bin/mw create saas my-app
```

## Getting Help

### Debug Mode
```bash
# Enable debug logging
mw --debug create saas my-app

# Check logs
mw logs

# System info
mw doctor
```

### Common Diagnostic Commands
```bash
# Check system status
mw doctor

# Verify installation
mw version

# List available commands
mw --help

# Check configuration
mw config list

# Update framework
mw update

# Reset configuration
mw config reset
```

### Report Issues

If you can't resolve an issue:

1. **Search existing issues**: GitHub Issues
2. **Create minimal reproduction**: Small example showing the problem
3. **Include system info**: Run `mw doctor` and include output
4. **Provide logs**: Use `mw --debug` and include relevant logs
5. **Submit issue**: Create GitHub issue with template

### Support Channels

- **Documentation**: `docs/` directory
- **GitHub Issues**: Bug reports and feature requests
- **Community Discord**: Real-time help and discussions
- **Stack Overflow**: Tag questions with `mywork-ai`

---

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Command not found | Add to PATH or reinstall |
| Template not found | Run `mw update` |
| Port in use | Kill process or use different port |
| Build fails | Clear cache and rebuild |
| Deploy fails | Check environment variables |
| Git conflicts | Stash, pull, unstash |
| API errors | Check keys and rate limits |
| Memory error | Increase Node.js memory limit |

Remember: Most issues are solved by updating (`mw update`), checking configuration (`mw config list`), or reviewing logs (`mw logs`).
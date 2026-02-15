# 🚀 MyWork-AI Deployment Guide

Complete guide for deploying MyWork-AI in production environments.

## 📦 PyPI Installation (Recommended for End Users)

### Quick Start
```bash
# Install the core framework
pip install mywork-ai

# Initialize your workspace
mw setup

# Quick tour of features
mw tour

# Start building
mw new my-project
```

### Version Management
```bash
# Install specific version
pip install mywork-ai==2.0.0

# Install with optional dependencies
pip install mywork-ai[api,dev]  # API server + dev tools
pip install mywork-ai[all]      # All optional features

# Upgrade
pip install --upgrade mywork-ai
```

### Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv mywork-env
source mywork-env/bin/activate  # Linux/macOS
# mywork-env\Scripts\activate  # Windows

# Install in virtual environment
pip install mywork-ai
```

## 🐳 Docker Deployment

### Core Framework
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

# For API server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Example: AI Dashboard Backend
```bash
# Build the image
docker build -t mywork-ai-backend ./projects/ai-dashboard/backend

# Run with persistent storage
docker run -d \
  --name mywork-backend \
  -p 8000:8000 \
  -v mywork-data:/data \
  -e DATABASE_PATH=/data/dashboard.db \
  --env-file .env \
  mywork-ai-backend

# Check health
curl http://localhost:8000/
```

### Docker Compose (Full Stack)
```yaml
version: '3.8'
services:
  backend:
    build: ./projects/ai-dashboard/backend
    ports:
      - "8000:8000"
    volumes:
      - api_data:/data
    environment:
      - DATABASE_PATH=/data/dashboard.db
    env_file: .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./projects/ai-dashboard/frontend  
    ports:
      - "3000:3000"
    depends_on:
      - backend
    env_file: .env

volumes:
  api_data:
```

## ▲ Vercel Deployment (Frontend)

### Quick Deploy
```bash
# From project root
vercel --prod

# Or deploy specific frontend
cd projects/ai-dashboard/frontend
vercel --prod
```

### Configuration
The root `vercel.json` automatically deploys the AI Dashboard frontend:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs",
  "rootDirectory": "projects/ai-dashboard/frontend"
}
```

### Environment Variables in Vercel
Set these in your Vercel dashboard:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `AUTH_GITHUB_ID`
- `AUTH_GITHUB_SECRET`
- `ANTHROPIC_API_KEY`

### Custom Domains
```bash
# Add custom domain
vercel domains add yourdomain.com
vercel domains add api.yourdomain.com
```

## 🚂 Railway Deployment (Backend/API)

### Quick Deploy
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway deploy

# Or deploy specific backend
cd projects/ai-dashboard/backend
railway up
```

### Configuration
Uses `railway.json` in backend directories:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "healthcheckPath": "/",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Environment Variables
Set in Railway dashboard or via CLI:
```bash
railway variables set DATABASE_PATH=/data/dashboard.db
railway variables set ANTHROPIC_API_KEY=your-key-here
railway variables set PORT=8000
```

### Persistent Storage
```bash
# Add volume for SQLite database
railway volumes create data --mount-path /data
```

## 🔧 Environment Variables Reference

### Required (Core)
| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key (primary LLM) | `sk-ant-xxxxx` |

### LLM Providers (Choose at least one)
| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI/GPT models | Optional |
| `OPENROUTER_API_KEY` | 100+ models via OpenRouter | Optional |
| `GROQ_API_KEY` | Fast inference | Optional |
| `ZAI_API_KEY` | GLM models | Optional |

### Workflow Automation
| Variable | Description | Required |
|----------|-------------|----------|
| `N8N_API_URL` | n8n instance URL | For n8n tools |
| `N8N_API_KEY` | n8n API key | For n8n tools |

### Development
| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub API access | For git tools |
| `GOOGLE_CLIENT_ID` | Google OAuth | For YouTube/Drive |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | For YouTube/Drive |

### Authentication (Web Apps)
| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk public key | For web apps |
| `CLERK_SECRET_KEY` | Clerk secret key | For web apps |
| `AUTH_GITHUB_ID` | GitHub OAuth ID | For GitHub auth |
| `AUTH_GITHUB_SECRET` | GitHub OAuth secret | For GitHub auth |

### Optional Services
| Variable | Description | Use Case |
|----------|-------------|----------|
| `RESEND_API_KEY` | Email sending | Email automation |
| `TELEGRAM_BOT_TOKEN` | Telegram bot | Bot integrations |
| `FIRECRAWL_API_KEY` | Web scraping | Content extraction |
| `APIFY_API_TOKEN` | Web automation | Advanced scraping |
| `RENDER_API_KEY` | Render deployments | Auto-deploy |
| `NETLIFY_AUTH_TOKEN` | Netlify deployments | Static sites |
| `SUPABASE_URL` | Supabase database | Cloud database |
| `SUPABASE_KEY` | Supabase API key | Cloud database |

## ✅ Production Checklist

### Before Launch
- [ ] Environment variables configured
- [ ] Database backups scheduled
- [ ] SSL certificates configured
- [ ] Domain names configured
- [ ] Health checks working
- [ ] Monitoring set up
- [ ] Error tracking enabled

### Security
- [ ] API keys secured (not in code)
- [ ] Authentication configured
- [ ] CORS configured properly
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] Dependencies updated

### Performance
- [ ] Database optimized
- [ ] Caching configured
- [ ] CDN configured (if needed)
- [ ] Load testing completed
- [ ] Resource limits set

### Monitoring
- [ ] Application metrics
- [ ] Error tracking (Sentry recommended)
- [ ] Uptime monitoring
- [ ] Log aggregation
- [ ] Alert notifications

### Backup & Recovery
- [ ] Database backups automated
- [ ] Code repository backed up
- [ ] Environment configuration backed up
- [ ] Recovery procedures documented
- [ ] Backup restoration tested

## 🔧 Common Issues & Solutions

### 1. Module Import Errors
```bash
# Ensure MyWork-AI is properly installed
pip install mywork-ai

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall if needed
pip uninstall mywork-ai
pip install mywork-ai
```

### 2. Environment Variables Not Loading
```bash
# Check .env file exists and is readable
cat .env

# Ensure python-dotenv is installed
pip install python-dotenv

# Test environment loading
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY', 'Not set'))"
```

### 3. Docker Build Issues
```bash
# Clear Docker cache
docker builder prune

# Build with no cache
docker build --no-cache -t mywork-ai .

# Check disk space
docker system df
```

### 4. Database Connection Issues
```bash
# Check database path exists
mkdir -p /data

# Check permissions
chmod 755 /data

# For SQLite, check write permissions
touch /data/test.db && rm /data/test.db
```

### 5. API Health Check Failures
```bash
# Test health endpoint
curl -f http://localhost:8000/

# Check application logs
docker logs mywork-backend

# Verify port binding
netstat -tlnp | grep 8000
```

## 📚 Additional Resources

- [MyWork-AI GitHub Repository](https://github.com/dansidanutz/MyWork-AI)
- [Bug Reports & Issues](https://github.com/dansidanutz/MyWork-AI/issues)
- [Contributing Guide](CONTRIBUTING.md)
- [FAQ](FAQ.md)
- [Changelog](CHANGELOG.md)

## 🆘 Getting Help

1. Check this deployment guide
2. Review the [FAQ](FAQ.md)
3. Search existing [GitHub issues](https://github.com/dansidanutz/MyWork-AI/issues)
4. Create a new issue with:
   - Environment details
   - Deployment method used
   - Full error messages
   - Steps to reproduce

---

**Happy Deploying!** 🎉

Deploy with confidence using this comprehensive guide. Each deployment method is production-tested and includes monitoring, security, and backup considerations.
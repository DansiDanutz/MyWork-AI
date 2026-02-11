# Getting Started Workflow

This workflow guides you through setting up your first MyWork-AI project from installation to deployment.

## Prerequisites

- Python 3.8+
- Git
- Node.js 16+ (for web projects)
- Code editor (VS Code recommended)

## Workflow Steps

### 1. Installation (5 minutes)

```bash
# Download and run the installer
curl -fsSL https://mywork-ai.dev/install.sh | bash

# Or clone and install manually
git clone https://github.com/yourorg/MyWork-AI.git
cd MyWork-AI
./install.sh
```

**Verification:**
```bash
# Check installation
mw version
mw status

# Should show:
# MyWork-AI v1.0.0
# System: Ready ✅
```

### 2. Choose Your Project Type (2 minutes)

```bash
# List available templates
mw list templates

# Available options:
# - saas: Complete SaaS application
# - marketplace: P2P marketplace platform
# - fastapi: Backend API only
# - nextjs: Frontend application only
# - fullstack: FastAPI + Next.js
# - blog: Content management system
# - mobile: React Native app
```

### 3. Create Your First Project (1 minute)

```bash
# Choose a template and create project
mw create <template> <project-name>

# Examples:
mw create saas my-startup
mw create marketplace freelance-hub
mw create fastapi task-api
mw create nextjs dashboard
mw create fullstack team-app
```

### 4. Explore the Generated Structure (5 minutes)

```bash
# Navigate to your project
cd projects/<project-name>

# Explore the structure
tree -L 2  # or ls -la
```

**Typical Structure:**
```
my-project/
├── .planning/          # GSD methodology files
├── backend/           # API server (if applicable)
├── frontend/          # Web UI (if applicable)
├── database/          # Database schemas and migrations
├── docs/              # Auto-generated documentation
├── tests/             # Test suites
├── .env.example       # Environment configuration
├── docker-compose.yml # Development environment
└── README.md          # Project-specific guide
```

### 5. Configure Environment (3 minutes)

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # or your preferred editor
```

**Essential Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Authentication
SECRET_KEY=your-secret-key
NEXTAUTH_SECRET=your-nextauth-secret

# External APIs
STRIPE_SECRET_KEY=sk_test_...  # for payment features
OPENAI_API_KEY=sk-...         # for AI features

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

### 6. Start Development Environment (2 minutes)

#### Option A: Docker (Recommended)
```bash
# Start all services
docker-compose up

# Check services are running
docker-compose ps
```

#### Option B: Manual Setup
```bash
# Backend (if applicable)
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (if applicable)
cd frontend
npm install
npm run dev
```

### 7. Verify Everything Works (3 minutes)

#### Web Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

#### Test Basic Functionality
```bash
# Run health check
curl http://localhost:8000/health

# Should return: {"status": "healthy"}
```

#### Check Database
```bash
# View database migrations
cd backend
alembic history

# Run initial migration
alembic upgrade head
```

### 8. Make Your First Changes (10 minutes)

#### Update Project Information
```bash
# Edit project metadata
nano .planning/PROJECT.md
```

#### Customize Branding
```bash
# Update frontend title and branding
nano frontend/app/layout.tsx
nano frontend/public/logo.svg
```

#### Add a New Feature
```bash
# Generate a new component/route
mw generate component UserProfile
mw generate route /api/profile
```

### 9. Test Your Changes (5 minutes)

```bash
# Run tests
npm test               # Frontend tests
python -m pytest      # Backend tests

# Check code quality
npm run lint
npm run type-check
```

### 10. Git Setup and Initial Commit (5 minutes)

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Generated with MyWork-AI"

# Connect to remote repository
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

## Next Steps

### Development Phase
- [ ] Explore the generated documentation in `docs/`
- [ ] Read through code examples and comments
- [ ] Set up your preferred IDE extensions
- [ ] Configure development tools (linting, formatting)

### Customization Phase
- [ ] Update database models for your specific needs
- [ ] Modify UI components and styling
- [ ] Add custom API endpoints
- [ ] Integrate external services

### Production Phase
- [ ] Set up production environment variables
- [ ] Configure CI/CD pipeline (see `workflows/deploy_to_production.md`)
- [ ] Set up monitoring and logging
- [ ] Deploy to your preferred platform

## Common Issues and Solutions

### Installation Issues
```bash
# Python version error
python3 --version  # Should be 3.8+
# Update if needed

# Permission denied
sudo chown -R $USER:$USER ~/.mywork-ai
```

### Development Issues
```bash
# Port already in use
lsof -ti:3000 | xargs kill -9  # Kill process on port 3000
PORT=3001 npm start             # Use different port

# Database connection failed
# Check docker-compose.yml ports and credentials
docker-compose logs db
```

### Build Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Backend dependencies
rm -rf venv
python -m venv venv
pip install -r requirements.txt
```

## Getting Help

### Documentation
- Project README: `README.md`
- API Documentation: `http://localhost:8000/docs`
- Frontend Components: `frontend/components/README.md`

### Community
- GitHub Issues: Report bugs or request features
- Discord/Slack: Real-time community help
- Stack Overflow: Tag questions with `mywork-ai`

### Professional Support
- Documentation: `docs/`
- Consulting: Contact maintainers
- Training: Available workshops

## Success Criteria

By the end of this workflow, you should have:

✅ **Functional Development Environment**
- All services running without errors
- Database connected and migrated
- Frontend accessible at localhost:3000

✅ **Basic Understanding**
- Know where to find key files
- Can make simple changes
- Tests are passing

✅ **Ready for Development**
- Git repository set up
- Development tools configured
- Next steps planned

**Estimated Total Time: 30-45 minutes**

---

**Next Workflow:** [AI-Assisted Development](./ai_assisted_development.md) - Learn how to leverage AI features for faster development.
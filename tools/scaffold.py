#!/usr/bin/env python3
"""
Project Scaffolding Tool for MyWork Framework
==============================================
Quickly create new projects with pre-configured templates.

Usage:
    python scaffold.py new <name> [template]   # Create new project
    python scaffold.py list                    # List available templates
    python scaffold.py from-module <name> <module_id>  # Create from registry module

Templates:
    - basic: Empty project with GSD structure
    - fastapi: FastAPI backend with SQLite
    - nextjs: Next.js frontend with TypeScript
    - fullstack: FastAPI backend + Next.js frontend
    - cli: Python CLI application
    - automation: n8n + Python automation project
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Configuration - Import from shared config with fallback
try:
    from config import MYWORK_ROOT, PROJECTS_DIR

    TEMPLATES_DIR = PROJECTS_DIR / "_template"
except ImportError:

    def _get_mywork_root():
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        return script_dir.parent if script_dir.name == "tools" else Path.home() / "MyWork"

    MYWORK_ROOT = _get_mywork_root()
    PROJECTS_DIR = MYWORK_ROOT / "projects"
    TEMPLATES_DIR = PROJECTS_DIR / "_template"

# Template definitions
TEMPLATES = {
    "basic": {
        "description": "Empty project with GSD structure",
        "structure": {
            ".planning": {
                "PROJECT.md": "# {name}\n\n## Vision\n\n[Describe what this project does]\n\n## Goals\n\n- [ ] Goal 1\n- [ ] Goal 2\n\n## Non-Goals\n\n- What this project does NOT do\n",
                "ROADMAP.md": "# {name} Roadmap\n\n## Current Milestone: v1.0\n\n### Phase 1: Setup\n- [ ] Initialize project structure\n- [ ] Configure development environment\n\n### Phase 2: Core Features\n- [ ] Feature 1\n- [ ] Feature 2\n",
                "STATE.md": "# {name} State\n\n## Current Phase\nPhase 1: Setup\n\n## Last Updated\n{date}\n\n## Recent Decisions\n\n## Blockers\nNone\n\n## Next Steps\n1. Define project requirements\n2. Set up development environment\n",
            },
            "tests/": {
                "__init__.py": "",
                "test_example.py": '''"""
Sample tests for {name}
"""
import unittest


class TestExample(unittest.TestCase):
    """Example test class."""
    
    def test_example(self):
        """Example test case."""
        self.assertTrue(True)
        
    def test_math(self):
        """Test basic math."""
        self.assertEqual(2 + 2, 4)


if __name__ == "__main__":
    unittest.main()
''',
            },
            ".env.example": """# {name} Environment Variables
# Copy this file to .env and configure your values

# API Keys
# OPENAI_API_KEY=your_openai_key_here
# OPENROUTER_API_KEY=your_openrouter_key_here

# Environment
DEBUG=true
""",
            "README.md": "# {name}\n\nA new project created with MyWork scaffold.\n\n## Quick Start\n\n```bash\n# Copy environment template\ncp .env.example .env\n\n# Set up your development environment\n# Add your specific setup instructions here\n```\n\n## Testing\n\n```bash\n# Run tests\npython -m pytest tests/\n# Or with unittest\npython -m unittest discover tests/\n```\n",
            ".gitignore": "# Dependencies\nnode_modules/\nvenv/\n.venv/\n\n# Environment\n.env\n.env.local\n\n# Build\ndist/\nbuild/\n.next/\n\n# IDE\n.idea/\n.vscode/\n*.swp\n\n# OS\n.DS_Store\nThumbs.db\n\n# Python\n__pycache__/\n*.pyc\n*.pyo\n",
        },
    },
    "fastapi": {
        "description": "FastAPI backend with SQLite",
        "structure": {
            ".planning": {
                "PROJECT.md": "# {name} API\n\n## Vision\nREST API built with FastAPI.\n\n## Tech Stack\n- FastAPI\n- SQLite + SQLAlchemy\n- Pydantic\n\n## Goals\n- [ ] Define API endpoints\n- [ ] Implement database models\n- [ ] Add authentication\n",
                "ROADMAP.md": "# Roadmap\n\n## Phase 1: Foundation\n- [ ] FastAPI setup\n- [ ] Database models\n- [ ] Basic CRUD endpoints\n\n## Phase 2: Features\n- [ ] Authentication\n- [ ] Validation\n- [ ] Error handling\n",
                "STATE.md": "# State\n\n## Current Phase\nPhase 1: Foundation\n\n## Last Updated\n{date}\n",
            },
            "backend": {
                "main.py": '''"""
{name} API
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="{name} API",
    description="API for {name}",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {{"message": "Welcome to {name} API"}}


@app.get("/health")
async def health():
    return {{"status": "healthy"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
''',
                "requirements.txt": """fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
pydantic>=2.5.0
httpx>=0.25.0
""",
                "database": {
                    "__init__.py": "",
                    "db.py": '''"""Database configuration."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
                    "models.py": '''"""Database models."""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .db import Base


class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
''',
                },
            },
            "start.sh": """#!/bin/bash
cd backend
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt -q
python main.py
""",
            "tests/": {
                "__init__.py": "",
                "test_main.py": '''"""
Tests for {name} API
"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_not_found():
    """Test 404 handling."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
''',
                "conftest.py": '''"""
Test configuration for pytest.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)
''',
            },
            ".env.example": """# {name} API Environment Variables
# Copy this file to .env and configure your values

# Database
DATABASE_URL=sqlite:///./app.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# JWT Secret (for authentication)
JWT_SECRET=your-secret-key-change-in-production

# API Keys
OPENAI_API_KEY=your_openai_key_here
""",
            "README.md": "# {name}\n\n## Setup\n\n```bash\ncd backend\npython -m venv venv\nsource venv/bin/activate\npip install -r requirements.txt\n\n# Copy and configure environment\ncp .env.example .env\n\n# Run the application\npython main.py\n```\n\nAPI available at http://localhost:8000\n\n## Testing\n\n```bash\n# Install test dependencies\npip install pytest httpx\n\n# Run tests\npython -m pytest tests/\n```\n\n## API Documentation\n\nOpenAPI docs available at:\n- Swagger UI: http://localhost:8000/docs\n- ReDoc: http://localhost:8000/redoc\n",
            ".gitignore": "venv/\n.env\n*.db\n__pycache__/\n*.pyc\n.pytest_cache/\n",
        },
    },
    "nextjs": {
        "description": "Next.js frontend with TypeScript and Tailwind",
        "structure": {
            ".planning": {
                "PROJECT.md": "# {name} Frontend\n\n## Vision\nModern web application with Next.js.\n\n## Tech Stack\n- Next.js 14\n- TypeScript\n- Tailwind CSS\n\n## Goals\n- [ ] Set up pages\n- [ ] Create components\n- [ ] Connect to API\n",
                "ROADMAP.md": "# Roadmap\n\n## Phase 1: Setup\n- [ ] Next.js configuration\n- [ ] Tailwind setup\n- [ ] Layout components\n\n## Phase 2: Features\n- [ ] Main pages\n- [ ] API integration\n",
                "STATE.md": "# State\n\n## Current Phase\nPhase 1: Setup\n\n## Last Updated\n{date}\n",
            },
            "frontend": {
                "package.json": """{
  "name": "{name_lower}",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0"
  },
  "devDependencies": {
    "@types/node": "20.10.0",
    "@types/react": "18.2.0",
    "autoprefixer": "10.4.16",
    "postcss": "8.4.32",
    "tailwindcss": "3.4.1",
    "typescript": "5.3.3"
  }
}""",
                "tsconfig.json": """{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}""",
                "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}""",
                "app": {
                    "layout.tsx": """import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '{name}',
  description: 'Built with Next.js',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}""",
                    "page.tsx": """export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold">{name}</h1>
      <p className="mt-4 text-gray-600">Welcome to your new project!</p>
    </main>
  )
}""",
                    "globals.css": """@tailwind base;
@tailwind components;
@tailwind utilities;
""",
                },
            },
            "start.sh": """#!/bin/bash
cd frontend
npm install
npm run dev
""",
            "README.md": "# {name}\n\n## Setup\n\n```bash\ncd frontend\nnpm install\nnpm run dev\n```\n\nApp available at http://localhost:3000\n",
            ".gitignore": "node_modules/\n.next/\n.env.local\n",
        },
    },
    "fullstack": {
        "description": "FastAPI backend + Next.js frontend",
        "structure": "COMBINE:fastapi+nextjs",  # Special marker to combine templates
    },
    "cli": {
        "description": "Python CLI application with Click",
        "structure": {
            ".planning": {
                "PROJECT.md": "# {name} CLI\n\n## Vision\nCommand-line tool for...\n\n## Commands\n- `{name} command1`\n- `{name} command2`\n",
                "ROADMAP.md": "# Roadmap\n\n## Phase 1: Core\n- [ ] CLI structure\n- [ ] Main commands\n\n## Phase 2: Features\n- [ ] Configuration\n- [ ] Output formatting\n",
                "STATE.md": "# State\n\n## Current Phase\nPhase 1: Core\n\n## Last Updated\n{date}\n",
            },
            "src": {
                "__init__.py": "",
                "cli.py": '''"""
{name} CLI
Main entry point for the command-line interface.
"""
import click


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """{name} - Your CLI description here."""
    pass


@cli.command()
@click.argument("name", default="World")
def hello(name: str):
    """Say hello."""
    click.echo(f"Hello, {{name}}!")


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def status(verbose: bool):
    """Show status."""
    click.echo("Status: OK")
    if verbose:
        click.echo("Everything is running smoothly.")


if __name__ == "__main__":
    cli()
''',
            },
            "requirements.txt": """click>=8.1.0
rich>=13.0.0
python-dotenv>=1.0.0
""",
            "setup.py": """from setuptools import setup, find_packages

setup(
    name="{name_lower}",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
    ],
    entry_points={{
        "console_scripts": [
            "{name_lower}=src.cli:cli",
        ],
    }},
)
""",
            "README.md": "# {name}\n\n## Installation\n\n```bash\npip install -e .\n```\n\n## Usage\n\n```bash\n{name_lower} --help\n{name_lower} hello\n{name_lower} status -v\n```\n",
            ".gitignore": "venv/\n.env\n__pycache__/\n*.pyc\n*.egg-info/\ndist/\nbuild/\n",
        },
    },
    "automation": {
        "description": "n8n + Python automation project",
        "structure": {
            ".planning": {
                "PROJECT.md": "# {name} Automation\n\n## Vision\nAutomation workflows using n8n and Python.\n\n## Workflows\n- Workflow 1: Description\n- Workflow 2: Description\n\n## Integrations\n- List APIs/services\n",
                "ROADMAP.md": "# Roadmap\n\n## Phase 1: Setup\n- [ ] n8n workflow design\n- [ ] Python handlers\n\n## Phase 2: Integration\n- [ ] API connections\n- [ ] Scheduling\n",
                "STATE.md": "# State\n\n## Current Phase\nPhase 1: Setup\n\n## Last Updated\n{date}\n\n## n8n Workflows\n| Name | ID | Status |\n|------|-----|--------|\n",
            },
            "scripts": {
                "__init__.py": "",
                "webhook_handler.py": '''"""
Webhook handler for n8n callbacks.
"""
from fastapi import FastAPI, Request
import json

app = FastAPI(title="{name} Webhook Handler")


@app.post("/webhook/{workflow_name}")
async def handle_webhook(workflow_name: str, request: Request):
    """Handle incoming webhook from n8n."""
    data = await request.json()
    print(f"Received webhook for {{workflow_name}}: {{json.dumps(data, indent=2)}}")

    # Process the webhook data here
    result = {{"status": "processed", "workflow": workflow_name}}

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
''',
            },
            "workflows": {
                "README.md": "# n8n Workflows\n\nExport your n8n workflows here as JSON files.\n\n## Workflow List\n\n1. `workflow_name.json` - Description\n",
            },
            "requirements.txt": """fastapi>=0.109.0
uvicorn[standard]>=0.27.0
httpx>=0.25.0
python-dotenv>=1.0.0
""",
            "README.md": "# {name}\n\n## Setup\n\n1. Configure n8n workflows\n2. Set up webhook handlers\n3. Run: `python scripts/webhook_handler.py`\n\n## n8n Integration\n\nPoint n8n HTTP Request nodes to:\n- Webhook URL: `http://localhost:8001/webhook/<workflow_name>`\n",
            ".gitignore": "venv/\n.env\n__pycache__/\n*.pyc\n",
        },
    },
    "saas": {
        "description": "Full SaaS starter with FastAPI, SQLite, JWT auth, and Stripe",
        "structure": {
            ".planning": {
                "PROJECT.md": "# {name} SaaS Platform\n\n## Vision\nComplete SaaS application with authentication, payments, and modern frontend.\n\n## Tech Stack\n- FastAPI backend with JWT authentication\n- SQLite database with users, subscriptions\n- Stripe payment integration\n- Next.js frontend\n- Docker deployment\n\n## Goals\n- [ ] User authentication (JWT)\n- [ ] Payment processing (Stripe)\n- [ ] Subscription management\n- [ ] API rate limiting\n- [ ] Frontend dashboard\n",
                "ROADMAP.md": "# SaaS Roadmap\n\n## Phase 1: Foundation\n- [ ] Authentication system\n- [ ] Database models\n- [ ] API endpoints\n\n## Phase 2: Payments\n- [ ] Stripe integration\n- [ ] Subscription plans\n- [ ] Webhook handling\n\n## Phase 3: Frontend\n- [ ] Landing page\n- [ ] User dashboard\n- [ ] Payment flow\n",
                "STATE.md": "# State\n\n## Current Phase\nPhase 1: Foundation\n\n## Last Updated\n{date}\n\n## Environment Setup\n- [ ] Database created\n- [ ] Stripe keys configured\n- [ ] JWT secret set\n",
            },
            "backend": {
                "main.py": '''"""
{name} SaaS API
FastAPI application with authentication and payments.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from database.db import get_db, engine
from database import models
from auth import auth_handler
from routes import auth, users, payments

load_dotenv()

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="{name} API",
    description="SaaS platform API with authentication and payments",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])

@app.get("/")
async def root():
    return {{"message": "Welcome to {name} SaaS API"}}

@app.get("/health")
async def health():
    return {{"status": "healthy", "environment": os.getenv("ENVIRONMENT", "development")}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
''',
                "requirements.txt": """fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
pydantic>=2.5.0
httpx>=0.25.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
stripe>=7.0.0
python-multipart>=0.0.6
""",
                "database": {
                    "__init__.py": "",
                    "models.py": '''"""Database models for SaaS application."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .db import Base

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    stripe_customer_id = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_subscription_id = Column(String, unique=True)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIALING)
    plan_name = Column(String, nullable=False)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscription")
''',
                    "db.py": '''"""Database configuration."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./saas.db")

engine = create_engine(DATABASE_URL, connect_args={{"check_same_thread": False}} if "sqlite" in DATABASE_URL else {{}})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
                },
                "auth": {
                    "__init__.py": "",
                    "auth_handler.py": '''"""JWT authentication handler."""
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import os

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({{"exp": expire}})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={{"WWW-Authenticate": "Bearer"}},
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={{"WWW-Authenticate": "Bearer"}},
        )
''',
                },
                "routes": {
                    "__init__.py": "",
                    "auth.py": '''"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database.db import get_db
from database.models import User
from auth.auth_handler import verify_password, get_password_hash, create_access_token, verify_token

router = APIRouter()
security = HTTPBearer()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Token)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(data={{"sub": user.email}})
    return {{"access_token": access_token, "token_type": "bearer"}}

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={{"WWW-Authenticate": "Bearer"}},
        )
    
    access_token = create_access_token(data={{"sub": user.email}})
    return {{"access_token": access_token, "token_type": "bearer"}}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
''',
                    "users.py": '''"""User management routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.db import get_db
from database.models import User
from .auth import get_current_user

router = APIRouter()

class UserProfile(BaseModel):
    email: str
    full_name: str = None
    is_active: bool
    is_verified: bool
    created_at: str

    class Config:
        from_attributes = True

@router.get("/me", response_model=UserProfile)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me")
async def update_profile(full_name: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.full_name = full_name
    db.commit()
    return {{"message": "Profile updated successfully"}}
''',
                    "payments.py": '''"""Payment and subscription routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.db import get_db
from database.models import User, Subscription
from .auth import get_current_user
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

router = APIRouter()

class CreateCheckoutSession(BaseModel):
    price_id: str

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CreateCheckoutSession,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={{"user_id": current_user.id}}
            )
            current_user.stripe_customer_id = customer.id
            db.commit()

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{{
                'price': request.price_id,
                'quantity': 1,
            }}],
            mode='subscription',
            success_url=os.getenv("FRONTEND_URL", "http://localhost:3000") + '/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=os.getenv("FRONTEND_URL", "http://localhost:3000") + '/cancel',
        )

        return {{"checkout_url": checkout_session.url}}

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/subscription")
async def get_subscription(current_user: User = Depends(get_current_user)):
    if current_user.subscription:
        return {{
            "status": current_user.subscription.status.value,
            "plan_name": current_user.subscription.plan_name,
            "current_period_end": current_user.subscription.current_period_end
        }}
    return {{"status": "none"}}

@router.post("/webhook")
async def stripe_webhook():
    # TODO: Implement Stripe webhook handling
    # Verify webhook signature and handle events like:
    # - customer.subscription.created
    # - customer.subscription.updated
    # - customer.subscription.deleted
    # - invoice.payment_succeeded
    # - invoice.payment_failed
    return {{"status": "ok"}}
''',
                },
            },
            "frontend": {
                "package.json": """{
  "name": "{name_lower}-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "@stripe/stripe-js": "^2.4.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/node": "20.10.0",
    "@types/react": "18.2.0",
    "autoprefixer": "10.4.16",
    "postcss": "8.4.32",
    "tailwindcss": "3.4.1",
    "typescript": "5.3.3"
  }
}""",
                "app": {
                    "page.tsx": """'use client'
import { useState } from 'react'

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">{name}</h1>
            </div>
            <div className="flex items-center space-x-4">
              {!isLoggedIn ? (
                <>
                  <button className="text-gray-600 hover:text-gray-900">Login</button>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                    Sign Up
                  </button>
                </>
              ) : (
                <button className="text-gray-600 hover:text-gray-900">Dashboard</button>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-4xl font-bold text-gray-900 sm:text-6xl">
            Welcome to {name}
          </h2>
          <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
            Your complete SaaS solution with authentication, payments, and modern design.
            Built with FastAPI, Next.js, and Stripe.
          </p>
          
          <div className="mt-10">
            <button className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg hover:bg-blue-700 transition-colors">
              Get Started
            </button>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-3">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900">Authentication</h3>
              <p className="mt-2 text-gray-600">JWT-based auth with registration and login</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900">Payments</h3>
              <p className="mt-2 text-gray-600">Stripe integration for subscriptions</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900">Modern Stack</h3>
              <p className="mt-2 text-gray-600">FastAPI backend with Next.js frontend</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}""",
                    "layout.tsx": """import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '{name} SaaS Platform',
  description: 'Complete SaaS solution with authentication and payments',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}""",
                    "globals.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}
""",
                },
            },
            "docker-compose.yml": """version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./saas.db
      - JWT_SECRET=your-jwt-secret-change-this
      - STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
      - STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
      - FRONTEND_URL=http://localhost:3000
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
      
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: saas_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
""",
            ".env.example": """# Database
DATABASE_URL=sqlite:///./saas.db
# For PostgreSQL: DATABASE_URL=postgresql://postgres:password@localhost:5432/saas_db

# JWT
JWT_SECRET=your-very-secret-jwt-key-change-this-in-production

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Frontend
FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# Environment
ENVIRONMENT=development
""",
            "README.md": "# {name} SaaS Platform\n\nComplete SaaS starter with authentication, payments, and modern design.\n\n## Features\n\n- FastAPI backend with JWT authentication\n- SQLite database with user and subscription models\n- Stripe payment integration\n- Next.js frontend with Tailwind CSS\n- Docker deployment ready\n\n## Quick Start\n\n1. **Setup Environment**\n   ```bash\n   cp .env.example .env\n   # Edit .env with your Stripe keys and JWT secret\n   ```\n\n2. **Run with Docker**\n   ```bash\n   docker-compose up --build\n   ```\n\n3. **Or run manually**\n   ```bash\n   # Backend\n   cd backend\n   pip install -r requirements.txt\n   python main.py\n   \n   # Frontend\n   cd frontend\n   npm install\n   npm run dev\n   ```\n\n## URLs\n\n- Frontend: http://localhost:3000\n- Backend API: http://localhost:8000\n- API Docs: http://localhost:8000/docs\n\n## Stripe Setup\n\n1. Create a Stripe account at https://stripe.com\n2. Get your test keys from the Stripe dashboard\n3. Create subscription products and get their price IDs\n4. Set up webhook endpoints for subscription events\n\n## Deployment\n\nFor production:\n1. Set up PostgreSQL database\n2. Configure environment variables\n3. Set up Stripe webhooks\n4. Deploy backend and frontend separately or use Docker\n",
            ".gitignore": "venv/\nnode_modules/\n.env\n*.db\n__pycache__/\n*.pyc\n.next/\ndist/\nbuild/\n*.egg-info/\n",
        },
    },
    "api-gateway": {
        "description": "API Gateway/Hub with rate limiting, key management, and monitoring",
        "structure": {
            ".planning": {
                "PROJECT.md": "# {name} API Gateway\n\n## Vision\nCentralized API gateway for managing multiple services with rate limiting, authentication, and monitoring.\n\n## Tech Stack\n- FastAPI with middleware\n- Redis for rate limiting and caching\n- PostgreSQL for API key management\n- Prometheus metrics\n- Swagger documentation\n\n## Goals\n- [ ] API key management\n- [ ] Rate limiting per key/endpoint\n- [ ] Request/response logging\n- [ ] Health monitoring\n- [ ] Load balancing\n",
                "ROADMAP.md": "# API Gateway Roadmap\n\n## Phase 1: Core Gateway\n- [ ] Basic proxy functionality\n- [ ] API key authentication\n- [ ] Rate limiting\n\n## Phase 2: Advanced Features\n- [ ] Request transformation\n- [ ] Caching\n- [ ] Analytics dashboard\n\n## Phase 3: Monitoring\n- [ ] Metrics collection\n- [ ] Alerting\n- [ ] Performance optimization\n",
                "STATE.md": "# State\n\n## Current Phase\nPhase 1: Core Gateway\n\n## Last Updated\n{date}\n\n## Services Configured\n- [ ] Service 1: Description\n- [ ] Service 2: Description\n",
            },
            "src": {
                "main.py": '''"""
{name} API Gateway
Centralized gateway for managing multiple services.
"""
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import redis
import time
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from auth import api_key_auth
from middleware import RateLimitMiddleware, LoggingMiddleware
from models import APIKey, RequestLog
from database import get_db

app = FastAPI(
    title="{name} API Gateway",
    description="Centralized API gateway with rate limiting and monitoring",
    version="1.0.0"
)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=0,
    decode_responses=True
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, redis_client=redis_client)

# Service registry
SERVICES = {{
    "api1": {{
        "url": os.getenv("SERVICE_API1_URL", "http://localhost:8001"),
        "timeout": 30,
        "retries": 3
    }},
    "api2": {{
        "url": os.getenv("SERVICE_API2_URL", "http://localhost:8002"),
        "timeout": 30,
        "retries": 3
    }}
}}

@app.get("/")
async def root():
    return {{
        "message": "Welcome to {name} API Gateway",
        "services": list(SERVICES.keys()),
        "version": "1.0.0"
    }}

@app.get("/health")
async def health():
    """Health check endpoint."""
    # Check Redis
    try:
        redis_client.ping()
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"
    
    # Check services
    service_status = {{}}
    async with httpx.AsyncClient() as client:
        for service_name, config in SERVICES.items():
            try:
                response = await client.get(f"{{config['url']}}/health", timeout=5)
                service_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception:
                service_status[service_name] = "unhealthy"
    
    return {{
        "status": "healthy",
        "redis": redis_status,
        "services": service_status,
        "timestamp": datetime.utcnow().isoformat()
    }}

@app.api_route("/api/{{service}}/{{path:path}}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(
    service: str,
    path: str,
    request: Request,
    api_key: APIKey = Depends(api_key_auth.get_current_api_key)
):
    """Proxy requests to backend services."""
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{{service}}' not found")
    
    service_config = SERVICES[service]
    target_url = f"{{service_config['url']}}/{{path}}"
    
    # Get request data
    body = await request.body()
    headers = dict(request.headers)
    
    # Remove hop-by-hop headers
    hop_by_hop_headers = {{
        "connection", "keep-alive", "proxy-authenticate",
        "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"
    }}
    headers = {{k: v for k, v in headers.items() if k.lower() not in hop_by_hop_headers}}
    
    # Add API key context to headers
    headers["X-API-Key-ID"] = str(api_key.id)
    headers["X-API-Key-Name"] = api_key.name
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=service_config["timeout"]
            )
            
        # Return response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={{k: v for k, v in response.headers.items() if k.lower() not in hop_by_hop_headers}}
        )
        
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Service timeout")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/metrics")
async def metrics():
    """Prometheus-style metrics endpoint."""
    # TODO: Implement proper Prometheus metrics
    metrics_data = []
    
    # Request count by service
    for service in SERVICES:
        count = redis_client.get(f"metrics:requests:{{service}}") or 0
        metrics_data.append(f"gateway_requests_total{{service=\\"{{service}}\\"}} {{count}}")
    
    # Rate limit hits
    rate_limit_hits = redis_client.get("metrics:rate_limit_hits") or 0
    metrics_data.append(f"gateway_rate_limit_hits_total {{rate_limit_hits}}")
    
    return Response("\n".join(metrics_data), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
''',
                "auth": {
                    "__init__.py": "",
                    "api_key_auth.py": '''"""API Key authentication."""
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.models import APIKey
from database.db import get_db

security = HTTPBearer()

async def get_current_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> APIKey:
    """Validate API key and return associated key object."""
    
    api_key = db.query(APIKey).filter(
        APIKey.key == credentials.credentials,
        APIKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
            headers={{"WWW-Authenticate": "Bearer"}},
        )
    
    # Update last used timestamp
    from datetime import datetime
    api_key.last_used_at = datetime.utcnow()
    db.commit()
    
    return api_key
''',
                },
                "middleware": {
                    "__init__.py": "",
                    "rate_limit.py": '''"""Rate limiting middleware."""
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import json
from typing import Callable

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client, default_limit: int = 100):
        super().__init__(app)
        self.redis_client = redis_client
        self.default_limit = default_limit
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract API key from Authorization header
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={{"detail": "Missing or invalid authorization header"}}
            )
        
        api_key = auth_header[7:]  # Remove "Bearer " prefix
        
        # Check rate limit
        current_time = int(time.time())
        window_start = current_time - (current_time % 60)  # 1-minute window
        
        key = f"rate_limit:{{api_key}}:{{window_start}}"
        current_requests = self.redis_client.incr(key)
        
        if current_requests == 1:
            # Set expiry for the window
            self.redis_client.expire(key, 60)
        
        # Get limit for this API key (default: 100 requests/minute)
        limit_key = f"api_key_limit:{{api_key}}"
        limit = int(self.redis_client.get(limit_key) or self.default_limit)
        
        if current_requests > limit:
            # Increment rate limit hit counter
            self.redis_client.incr("metrics:rate_limit_hits")
            
            return JSONResponse(
                status_code=429,
                content={{
                    "detail": "Rate limit exceeded",
                    "limit": limit,
                    "window": "1 minute",
                    "retry_after": 60 - (current_time % 60)
                }},
                headers={{
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": str(max(0, limit - current_requests)),
                    "X-RateLimit-Reset": str(window_start + 60),
                    "Retry-After": str(60 - (current_time % 60))
                }}
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current_requests))
        response.headers["X-RateLimit-Reset"] = str(window_start + 60)
        
        return response
''',
                    "logging.py": '''"""Request logging middleware."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-gateway")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        request_data = {{
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None
        }}
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        response_data = {{
            **request_data,
            "status_code": response.status_code,
            "process_time": round(process_time, 4)
        }}
        
        logger.info(f"{{request.method}} {{request.url.path}} - {{response.status_code}} - {{process_time:.4f}}s")
        
        # Add process time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
''',
                },
                "models": {
                    "__init__.py": "",
                    "api_key.py": '''"""API Key model."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime
from database.db import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    key = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=100)  # requests per minute
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, nullable=True)
    method = Column(String, nullable=False)
    path = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time = Column(Integer)  # milliseconds
    timestamp = Column(DateTime, default=datetime.utcnow)
    client_ip = Column(String)
    user_agent = Column(Text)
''',
                },
                "database": {
                    "__init__.py": "",
                    "db.py": '''"""Database configuration."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gateway.db")

engine = create_engine(DATABASE_URL, connect_args={{"check_same_thread": False}} if "sqlite" in DATABASE_URL else {{}})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
                },
                "requirements.txt": """fastapi>=0.109.0
uvicorn[standard]>=0.27.0
httpx>=0.25.0
redis>=5.0.0
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
prometheus-client>=0.19.0
""",
            },
            "docker-compose.yml": """version: '3.8'
services:
  gateway:
    build: ./src
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - DATABASE_URL=sqlite:///./gateway.db
      - SERVICE_API1_URL=http://api1:8001
      - SERVICE_API2_URL=http://api2:8002
    depends_on:
      - redis
    volumes:
      - ./src:/app

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  # Example backend services
  api1:
    image: nginx:alpine
    ports:
      - "8001:80"
    
  api2:
    image: nginx:alpine
    ports:
      - "8002:80"

volumes:
  redis_data:
""",
            ".env.example": """# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Database
DATABASE_URL=sqlite:///./gateway.db

# Backend Services
SERVICE_API1_URL=http://localhost:8001
SERVICE_API2_URL=http://localhost:8002

# Rate Limiting
DEFAULT_RATE_LIMIT=100
""",
            "README.md": "# {name} API Gateway\n\nCentralized API gateway with rate limiting, authentication, and monitoring.\n\n## Features\n\n- API key authentication\n- Rate limiting per key\n- Request/response logging\n- Health monitoring\n- Prometheus metrics\n- Service discovery\n- Auto-generated Swagger docs\n\n## Quick Start\n\n1. **Setup Environment**\n   ```bash\n   cp .env.example .env\n   ```\n\n2. **Run with Docker**\n   ```bash\n   docker-compose up --build\n   ```\n\n3. **Or run manually**\n   ```bash\n   pip install -r requirements.txt\n   python src/main.py\n   ```\n\n## API Usage\n\n1. **Create API Key** (via admin interface or database)\n2. **Make requests with Bearer token**:\n   ```bash\n   curl -H \"Authorization: Bearer your-api-key\" \\\n        http://localhost:8000/api/service1/endpoint\n   ```\n\n## Endpoints\n\n- `/` - Gateway info\n- `/health` - Health check\n- `/metrics` - Prometheus metrics\n- `/docs` - Swagger documentation\n- `/api/{service}/{path}` - Proxy to backend services\n\n## Configuration\n\n- Add services in `src/main.py` SERVICES dict\n- Set rate limits in Redis: `api_key_limit:{key}` = requests per minute\n- Configure service URLs in environment variables\n",
            ".gitignore": "venv/\n__pycache__/\n*.pyc\n*.db\n.env\n.env.local\nlogs/\n",
        },
    },
    "discord-bot": {
        "description": "Discord bot starter with discord.py",
        "structure": {
            ".planning": {
                "PROJECT.md": "# {name} Discord Bot\n\n## Vision\nFeature-rich Discord bot with commands, events, and modular design.\n\n## Tech Stack\n- discord.py\n- SQLite for data storage\n- Modular command system\n- Environment configuration\n\n## Goals\n- [ ] Basic bot setup\n- [ ] Command handler\n- [ ] Event system\n- [ ] Database integration\n- [ ] Custom commands\n",
                "ROADMAP.md": "# Discord Bot Roadmap\n\n## Phase 1: Foundation\n- [ ] Bot setup and authentication\n- [ ] Basic command structure\n- [ ] Event handlers\n\n## Phase 2: Features\n- [ ] Custom commands\n- [ ] Moderation tools\n- [ ] Database integration\n\n## Phase 3: Advanced\n- [ ] Web dashboard\n- [ ] API integration\n- [ ] Analytics\n",
                "STATE.md": "# State\n\n## Current Phase\nPhase 1: Foundation\n\n## Last Updated\n{date}\n\n## Bot Configuration\n- [ ] Discord token configured\n- [ ] Guild permissions set\n- [ ] Commands registered\n",
            },
            "src": {
                "__init__.py": "",
                "bot.py": '''"""
{name} Discord Bot
Main bot entry point and configuration.
"""
import discord
from discord.ext import commands
import os
import asyncio
import logging
from dotenv import load_dotenv

from handlers.commands import setup_commands
from handlers.events import setup_events
from database.db import init_db

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Enable if you need member events

bot = commands.Bot(
    command_prefix=os.getenv("BOT_PREFIX", "!"),
    intents=intents,
    description="{name} - A Discord bot built with discord.py",
    case_insensitive=True
)

@bot.event
async def on_ready():
    """Called when the bot is ready."""
    logger.info(f"{{bot.user}} has connected to Discord!")
    logger.info(f"Bot is in {{len(bot.guilds)}} guilds")
    
    # Initialize database
    await init_db()
    
    # Sync slash commands (for development)
    if os.getenv("SYNC_COMMANDS", "false").lower() == "true":
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synced {{len(synced)}} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {{e}}")

@bot.event
async def on_command_error(ctx, error):
    """Global error handler."""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: `{{error.param.name}}`")
        return
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
        return
    
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I don't have permission to do that.")
        return
    
    logger.error(f"Command error: {{error}}")
    await ctx.send("❌ An error occurred while processing the command.")

async def main():
    """Main function to run the bot."""
    # Setup commands and events
    await setup_commands(bot)
    await setup_events(bot)
    
    # Start the bot
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        return
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
    except Exception as e:
        logger.error(f"Bot error: {{e}}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
''',
                "handlers": {
                    "__init__.py": "",
                    "commands.py": '''"""Command handlers for the Discord bot."""
import discord
from discord.ext import commands
from typing import Optional

async def setup_commands(bot: commands.Bot):
    """Setup bot commands."""
    
    @bot.command(name="ping")
    async def ping(ctx):
        """Check bot latency."""
        latency = round(bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: {{latency}}ms",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @bot.command(name="info")
    async def info(ctx):
        """Show bot information."""
        embed = discord.Embed(
            title="🤖 Bot Information",
            description=f"{{bot.description}}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(bot.users), inline=True)
        embed.add_field(name="Prefix", value=bot.command_prefix, inline=True)
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        await ctx.send(embed=embed)
    
    @bot.command(name="help_custom")
    async def help_custom(ctx, *, command: Optional[str] = None):
        """Custom help command."""
        if command:
            # Help for specific command
            cmd = bot.get_command(command)
            if cmd:
                embed = discord.Embed(
                    title=f"Help: {{cmd.name}}",
                    description=cmd.help or "No description available",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Usage", value=f"`{{bot.command_prefix}}{{cmd.name}} {{cmd.signature}}`", inline=False)
            else:
                embed = discord.Embed(
                    title="❌ Command not found",
                    description=f"Command `{{command}}` does not exist.",
                    color=discord.Color.red()
                )
        else:
            # General help
            embed = discord.Embed(
                title="📚 Bot Commands",
                description="Here are all available commands:",
                color=discord.Color.blue()
            )
            
            for cmd in bot.commands:
                if not cmd.hidden:
                    embed.add_field(
                        name=f"`{{bot.command_prefix}}{{cmd.name}}`",
                        value=cmd.help or "No description",
                        inline=False
                    )
        
        await ctx.send(embed=embed)
    
    # Slash commands
    @bot.tree.command(name="ping", description="Check bot latency")
    async def ping_slash(interaction: discord.Interaction):
        latency = round(bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: {{latency}}ms",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="serverinfo", description="Show server information")
    async def serverinfo(interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🏰 {{guild.name}}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        await interaction.response.send_message(embed=embed)
''',
                    "events.py": '''"""Event handlers for the Discord bot."""
import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

async def setup_events(bot: commands.Bot):
    """Setup bot event handlers."""
    
    @bot.event
    async def on_guild_join(guild):
        """Called when the bot joins a new guild."""
        logger.info(f"Joined guild: {{guild.name}} ({{guild.id}})")
        
        # Find a channel to send a welcome message
        channel = None
        if guild.system_channel:
            channel = guild.system_channel
        elif guild.text_channels:
            # Find first channel bot can send messages to
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    channel = ch
                    break
        
        if channel:
            embed = discord.Embed(
                title="👋 Hello there!",
                description=f"Thanks for adding me to **{{guild.name}}**!\\n\\nUse `{{bot.command_prefix}}help` to see my commands.",
                color=discord.Color.green()
            )
            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                logger.warning(f"Could not send welcome message in {{guild.name}} - no permission")
    
    @bot.event
    async def on_guild_remove(guild):
        """Called when the bot leaves a guild."""
        logger.info(f"Left guild: {{guild.name}} ({{guild.id}})")
    
    @bot.event
    async def on_member_join(member):
        """Called when a member joins a guild."""
        logger.info(f"Member joined {{member.guild.name}}: {{member.name}}")
        
        # Example: Send welcome DM
        # try:
        #     embed = discord.Embed(
        #         title=f"Welcome to {{member.guild.name}}!",
        #         description="Welcome to the server! Feel free to introduce yourself.",
        #         color=discord.Color.green()
        #     )
        #     await member.send(embed=embed)
        # except discord.Forbidden:
        #     pass  # User has DMs disabled
    
    @bot.event
    async def on_member_remove(member):
        """Called when a member leaves a guild."""
        logger.info(f"Member left {{member.guild.name}}: {{member.name}}")
    
    @bot.event
    async def on_message(message):
        """Called when a message is sent."""
        # Don't respond to bots
        if message.author.bot:
            return
        
        # Example: Auto-react to messages containing certain keywords
        if "hello" in message.content.lower() and bot.user in message.mentions:
            await message.add_reaction("👋")
        
        # Process commands
        await bot.process_commands(message)
    
    @bot.event
    async def on_reaction_add(reaction, user):
        """Called when a reaction is added to a message."""
        if user.bot:
            return
        
        # Example: Role assignment with reactions
        # if reaction.message.id == ROLE_MESSAGE_ID:
        #     role_mapping = {
        #         "🎮": "Gamer",
        #         "🎵": "Music Lover",
        #     }
        #     if str(reaction.emoji) in role_mapping:
        #         role_name = role_mapping[str(reaction.emoji)]
        #         role = discord.utils.get(user.guild.roles, name=role_name)
        #         if role:
        #             await user.add_roles(role)
''',
                },
                "database": {
                    "__init__.py": "",
                    "db.py": '''"""Database configuration and models."""
import aiosqlite
import os
from typing import Optional

DATABASE_PATH = os.getenv("DATABASE_PATH", "bot.db")

async def init_db():
    """Initialize the database and create tables."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guilds (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                prefix TEXT DEFAULT '!',
                welcome_channel INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                discriminator TEXT NOT NULL,
                experience INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.commit()

async def get_guild_config(guild_id: int) -> Optional[dict]:
    """Get guild configuration."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM guilds WHERE id = ?", (guild_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def set_guild_config(guild_id: int, **kwargs):
    """Set guild configuration."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Insert or update
        await db.execute("""
            INSERT OR REPLACE INTO guilds (id, name, prefix, welcome_channel)
            VALUES (?, ?, ?, ?)
        """, (
            guild_id,
            kwargs.get('name'),
            kwargs.get('prefix', '!'),
            kwargs.get('welcome_channel')
        ))
        await db.commit()

async def get_user_data(user_id: int) -> Optional[dict]:
    """Get user data."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def update_user_data(user_id: int, **kwargs):
    """Update user data."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO users (id, username, discriminator, experience, level)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            kwargs.get('username'),
            kwargs.get('discriminator'),
            kwargs.get('experience', 0),
            kwargs.get('level', 1)
        ))
        await db.commit()
''',
                },
                "utils": {
                    "__init__.py": "",
                    "helpers.py": '''"""Utility functions and helpers."""
import discord
from typing import Optional, Union

def format_user(user: Union[discord.User, discord.Member]) -> str:
    """Format user for display."""
    return f"{{user.name}}#{{{user.discriminator}}}"

def create_embed(
    title: str = None,
    description: str = None,
    color: discord.Color = discord.Color.blue(),
    **kwargs
) -> discord.Embed:
    """Create a standardized embed."""
    embed = discord.Embed(title=title, description=description, color=color)
    
    for key, value in kwargs.items():
        if key.startswith("field_"):
            # Add field: field_name="value"
            field_name = key[6:].replace("_", " ").title()
            embed.add_field(name=field_name, value=value, inline=True)
    
    return embed

async def safe_send(
    channel: discord.TextChannel,
    content: str = None,
    embed: discord.Embed = None
) -> Optional[discord.Message]:
    """Safely send a message to a channel."""
    try:
        return await channel.send(content=content, embed=embed)
    except discord.Forbidden:
        print(f"No permission to send message in {{channel.name}}")
        return None
    except discord.HTTPException as e:
        print(f"HTTP error sending message: {{e}}")
        return None

def has_permissions(member: discord.Member, **permissions) -> bool:
    """Check if a member has specific permissions."""
    return all(
        getattr(member.guild_permissions, perm, False) == value
        for perm, value in permissions.items()
    )
''',
                },
                "requirements.txt": """discord.py>=2.3.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
""",
            },
            ".env.example": """# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
BOT_PREFIX=!
SYNC_COMMANDS=false

# Database
DATABASE_PATH=bot.db

# Logging
LOG_LEVEL=INFO
""",
            "README.md": "# {name} Discord Bot\n\nA feature-rich Discord bot built with discord.py.\n\n## Features\n\n- Prefix and slash commands\n- Event handling\n- Database integration\n- Modular design\n- Error handling\n- Configurable per-guild settings\n\n## Setup\n\n1. **Create Discord Application**\n   - Go to https://discord.com/developers/applications\n   - Create new application\n   - Go to Bot section and create bot\n   - Copy the token\n\n2. **Configure Environment**\n   ```bash\n   cp .env.example .env\n   # Edit .env and add your bot token\n   ```\n\n3. **Install Dependencies**\n   ```bash\n   pip install -r requirements.txt\n   ```\n\n4. **Run the Bot**\n   ```bash\n   python src/bot.py\n   ```\n\n## Bot Permissions\n\nInvite URL (replace CLIENT_ID with your application ID):\n```\nhttps://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=8&scope=bot%20applications.commands\n```\n\n## Commands\n\n### Prefix Commands\n- `!ping` - Check bot latency\n- `!info` - Show bot information\n- `!help_custom` - Show command help\n\n### Slash Commands\n- `/ping` - Check bot latency\n- `/serverinfo` - Show server information\n\n## Adding Commands\n\n1. **Prefix Commands**: Add to `src/handlers/commands.py`\n2. **Slash Commands**: Use `@bot.tree.command()` decorator\n3. **Events**: Add to `src/handlers/events.py`\n\n## Database\n\nThe bot uses SQLite for data storage. Tables:\n- `guilds` - Server-specific configuration\n- `users` - User data and statistics\n\n## Development\n\n- Set `SYNC_COMMANDS=true` in .env to sync slash commands on startup\n- Check logs for debugging information\n- Use Discord Developer Portal to test permissions\n",
            ".gitignore": "venv/\n__pycache__/\n*.pyc\n.env\n.env.local\n*.db\nlogs/\n*.log\n",
        },
    },
    "data-pipeline": {
        "description": "Data processing pipeline with validation and error handling",
        "structure": {
            ".planning": {
                "PROJECT.md": "# {name} Data Pipeline\n\n## Vision\nRobust data processing pipeline with input/output handlers, validation, and error recovery.\n\n## Tech Stack\n- Python with asyncio\n- Pandas for data processing\n- Pydantic for validation\n- Redis for caching\n- SQLite/PostgreSQL for storage\n\n## Goals\n- [ ] Input/output adapters\n- [ ] Data transformation pipeline\n- [ ] Validation with schemas\n- [ ] Error handling and retry logic\n- [ ] Monitoring and logging\n",
                "ROADMAP.md": "# Data Pipeline Roadmap\n\n## Phase 1: Core Pipeline\n- [ ] Input/output handlers\n- [ ] Basic transformation\n- [ ] Error handling\n\n## Phase 2: Advanced Features\n- [ ] Parallel processing\n- [ ] Data validation schemas\n- [ ] Retry mechanisms\n\n## Phase 3: Monitoring\n- [ ] Pipeline metrics\n- [ ] Alerting\n- [ ] Dashboard\n",
                "STATE.md": "# State\n\n## Current Phase\nPhase 1: Core Pipeline\n\n## Last Updated\n{date}\n\n## Data Sources\n- [ ] Source 1: Description\n- [ ] Source 2: Description\n\n## Processing Status\n- Last successful run: TBD\n- Errors in last 24h: TBD\n",
            },
            "src": {
                "__init__.py": "",
                "pipeline.py": '''"""
{name} Data Pipeline
Main pipeline orchestration and configuration.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from .processors import DataProcessor
from .handlers.input_handler import InputHandler
from .handlers.output_handler import OutputHandler
from .validation import DataValidator
from .monitoring import PipelineMonitor
from .config import PipelineConfig

logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    COMPLETED = "completed"

@dataclass
class PipelineResult:
    status: PipelineStatus
    processed_count: int
    error_count: int
    start_time: datetime
    end_time: datetime
    errors: List[str]

class DataPipeline:
    """Main data pipeline orchestrator."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.input_handler = InputHandler(config.input_config)
        self.output_handler = OutputHandler(config.output_config)
        self.processor = DataProcessor(config.processing_config)
        self.validator = DataValidator(config.validation_config)
        self.monitor = PipelineMonitor(config.monitoring_config)
        
        self.status = PipelineStatus.IDLE
        self._stop_requested = False
    
    async def run(self) -> PipelineResult:
        """Run the complete pipeline."""
        start_time = datetime.now()
        processed_count = 0
        error_count = 0
        errors = []
        
        try:
            self.status = PipelineStatus.RUNNING
            logger.info("Starting data pipeline")
            
            # Initialize components
            await self.monitor.pipeline_started()
            
            # Process data in batches
            async for batch in self.input_handler.read_batches():
                if self._stop_requested:
                    logger.info("Pipeline stop requested")
                    break
                
                try:
                    # Validate input data
                    validated_batch = await self.validator.validate_input(batch)
                    
                    # Process data
                    processed_batch = await self.processor.process(validated_batch)
                    
                    # Validate output data
                    validated_output = await self.validator.validate_output(processed_batch)
                    
                    # Write output
                    await self.output_handler.write(validated_output)
                    
                    processed_count += len(batch)
                    await self.monitor.batch_processed(len(batch))
                    
                    logger.info(f"Processed batch of {{len(batch)}} records")
                    
                except Exception as e:
                    error_count += len(batch)
                    error_msg = f"Error processing batch: {{str(e)}}"
                    errors.append(error_msg)
                    logger.error(error_msg, exc_info=True)
                    
                    await self.monitor.batch_failed(len(batch), str(e))
                    
                    # Decide whether to continue or fail
                    if not self.config.continue_on_error:
                        break
            
            self.status = PipelineStatus.COMPLETED if error_count == 0 else PipelineStatus.ERROR
            
        except Exception as e:
            self.status = PipelineStatus.ERROR
            error_msg = f"Pipeline failed: {{str(e)}}"
            errors.append(error_msg)
            logger.error(error_msg, exc_info=True)
            
        finally:
            end_time = datetime.now()
            
            # Cleanup
            await self.input_handler.close()
            await self.output_handler.close()
            await self.monitor.pipeline_completed(
                processed_count, error_count, end_time - start_time
            )
            
            logger.info(f"Pipeline completed. Processed: {{processed_count}}, Errors: {{error_count}}")
        
        return PipelineResult(
            status=self.status,
            processed_count=processed_count,
            error_count=error_count,
            start_time=start_time,
            end_time=end_time,
            errors=errors
        )
    
    async def stop(self):
        """Request pipeline to stop gracefully."""
        logger.info("Stopping pipeline...")
        self._stop_requested = True
    
    async def health_check(self) -> Dict[str, Any]:
        """Check pipeline component health."""
        return {{
            "status": self.status.value,
            "input_handler": await self.input_handler.health_check(),
            "output_handler": await self.output_handler.health_check(),
            "processor": await self.processor.health_check(),
            "validator": self.validator.health_check(),
            "monitor": await self.monitor.health_check()
        }}

async def main():
    """Main entry point for running the pipeline."""
    import os
    from .config import load_config
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Load configuration
    config_path = os.getenv("PIPELINE_CONFIG", "config.yaml")
    config = load_config(config_path)
    
    # Create and run pipeline
    pipeline = DataPipeline(config)
    result = await pipeline.run()
    
    print(f"Pipeline completed with status: {{result.status.value}}")
    print(f"Processed {{result.processed_count}} records with {{result.error_count}} errors")
    
    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"  - {{error}}")

if __name__ == "__main__":
    asyncio.run(main())
''',
                "processors": {
                    "__init__.py": "",
                    "data_processor.py": '''"""Data processing logic."""
import pandas as pd
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class DataProcessor:
    """Main data processor with transformation logic."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.transformations = []
        self._setup_transformations()
    
    def _setup_transformations(self):
        """Setup transformation functions based on config."""
        transform_config = self.config.get("transformations", [])
        
        for transform in transform_config:
            if transform["type"] == "clean_nulls":
                self.transformations.append(self._clean_nulls)
            elif transform["type"] == "normalize_dates":
                self.transformations.append(self._normalize_dates)
            elif transform["type"] == "custom":
                # Load custom transformation
                pass
    
    async def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of data."""
        logger.debug(f"Processing {{len(data)}} records")
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(data)
        
        # Apply transformations
        for transform_func in self.transformations:
            df = await transform_func(df)
        
        # Convert back to dict format
        return df.to_dict("records")
    
    async def _clean_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove or fill null values."""
        null_strategy = self.config.get("null_strategy", "drop")
        
        if null_strategy == "drop":
            return df.dropna()
        elif null_strategy == "fill":
            fill_value = self.config.get("fill_value", 0)
            return df.fillna(fill_value)
        else:
            return df
    
    async def _normalize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize date columns to ISO format."""
        date_columns = self.config.get("date_columns", [])
        
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    logger.warning(f"Failed to normalize date column {{col}}: {{e}}")
        
        return df
    
    async def health_check(self) -> Dict[str, Any]:
        """Check processor health."""
        return {{
            "status": "healthy",
            "transformations_loaded": len(self.transformations),
            "config": self.config
        }}

class BatchProcessor:
    """Process data in parallel batches."""
    
    def __init__(self, processor: DataProcessor, batch_size: int = 1000, max_workers: int = 4):
        self.processor = processor
        self.batch_size = batch_size
        self.max_workers = max_workers
    
    async def process_parallel(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process data in parallel batches."""
        batches = [data[i:i + self.batch_size] for i in range(0, len(data), self.batch_size)]
        
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def process_batch(batch):
            async with semaphore:
                return await self.processor.process(batch)
        
        tasks = [process_batch(batch) for batch in batches]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results and handle exceptions
        combined_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch processing error: {{result}}")
                raise result
            combined_results.extend(result)
        
        return combined_results
''',
                },
                "handlers": {
                    "__init__.py": "",
                    "input_handler.py": '''"""Input data handlers for various sources."""
import asyncio
import aiofiles
import json
import csv
import logging
from typing import Dict, Any, List, AsyncGenerator
from pathlib import Path
import aiohttp

logger = logging.getLogger(__name__)

class InputHandler:
    """Handle input from various data sources."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_type = config.get("type", "file")
        self.batch_size = config.get("batch_size", 1000)
        self._session = None
    
    async def read_batches(self) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """Read data in batches."""
        if self.source_type == "file":
            async for batch in self._read_file_batches():
                yield batch
        elif self.source_type == "api":
            async for batch in self._read_api_batches():
                yield batch
        elif self.source_type == "database":
            async for batch in self._read_database_batches():
                yield batch
        else:
            raise ValueError(f"Unsupported source type: {{self.source_type}}")
    
    async def _read_file_batches(self) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """Read from file sources."""
        file_path = Path(self.config["path"])
        
        if file_path.suffix.lower() == ".json":
            async for batch in self._read_json_batches(file_path):
                yield batch
        elif file_path.suffix.lower() == ".csv":
            async for batch in self._read_csv_batches(file_path):
                yield batch
        else:
            raise ValueError(f"Unsupported file type: {{file_path.suffix}}")
    
    async def _read_json_batches(self, file_path: Path) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """Read JSON file in batches."""
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            data = json.loads(content)
            
            # Handle different JSON structures
            if isinstance(data, list):
                for i in range(0, len(data), self.batch_size):
                    yield data[i:i + self.batch_size]
            elif isinstance(data, dict) and "data" in data:
                # Assume data is in a 'data' field
                data_list = data["data"]
                for i in range(0, len(data_list), self.batch_size):
                    yield data_list[i:i + self.batch_size]
            else:
                # Single object
                yield [data]
    
    async def _read_csv_batches(self, file_path: Path) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """Read CSV file in batches."""
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            reader = csv.DictReader(content.splitlines())
            
            batch = []
            for row in reader:
                batch.append(row)
                if len(batch) >= self.batch_size:
                    yield batch
                    batch = []
            
            if batch:
                yield batch
    
    async def _read_api_batches(self) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """Read from API sources."""
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        url = self.config["url"]
        headers = self.config.get("headers", {{}})
        params = self.config.get("params", {{}})
        
        # Handle pagination
        page = 1
        while True:
            params["page"] = page
            params["limit"] = self.batch_size
            
            try:
                async with self._session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        logger.error(f"API request failed with status {{response.status}}")
                        break
                    
                    data = await response.json()
                    
                    # Extract data based on API structure
                    if isinstance(data, list):
                        items = data
                    elif "data" in data:
                        items = data["data"]
                    elif "items" in data:
                        items = data["items"]
                    else:
                        items = [data]
                    
                    if not items:
                        break
                    
                    yield items
                    page += 1
                    
            except Exception as e:
                logger.error(f"Error reading from API: {{e}}")
                break
    
    async def _read_database_batches(self) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """Read from database sources."""
        # TODO: Implement database reading
        # This would use aiopg, aiomysql, or similar async database drivers
        raise NotImplementedError("Database input not yet implemented")
    
    async def close(self):
        """Close input handler resources."""
        if self._session:
            await self._session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check input handler health."""
        return {{
            "status": "healthy",
            "source_type": self.source_type,
            "config": self.config
        }}
''',
                    "output_handler.py": '''"""Output data handlers for various destinations."""
import asyncio
import aiofiles
import json
import csv
import logging
from typing import Dict, Any, List
from pathlib import Path
import aiohttp

logger = logging.getLogger(__name__)

class OutputHandler:
    """Handle output to various destinations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.destination_type = config.get("type", "file")
        self._session = None
        self._buffer = []
        self._buffer_size = config.get("buffer_size", 1000)
    
    async def write(self, data: List[Dict[str, Any]]):
        """Write data to destination."""
        self._buffer.extend(data)
        
        if len(self._buffer) >= self._buffer_size:
            await self._flush()
    
    async def _flush(self):
        """Flush buffered data to destination."""
        if not self._buffer:
            return
        
        if self.destination_type == "file":
            await self._write_to_file(self._buffer)
        elif self.destination_type == "api":
            await self._write_to_api(self._buffer)
        elif self.destination_type == "database":
            await self._write_to_database(self._buffer)
        else:
            raise ValueError(f"Unsupported destination type: {{self.destination_type}}")
        
        logger.info(f"Flushed {{len(self._buffer)}} records to {{self.destination_type}}")
        self._buffer.clear()
    
    async def _write_to_file(self, data: List[Dict[str, Any]]):
        """Write to file destination."""
        file_path = Path(self.config["path"])
        file_format = self.config.get("format", "json")
        
        if file_format == "json":
            await self._write_json(file_path, data)
        elif file_format == "csv":
            await self._write_csv(file_path, data)
        else:
            raise ValueError(f"Unsupported file format: {{file_format}}")
    
    async def _write_json(self, file_path: Path, data: List[Dict[str, Any]]):
        """Write data as JSON."""
        mode = "w" if not file_path.exists() else "a"
        
        async with aiofiles.open(file_path, mode) as f:
            if mode == "a":
                await f.write("\\n")
            
            for record in data:
                await f.write(json.dumps(record) + "\\n")
    
    async def _write_csv(self, file_path: Path, data: List[Dict[str, Any]]):
        """Write data as CSV."""
        if not data:
            return
        
        file_exists = file_path.exists()
        
        async with aiofiles.open(file_path, "a") as f:
            fieldnames = data[0].keys()
            
            # Write header if file is new
            if not file_exists:
                await f.write(",".join(fieldnames) + "\\n")
            
            # Write data rows
            for record in data:
                row = ",".join(str(record.get(field, "")) for field in fieldnames)
                await f.write(row + "\\n")
    
    async def _write_to_api(self, data: List[Dict[str, Any]]):
        """Write to API destination."""
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        url = self.config["url"]
        headers = self.config.get("headers", {{}})
        
        try:
            async with self._session.post(url, json=data, headers=headers) as response:
                if response.status not in (200, 201):
                    error_text = await response.text()
                    raise Exception(f"API write failed with status {{response.status}}: {{error_text}}")
                    
        except Exception as e:
            logger.error(f"Error writing to API: {{e}}")
            raise
    
    async def _write_to_database(self, data: List[Dict[str, Any]]):
        """Write to database destination."""
        # TODO: Implement database writing
        raise NotImplementedError("Database output not yet implemented")
    
    async def close(self):
        """Close output handler and flush remaining data."""
        await self._flush()
        
        if self._session:
            await self._session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check output handler health."""
        return {{
            "status": "healthy",
            "destination_type": self.destination_type,
            "buffer_size": len(self._buffer),
            "config": self.config
        }}
''',
                },
                "validation": {
                    "__init__.py": "",
                    "data_validator.py": '''"""Data validation using Pydantic schemas."""
from pydantic import BaseModel, ValidationError
from typing import Dict, Any, List, Optional, Type
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Validate data using Pydantic models."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.input_schema = self._create_schema(config.get("input_schema"))
        self.output_schema = self._create_schema(config.get("output_schema"))
        self.strict_validation = config.get("strict_validation", True)
    
    def _create_schema(self, schema_config: Optional[Dict[str, Any]]) -> Optional[Type[BaseModel]]:
        """Dynamically create Pydantic schema from config."""
        if not schema_config:
            return None
        
        # Create dynamic Pydantic model
        fields = {{}}
        for field_name, field_config in schema_config.get("fields", {{}}).items():
            field_type = self._get_field_type(field_config.get("type", "str"))
            field_required = field_config.get("required", True)
            
            if field_required:
                fields[field_name] = (field_type, ...)
            else:
                fields[field_name] = (Optional[field_type], None)
        
        return type(
            schema_config.get("name", "DynamicSchema"),
            (BaseModel,),
            {{"__annotations__": fields}}
        )
    
    def _get_field_type(self, type_str: str):
        """Convert string type to Python type."""
        type_mapping = {{
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict
        }}
        return type_mapping.get(type_str, str)
    
    async def validate_input(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate input data."""
        if not self.input_schema:
            return data
        
        validated_data = []
        errors = []
        
        for i, record in enumerate(data):
            try:
                validated_record = self.input_schema(**record)
                validated_data.append(validated_record.dict())
            except ValidationError as e:
                error_msg = f"Input validation error at record {{i}}: {{e}}"
                errors.append(error_msg)
                logger.warning(error_msg)
                
                if self.strict_validation:
                    raise ValueError(f"Input validation failed: {{error_msg}}")
        
        if errors and not self.strict_validation:
            logger.warning(f"Input validation completed with {{len(errors)}} errors")
        
        return validated_data
    
    async def validate_output(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate output data."""
        if not self.output_schema:
            return data
        
        validated_data = []
        errors = []
        
        for i, record in enumerate(data):
            try:
                validated_record = self.output_schema(**record)
                validated_data.append(validated_record.dict())
            except ValidationError as e:
                error_msg = f"Output validation error at record {{i}}: {{e}}"
                errors.append(error_msg)
                logger.warning(error_msg)
                
                if self.strict_validation:
                    raise ValueError(f"Output validation failed: {{error_msg}}")
        
        if errors and not self.strict_validation:
            logger.warning(f"Output validation completed with {{len(errors)}} errors")
        
        return validated_data
    
    def health_check(self) -> Dict[str, Any]:
        """Check validator health."""
        return {{
            "status": "healthy",
            "input_schema": self.input_schema.__name__ if self.input_schema else None,
            "output_schema": self.output_schema.__name__ if self.output_schema else None,
            "strict_validation": self.strict_validation
        }}
''',
                },
                "monitoring": {
                    "__init__.py": "",
                    "pipeline_monitor.py": '''"""Pipeline monitoring and metrics collection."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class PipelineMonitor:
    """Monitor pipeline execution and collect metrics."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = {{
            "pipeline_runs": 0,
            "total_processed": 0,
            "total_errors": 0,
            "avg_processing_time": 0,
            "last_run": None,
            "last_error": None
        }}
        self.metrics_file = Path(config.get("metrics_file", "pipeline_metrics.json"))
        self._load_metrics()
    
    def _load_metrics(self):
        """Load metrics from file."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    saved_metrics = json.load(f)
                    self.metrics.update(saved_metrics)
            except Exception as e:
                logger.warning(f"Could not load metrics: {{e}}")
    
    def _save_metrics(self):
        """Save metrics to file."""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save metrics: {{e}}")
    
    async def pipeline_started(self):
        """Called when pipeline starts."""
        self.metrics["pipeline_runs"] += 1
        self.metrics["last_run"] = datetime.now()
        logger.info(f"Pipeline started (run #{{self.metrics['pipeline_runs']}})")
        self._save_metrics()
    
    async def batch_processed(self, batch_size: int):
        """Called when a batch is successfully processed."""
        self.metrics["total_processed"] += batch_size
        logger.debug(f"Batch processed: {{batch_size}} records")
    
    async def batch_failed(self, batch_size: int, error: str):
        """Called when a batch fails."""
        self.metrics["total_errors"] += batch_size
        self.metrics["last_error"] = {{
            "timestamp": datetime.now(),
            "error": error,
            "batch_size": batch_size
        }}
        logger.error(f"Batch failed: {{batch_size}} records - {{error}}")
    
    async def pipeline_completed(self, processed_count: int, error_count: int, duration: timedelta):
        """Called when pipeline completes."""
        # Update average processing time
        total_runs = self.metrics["pipeline_runs"]
        current_avg = self.metrics["avg_processing_time"]
        new_duration_seconds = duration.total_seconds()
        
        self.metrics["avg_processing_time"] = (
            (current_avg * (total_runs - 1) + new_duration_seconds) / total_runs
        )
        
        logger.info(f"Pipeline completed in {{duration}}. Processed: {{processed_count}}, Errors: {{error_count}}")
        self._save_metrics()
        
        # Send alerts if configured
        if self.config.get("alerts_enabled") and error_count > 0:
            await self._send_alert(f"Pipeline completed with {{error_count}} errors")
    
    async def _send_alert(self, message: str):
        """Send alert notification."""
        alert_config = self.config.get("alerts", {{}})
        alert_type = alert_config.get("type", "log")
        
        if alert_type == "log":
            logger.warning(f"ALERT: {{message}}")
        elif alert_type == "email":
            # TODO: Implement email alerts
            logger.info(f"Email alert would be sent: {{message}}")
        elif alert_type == "webhook":
            # TODO: Implement webhook alerts
            logger.info(f"Webhook alert would be sent: {{message}}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check monitor health."""
        return {{
            "status": "healthy",
            "metrics_file": str(self.metrics_file),
            "last_run": self.metrics.get("last_run"),
            "total_runs": self.metrics["pipeline_runs"]
        }}

class MetricCollector:
    """Collect detailed pipeline metrics."""
    
    def __init__(self):
        self.start_time = None
        self.batch_times = []
        self.error_log = []
    
    def start_timing(self):
        """Start timing a pipeline run."""
        self.start_time = datetime.now()
    
    def record_batch_time(self, batch_size: int, processing_time: float):
        """Record batch processing time."""
        self.batch_times.append({{
            "timestamp": datetime.now(),
            "batch_size": batch_size,
            "processing_time": processing_time,
            "records_per_second": batch_size / processing_time if processing_time > 0 else 0
        }})
    
    def record_error(self, error: str, context: Dict[str, Any] = None):
        """Record an error."""
        self.error_log.append({{
            "timestamp": datetime.now(),
            "error": error,
            "context": context or {{}}
        }})
    
    def get_summary(self) -> Dict[str, Any]:
        """Get processing summary."""
        if not self.start_time:
            return {{"error": "Timing not started"}}
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        total_records = sum(batch["batch_size"] for batch in self.batch_times)
        
        return {{
            "total_time": total_time,
            "total_records": total_records,
            "total_batches": len(self.batch_times),
            "total_errors": len(self.error_log),
            "records_per_second": total_records / total_time if total_time > 0 else 0,
            "avg_batch_time": sum(b["processing_time"] for b in self.batch_times) / len(self.batch_times) if self.batch_times else 0
        }}
''',
                },
                "config": {
                    "__init__.py": "",
                    "pipeline_config.py": '''"""Pipeline configuration management."""
import yaml
import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class PipelineConfig:
    """Main pipeline configuration."""
    input_config: Dict[str, Any]
    output_config: Dict[str, Any]
    processing_config: Dict[str, Any]
    validation_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    continue_on_error: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0

def load_config(config_path: str) -> PipelineConfig:
    """Load pipeline configuration from YAML file."""
    if not os.path.exists(config_path):
        # Return default configuration
        return create_default_config()
    
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    return PipelineConfig(
        input_config=config_data.get("input", {{}}),
        output_config=config_data.get("output", {{}}),
        processing_config=config_data.get("processing", {{}}),
        validation_config=config_data.get("validation", {{}}),
        monitoring_config=config_data.get("monitoring", {{}}),
        continue_on_error=config_data.get("continue_on_error", True),
        max_retries=config_data.get("max_retries", 3),
        retry_delay=config_data.get("retry_delay", 1.0)
    )

def create_default_config() -> PipelineConfig:
    """Create default pipeline configuration."""
    return PipelineConfig(
        input_config={{
            "type": "file",
            "path": "input/data.json",
            "batch_size": 1000
        }},
        output_config={{
            "type": "file",
            "path": "output/processed_data.json",
            "format": "json",
            "buffer_size": 1000
        }},
        processing_config={{
            "transformations": [
                {{"type": "clean_nulls"}},
                {{"type": "normalize_dates"}}
            ],
            "null_strategy": "drop",
            "date_columns": []
        }},
        validation_config={{
            "strict_validation": False,
            "input_schema": None,
            "output_schema": None
        }},
        monitoring_config={{
            "metrics_file": "pipeline_metrics.json",
            "alerts_enabled": False
        }}
    )

def save_config(config: PipelineConfig, config_path: str):
    """Save pipeline configuration to YAML file."""
    config_dict = {{
        "input": config.input_config,
        "output": config.output_config,
        "processing": config.processing_config,
        "validation": config.validation_config,
        "monitoring": config.monitoring_config,
        "continue_on_error": config.continue_on_error,
        "max_retries": config.max_retries,
        "retry_delay": config.retry_delay
    }}
    
    with open(config_path, 'w') as f:
        yaml.dump(config_dict, f, indent=2)
''',
                },
                "requirements.txt": """pandas>=2.0.0
pydantic>=2.0.0
aiofiles>=23.0.0
aiohttp>=3.8.0
PyYAML>=6.0.0
asyncio
""",
            },
            "config.yaml": """# {name} Data Pipeline Configuration

input:
  type: file  # file, api, database
  path: "input/sample_data.json"
  batch_size: 1000

output:
  type: file  # file, api, database
  path: "output/processed_data.json"
  format: json  # json, csv
  buffer_size: 1000

processing:
  transformations:
    - type: clean_nulls
    - type: normalize_dates
  null_strategy: drop  # drop, fill
  fill_value: 0
  date_columns: ["created_at", "updated_at"]

validation:
  strict_validation: false
  input_schema:
    name: "InputRecord"
    fields:
      id:
        type: int
        required: true
      name:
        type: str
        required: true
      email:
        type: str
        required: false
  output_schema:
    name: "OutputRecord"
    fields:
      id:
        type: int
        required: true
      processed_name:
        type: str
        required: true
      email:
        type: str
        required: false

monitoring:
  metrics_file: "pipeline_metrics.json"
  alerts_enabled: false
  alerts:
    type: log  # log, email, webhook

# Pipeline settings
continue_on_error: true
max_retries: 3
retry_delay: 1.0
""",
            "input/sample_data.json": """[
  {"id": 1, "name": "John Doe", "email": "john@example.com", "created_at": "2024-01-01"},
  {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "created_at": "2024-01-02"},
  {"id": 3, "name": "Bob Johnson", "email": null, "created_at": "2024-01-03"}
]
""",
            "README.md": "# {name} Data Pipeline\n\nRobust data processing pipeline with validation, error handling, and monitoring.\n\n## Features\n\n- Input/output adapters for files, APIs, and databases\n- Data transformation with pandas\n- Pydantic-based validation\n- Error handling with retry logic\n- Pipeline monitoring and metrics\n- Configurable via YAML\n- Async processing for performance\n\n## Quick Start\n\n1. **Install Dependencies**\n   ```bash\n   pip install -r requirements.txt\n   ```\n\n2. **Configure Pipeline**\n   ```bash\n   # Edit config.yaml to match your data sources\n   cp config.yaml my_config.yaml\n   ```\n\n3. **Run Pipeline**\n   ```bash\n   python src/pipeline.py\n   # Or with custom config:\n   PIPELINE_CONFIG=my_config.yaml python src/pipeline.py\n   ```\n\n## Configuration\n\nThe pipeline is configured via `config.yaml`:\n\n### Input Sources\n- **File**: JSON, CSV files\n- **API**: REST APIs with pagination\n- **Database**: PostgreSQL, MySQL (coming soon)\n\n### Output Destinations\n- **File**: JSON, CSV files\n- **API**: REST API endpoints\n- **Database**: PostgreSQL, MySQL (coming soon)\n\n### Processing\n- Data cleaning (nulls, duplicates)\n- Date normalization\n- Custom transformations\n- Parallel batch processing\n\n### Validation\n- Input/output schema validation\n- Pydantic model validation\n- Strict or lenient modes\n\n### Monitoring\n- Metrics collection\n- Error tracking\n- Performance monitoring\n- Alert notifications\n\n## Example Usage\n\n```python\nfrom src.pipeline import DataPipeline\nfrom src.config import load_config\n\n# Load configuration\nconfig = load_config(\"config.yaml\")\n\n# Create and run pipeline\npipeline = DataPipeline(config)\nresult = await pipeline.run()\n\nprint(f\"Processed {{result.processed_count}} records\")\n```\n\n## Extending the Pipeline\n\n1. **Add new input sources**: Extend `InputHandler`\n2. **Add transformations**: Add to `DataProcessor`\n3. **Add validation rules**: Create Pydantic models\n4. **Add monitoring**: Extend `PipelineMonitor`\n\n## Error Handling\n\n- Configurable retry logic\n- Continue on error option\n- Detailed error logging\n- Graceful degradation\n\n## Performance\n\n- Async I/O for better performance\n- Batch processing\n- Parallel transformation\n- Memory-efficient streaming\n",
            ".gitignore": "venv/\n__pycache__/\n*.pyc\n.env\n.env.local\npipeline_metrics.json\noutput/\n*.log\n",
        },
    },
    "saas": {
        "description": "SaaS starter: auth, billing (Stripe), dashboard, admin, landing page",
        "structure": {
            ".planning": {
                "PROJECT.md": "# {name} SaaS\n\n## Vision\nModern SaaS application with authentication, billing, and admin dashboard.\n\n## Tech Stack\n- Next.js 14 (Frontend)\n- FastAPI (Backend API)\n- Stripe (Billing)\n- Tailwind CSS (Styling)\n- PostgreSQL (Database)\n\n## Goals\n- [ ] User authentication\n- [ ] Subscription billing\n- [ ] Admin dashboard\n- [ ] Landing page\n- [ ] User dashboard\n",
                "ROADMAP.md": "# {name} SaaS Roadmap\n\n## Phase 1: Foundation\n- [ ] Authentication system\n- [ ] Database setup\n- [ ] Basic API endpoints\n\n## Phase 2: Billing\n- [ ] Stripe integration\n- [ ] Subscription plans\n- [ ] Payment flows\n\n## Phase 3: Dashboard\n- [ ] User dashboard\n- [ ] Admin panel\n- [ ] Analytics\n\n## Phase 4: Marketing\n- [ ] Landing page\n- [ ] Pricing page\n- [ ] Email campaigns\n",
                "STATE.md": "# {name} SaaS State\n\n## Current Phase\nPhase 1: Foundation\n\n## Last Updated\n{date}\n\n## Tech Decisions\n- Auth: NextAuth.js\n- Payments: Stripe\n- Database: PostgreSQL\n- Deployment: Vercel + Railway\n",
            },
            "backend": {
                "main.py": '''"""
{name} SaaS API
FastAPI backend with authentication and Stripe billing.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import stripe
import os
from datetime import datetime, timedelta
import jwt

app = FastAPI(
    title="{name} SaaS API",
    description="SaaS backend with auth and billing",
    version="1.0.0"
)

# Environment variables
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
stripe.api_key = STRIPE_SECRET_KEY

security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.get("/")
async def root():
    return {{"message": "Welcome to {name} SaaS API"}}


@app.get("/health")
async def health():
    return {{"status": "healthy"}}


@app.post("/auth/login")
async def login(email: str, password: str):
    # TODO: Validate credentials against database
    token = jwt.encode(
        {{"email": email, "exp": datetime.utcnow() + timedelta(days=7)}},
        JWT_SECRET,
        algorithm="HS256"
    )
    return {{"access_token": token, "token_type": "bearer"}}


@app.get("/auth/me")
async def get_current_user(user = Depends(verify_token)):
    return user


@app.post("/billing/create-checkout-session")
async def create_checkout_session(price_id: str, user = Depends(verify_token)):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{{"price": price_id, "quantity": 1}}],
            mode="subscription",
            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/pricing",
        )
        return {{"checkout_url": checkout_session.url}}
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
''',
                "requirements.txt": """fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
pydantic>=2.5.0
stripe>=7.0.0
pyjwt>=2.8.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
""",
                ".env.example": """# Database
DATABASE_URL=postgresql://user:password@localhost/saas_db

# JWT Secret
JWT_SECRET=your-super-secret-jwt-key

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# App
APP_URL=http://localhost:3000
""",
            },
            "frontend": {
                "package.json": """{
  "name": "{name_lower}-saas",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "next-auth": "5.0.0-beta.13",
    "@stripe/stripe-js": "2.4.0",
    "stripe": "14.15.0",
    "tailwindcss": "3.4.1",
    "typescript": "5.3.3",
    "lucide-react": "0.316.0"
  },
  "devDependencies": {
    "@types/node": "20.10.0",
    "@types/react": "18.2.0",
    "autoprefixer": "10.4.16",
    "postcss": "8.4.32"
  }
}""",
                "src": {
                    "app": {
                        "page.tsx": '''import Link from "next/link"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="p-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">{name}</h1>
          <div className="space-x-4">
            <Link href="/login" className="text-gray-600 hover:text-gray-900">Login</Link>
            <Link href="/signup" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
              Sign Up
            </Link>
          </div>
        </div>
      </nav>
      
      <main className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Welcome to {name}
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            The modern SaaS solution you\'ve been waiting for. 
            Get started today with our simple pricing plans.
          </p>
          <div className="space-x-4">
            <Link href="/signup" className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg hover:bg-blue-700">
              Get Started
            </Link>
            <Link href="/pricing" className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg text-lg hover:bg-gray-50">
              View Pricing
            </Link>
          </div>
        </div>
        
        <div className="mt-20 grid md:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-blue-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
              ⚡
            </div>
            <h3 className="text-xl font-semibold mb-2">Lightning Fast</h3>
            <p className="text-gray-600">Built for speed and performance</p>
          </div>
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-green-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
              🔒
            </div>
            <h3 className="text-xl font-semibold mb-2">Secure</h3>
            <p className="text-gray-600">Enterprise-grade security</p>
          </div>
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-purple-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
              📈
            </div>
            <h3 className="text-xl font-semibold mb-2">Scalable</h3>
            <p className="text-gray-600">Grows with your business</p>
          </div>
        </div>
      </main>
    </div>
  )
}''',
                        "pricing": {
                            "page.tsx": '''export default function Pricing() {
  const plans = [
    {
      name: "Starter",
      price: "$9",
      features: ["5 Projects", "Basic Support", "1GB Storage"]
    },
    {
      name: "Pro",
      price: "$29",
      features: ["Unlimited Projects", "Priority Support", "10GB Storage", "Advanced Analytics"],
      popular: true
    },
    {
      name: "Enterprise",
      price: "$99",
      features: ["Everything in Pro", "Custom Integrations", "Dedicated Support", "SSO"]
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Simple Pricing</h1>
          <p className="text-xl text-gray-600">Choose the plan that works for you</p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {{plans.map((plan, index) => (
            <div key={{index}} className={{`bg-white rounded-lg shadow-lg p-8 {{plan.popular ? "ring-2 ring-blue-500" : ""}}`}}>
              {{plan.popular && (
                <div className="bg-blue-500 text-white text-sm font-semibold px-3 py-1 rounded-full inline-block mb-4">
                  Most Popular
                </div>
              )}}
              <h3 className="text-2xl font-bold text-gray-900 mb-4">{{plan.name}}</h3>
              <div className="mb-6">
                <span className="text-4xl font-bold text-gray-900">{{plan.price}}</span>
                <span className="text-gray-600">/month</span>
              </div>
              <ul className="space-y-3 mb-8">
                {{plan.features.map((feature, i) => (
                  <li key={{i}} className="flex items-center text-gray-600">
                    <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    {{feature}}
                  </li>
                ))}}
              </ul>
              <button className={{`w-full py-3 px-6 rounded-lg font-semibold {{plan.popular ? "bg-blue-600 text-white hover:bg-blue-700" : "bg-gray-200 text-gray-900 hover:bg-gray-300"}}`}}>
                Get Started
              </button>
            </div>
          ))}}
        </div>
      </div>
    </div>
  )
}}'''
                        },
                        "dashboard": {
                            "page.tsx": '''export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-semibold text-gray-900">{name} Dashboard</h1>
            <button className="text-gray-600 hover:text-gray-900">Logout</button>
          </div>
        </div>
      </nav>
      
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Users</h3>
            <p className="text-3xl font-bold text-blue-600">1,234</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Revenue</h3>
            <p className="text-3xl font-bold text-green-600">$12,345</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Growth</h3>
            <p className="text-3xl font-bold text-purple-600">+23%</p>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="font-medium text-gray-900">New user signed up</p>
                  <p className="text-sm text-gray-600">john@example.com</p>
                </div>
                <span className="text-sm text-gray-500">2 minutes ago</span>
              </div>
              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="font-medium text-gray-900">Payment received</p>
                  <p className="text-sm text-gray-600">$29.00 from jane@example.com</p>
                </div>
                <span className="text-sm text-gray-500">1 hour ago</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}}'''
                        }
                    }
                },
                "tailwind.config.js": '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}''',
                "next.config.js": '''/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
}

module.exports = nextConfig''',
            },
            "docker-compose.yml": '''version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: saas_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:''',
            "README.md": "# {name} SaaS\n\nA complete SaaS starter with authentication, billing, and dashboard.\n\n## Features\n\n- 🔐 User authentication with NextAuth.js\n- 💳 Stripe billing and subscriptions\n- 📊 Admin dashboard\n- 🎨 Beautiful landing page\n- 🚀 Ready to deploy\n\n## Quick Start\n\n1. **Backend Setup**\n   ```bash\n   cd backend\n   python -m venv venv\n   source venv/bin/activate\n   pip install -r requirements.txt\n   cp .env.example .env\n   # Edit .env with your keys\n   python main.py\n   ```\n\n2. **Frontend Setup**\n   ```bash\n   cd frontend\n   npm install\n   npm run dev\n   ```\n\n3. **Database Setup**\n   ```bash\n   docker-compose up -d postgres\n   ```\n\n## Environment Variables\n\nCopy `.env.example` to `.env` and configure:\n\n- `STRIPE_SECRET_KEY` - Your Stripe secret key\n- `DATABASE_URL` - PostgreSQL connection string\n- `JWT_SECRET` - Secret for JWT tokens\n\n## Deployment\n\n- Frontend: Deploy to Vercel\n- Backend: Deploy to Railway or Render\n- Database: Use Supabase or Railway PostgreSQL\n\n## Tech Stack\n\n- **Frontend**: Next.js 14, Tailwind CSS, TypeScript\n- **Backend**: FastAPI, SQLAlchemy, JWT\n- **Database**: PostgreSQL\n- **Payments**: Stripe\n- **Auth**: NextAuth.js\n",
            ".gitignore": "node_modules/\nvenv/\n.env\n.env.local\n*.pyc\n__pycache__/\n.next/\ndist/\n*.log\n",
        },
    },
    "marketplace": {
        "description": "Multi-vendor marketplace: sellers, buyers, listings, payments",
        "structure": {
            ".planning": {
                "PROJECT.md": "# {name} Marketplace\n\n## Vision\nMulti-vendor marketplace platform connecting sellers and buyers.\n\n## Core Features\n- Vendor registration and management\n- Product listings and catalog\n- Order management\n- Payment processing\n- Rating and review system\n- Commission tracking\n\n## User Roles\n- **Admin**: Platform management\n- **Vendor**: Sell products\n- **Buyer**: Purchase products\n\n## Goals\n- [ ] Vendor onboarding\n- [ ] Product management\n- [ ] Order processing\n- [ ] Payment splits\n- [ ] Review system\n",
                "ROADMAP.md": "# Marketplace Roadmap\n\n## Phase 1: Core Platform\n- [ ] User authentication (buyers/sellers/admin)\n- [ ] Vendor registration and approval\n- [ ] Basic product listings\n\n## Phase 2: Commerce\n- [ ] Shopping cart and checkout\n- [ ] Payment processing with splits\n- [ ] Order management\n\n## Phase 3: Features\n- [ ] Rating and review system\n- [ ] Search and filtering\n- [ ] Vendor dashboard\n\n## Phase 4: Scale\n- [ ] Analytics and reporting\n- [ ] Commission management\n- [ ] Multi-language support\n",
                "STATE.md": "# Marketplace State\n\n## Current Phase\nPhase 1: Core Platform\n\n## Last Updated\n{date}\n\n## Tech Stack\n- Frontend: Next.js + Tailwind\n- Backend: FastAPI + PostgreSQL\n- Payments: Stripe Connect\n- File storage: AWS S3\n",
            },
            "backend": {
                "main.py": '''"""
{name} Marketplace API
Multi-vendor marketplace backend with Stripe Connect.
"""
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import stripe
import os
from datetime import datetime

app = FastAPI(
    title="{name} Marketplace",
    description="Multi-vendor marketplace API",
    version="1.0.0"
)

# Environment
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
stripe.api_key = STRIPE_SECRET_KEY

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {{"message": "Welcome to {name} Marketplace API"}}


@app.get("/health")
async def health():
    return {{"status": "healthy", "timestamp": datetime.utcnow()}}


# Vendor endpoints
@app.post("/vendors/register")
async def register_vendor(vendor_data: dict):
    """Register a new vendor and create Stripe Connect account."""
    try:
        # Create Stripe Connect account
        account = stripe.Account.create(
            type="express",
            country="US",
            email=vendor_data.get("email"),
            capabilities={{"card_payments": {{"requested": True}}, "transfers": {{"requested": True}}}},
        )
        
        # TODO: Save vendor to database with account.id
        return {{"vendor_id": "temp_id", "stripe_account_id": account.id, "status": "pending"}}
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/vendors/{{vendor_id}}/onboarding-link")
async def get_onboarding_link(vendor_id: str):
    """Get Stripe Connect onboarding link for vendor."""
    try:
        # TODO: Get stripe_account_id from database
        stripe_account_id = "acct_..."  # From database
        
        account_link = stripe.AccountLink.create(
            account=stripe_account_id,
            refresh_url="http://localhost:3000/vendor/onboarding",
            return_url="http://localhost:3000/vendor/dashboard",
            type="account_onboarding",
        )
        
        return {{"url": account_link.url}}
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


# Product endpoints
@app.post("/products")
async def create_product(product_data: dict):
    """Create a new product listing."""
    # TODO: Validate vendor, save to database
    return {{
        "id": "prod_123",
        "name": product_data.get("name"),
        "price": product_data.get("price"),
        "vendor_id": product_data.get("vendor_id"),
        "status": "active"
    }}


@app.get("/products")
async def list_products(skip: int = 0, limit: int = 20, category: str = None):
    """List products with optional filtering."""
    # TODO: Query database with filters
    return {{
        "products": [
            {{"id": "1", "name": "Sample Product", "price": 29.99, "vendor": "Vendor A"}},
        ],
        "total": 1,
        "skip": skip,
        "limit": limit
    }}


@app.get("/products/{{product_id}}")
async def get_product(product_id: str):
    """Get product details."""
    # TODO: Query database
    return {{
        "id": product_id,
        "name": "Sample Product",
        "description": "Product description",
        "price": 29.99,
        "images": ["image1.jpg"],
        "vendor": {{"id": "vendor_1", "name": "Vendor A"}}
    }}


# Order endpoints
@app.post("/orders")
async def create_order(order_data: dict):
    """Create order and process payment with marketplace fee."""
    try:
        items = order_data.get("items", [])
        total_amount = sum(item["price"] * item["quantity"] for item in items)
        marketplace_fee = int(total_amount * 0.10 * 100)  # 10% fee in cents
        
        # Create payment intent with application fee
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # Amount in cents
            currency="usd",
            application_fee_amount=marketplace_fee,
            transfer_data={{"destination": "acct_vendor_stripe_id"}},  # TODO: Get from DB
            metadata={{"order_id": "order_123"}}
        )
        
        return {{
            "order_id": "order_123",
            "payment_intent_id": payment_intent.id,
            "client_secret": payment_intent.client_secret
        }}
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/orders/{{order_id}}")
async def get_order(order_id: str):
    """Get order details."""
    # TODO: Query database
    return {{
        "id": order_id,
        "status": "pending",
        "total": 29.99,
        "items": [{{"product": "Sample Product", "quantity": 1, "price": 29.99}}],
        "created_at": datetime.utcnow().isoformat()
    }}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
''',
                "requirements.txt": """fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
pydantic>=2.5.0
stripe>=7.0.0
pillow>=10.0.0
python-multipart>=0.0.6
boto3>=1.34.0
""",
                ".env.example": """# Database
DATABASE_URL=postgresql://user:password@localhost/marketplace_db

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# AWS S3 (for product images)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=marketplace-images
AWS_REGION=us-east-1

# App
APP_URL=http://localhost:3000
""",
            },
            "frontend": {
                "package.json": """{
  "name": "{name_lower}-marketplace",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "@stripe/stripe-js": "2.4.0",
    "@stripe/react-stripe-js": "2.4.0",
    "tailwindcss": "3.4.1",
    "typescript": "5.3.3",
    "lucide-react": "0.316.0",
    "axios": "1.6.0"
  },
  "devDependencies": {
    "@types/node": "20.10.0",
    "@types/react": "18.2.0",
    "autoprefixer": "10.4.16",
    "postcss": "8.4.32"
  }
}""",
                "src": {
                    "app": {
                        "page.tsx": '''import Link from "next/link"
import { ShoppingBag, Store, Star } from "lucide-react"

export default function Home() {
  const featuredProducts = [
    {{ id: 1, name: "Wireless Headphones", price: 99.99, vendor: "AudioTech", rating: 4.5, image: "/api/placeholder/300/200" }},
    {{ id: 2, name: "Smart Watch", price: 199.99, vendor: "TechWear", rating: 4.8, image: "/api/placeholder/300/200" }},
    {{ id: 3, name: "Laptop Stand", price: 49.99, vendor: "OfficeGear", rating: 4.2, image: "/api/placeholder/300/200" }},
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-8">
              <Link href="/" className="text-2xl font-bold text-gray-900">{name}</Link>
              <nav className="hidden md:flex space-x-6">
                <Link href="/products" className="text-gray-600 hover:text-gray-900">Browse</Link>
                <Link href="/categories" className="text-gray-600 hover:text-gray-900">Categories</Link>
                <Link href="/vendors" className="text-gray-600 hover:text-gray-900">Vendors</Link>
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/sell" className="text-blue-600 hover:text-blue-700">Start Selling</Link>
              <Link href="/cart" className="p-2">
                <ShoppingBag className="w-6 h-6" />
              </Link>
              <Link href="/login" className="text-gray-600 hover:text-gray-900">Login</Link>
              <Link href="/signup" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h1 className="text-5xl font-bold mb-6">Discover Amazing Products</h1>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Shop from thousands of independent sellers and find unique products you can\'t get anywhere else.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/products" className="bg-white text-blue-600 px-8 py-3 rounded-lg text-lg font-semibold hover:bg-gray-100">
              Start Shopping
            </Link>
            <Link href="/sell" className="border border-white text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-white/10">
              Become a Seller
            </Link>
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Featured Products</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {{featuredProducts.map((product) => (
              <div key={{product.id}} className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                <div className="aspect-video bg-gray-200"></div>
                <div className="p-6">
                  <h3 className="font-semibold text-lg mb-2">{{product.name}}</h3>
                  <p className="text-gray-600 mb-2">by {{product.vendor}}</p>
                  <div className="flex items-center mb-3">
                    <div className="flex text-yellow-400">
                      {{[...Array(5)].map((_, i) => (
                        <Star key={{i}} className={{`w-4 h-4 ${{i < Math.floor(product.rating) ? "fill-current" : ""}}`}} />
                      ))}}
                    </div>
                    <span className="text-sm text-gray-600 ml-2">{{product.rating}}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-2xl font-bold text-gray-900">${{product.price}}</span>
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                      Add to Cart
                    </button>
                  </div>
                </div>
              </div>
            ))}}
          </div>
        </div>
      </section>

      {/* Vendor CTA */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <Store className="w-16 h-16 text-blue-600 mx-auto mb-6" />
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Start Your Online Store Today</h2>
          <p className="text-lg text-gray-600 mb-8">
            Join thousands of successful sellers on our platform. Easy setup, powerful tools, and dedicated support.
          </p>
          <Link href="/vendor/register" className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700">
            Become a Vendor
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">{name}</h3>
              <p className="text-gray-400">The marketplace that connects you with amazing independent sellers.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Shop</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/products" className="hover:text-white">All Products</Link></li>
                <li><Link href="/categories" className="hover:text-white">Categories</Link></li>
                <li><Link href="/vendors" className="hover:text-white">Vendors</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Sell</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/sell" className="hover:text-white">Start Selling</Link></li>
                <li><Link href="/vendor/login" className="hover:text-white">Vendor Login</Link></li>
                <li><Link href="/fees" className="hover:text-white">Fees & Pricing</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/help" className="hover:text-white">Help Center</Link></li>
                <li><Link href="/contact" className="hover:text-white">Contact Us</Link></li>
                <li><Link href="/terms" className="hover:text-white">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}}''',
                        "vendor": {
                            "register": {
                                "page.tsx": '''import {{ useState }} from "react"

export default function VendorRegister() {{
  const [formData, setFormData] = useState({{
    businessName: "",
    email: "",
    phone: "",
    description: "",
    category: ""
  }})

  const handleSubmit = async (e) => {{
    e.preventDefault()
    // TODO: Submit to API
    console.log("Vendor registration:", formData)
  }}

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-2xl mx-auto px-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Become a Vendor</h1>
          <p className="text-lg text-gray-600">Join our marketplace and start selling your products today</p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <form onSubmit={{handleSubmit}} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Business Name</label>
              <input
                type="text"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={{formData.businessName}}
                onChange={{(e) => setFormData({{...formData, businessName: e.target.value}})}}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={{formData.email}}
                onChange={{(e) => setFormData({{...formData, email: e.target.value}})}}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
              <input
                type="tel"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={{formData.phone}}
                onChange={{(e) => setFormData({{...formData, phone: e.target.value}})}}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Business Category</label>
              <select
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={{formData.category}}
                onChange={{(e) => setFormData({{...formData, category: e.target.value}})}}
              >
                <option value="">Select a category</option>
                <option value="electronics">Electronics</option>
                <option value="clothing">Clothing & Fashion</option>
                <option value="home">Home & Garden</option>
                <option value="sports">Sports & Outdoors</option>
                <option value="books">Books & Media</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Business Description</label>
              <textarea
                rows={{4}}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Tell us about your business and products..."
                value={{formData.description}}
                onChange={{(e) => setFormData({{...formData, description: e.target.value}})}}
              />
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Submit Application
            </button>
          </form>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">What happens next?</h3>
            <ol className="text-sm text-blue-800 space-y-1">
              <li>1. We\'ll review your application within 24-48 hours</li>
              <li>2. You\'ll receive an email with onboarding instructions</li>
              <li>3. Complete your Stripe Connect setup for payments</li>
              <li>4. Start listing and selling your products!</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  )
}}'''
                            }
                        },
                        "products": {
                            "page.tsx": '''import {{ Star, Filter }} from "lucide-react"

export default function Products() {{
  const products = [
    {{ id: 1, name: "Wireless Bluetooth Headphones", price: 89.99, vendor: "AudioTech", rating: 4.5, reviews: 127, image: "/api/placeholder/250/200", category: "Electronics" }},
    {{ id: 2, name: "Organic Cotton T-Shirt", price: 24.99, vendor: "EcoWear", rating: 4.3, reviews: 89, image: "/api/placeholder/250/200", category: "Clothing" }},
    {{ id: 3, name: "Smart Fitness Watch", price: 199.99, vendor: "TechWear", rating: 4.8, reviews: 203, image: "/api/placeholder/250/200", category: "Electronics" }},
    {{ id: 4, name: "Handcrafted Wooden Bowl", price: 34.99, vendor: "CraftCo", rating: 4.7, reviews: 56, image: "/api/placeholder/250/200", category: "Home" }},
    {{ id: 5, name: "Professional Yoga Mat", price: 59.99, vendor: "FitLife", rating: 4.6, reviews: 145, image: "/api/placeholder/250/200", category: "Sports" }},
    {{ id: 6, name: "Artisan Coffee Blend", price: 18.99, vendor: "RoastMaster", rating: 4.9, reviews: 312, image: "/api/placeholder/250/200", category: "Food" }},
  ]

  const categories = ["All", "Electronics", "Clothing", "Home", "Sports", "Food"]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">All Products</h1>
          <div className="flex items-center space-x-4">
            <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              <Filter className="w-4 h-4" />
              <span>Filter</span>
            </button>
            <select className="px-4 py-2 border border-gray-300 rounded-lg">
              <option>Sort by: Featured</option>
              <option>Price: Low to High</option>
              <option>Price: High to Low</option>
              <option>Customer Rating</option>
              <option>Newest</option>
            </select>
          </div>
        </div>

        <div className="flex gap-8">
          {/* Sidebar */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Categories</h3>
              <ul className="space-y-2">
                {{categories.map((category) => (
                  <li key={{category}}>
                    <button className="text-left w-full py-2 px-3 rounded hover:bg-gray-100">
                      {{category}}
                    </button>
                  </li>
                ))}}
              </ul>

              <hr className="my-6" />

              <h3 className="font-semibold text-gray-900 mb-4">Price Range</h3>
              <div className="space-y-3">
                <input type="range" className="w-full" min="0" max="500" />
                <div className="flex justify-between text-sm text-gray-600">
                  <span>$0</span>
                  <span>$500+</span>
                </div>
              </div>

              <hr className="my-6" />

              <h3 className="font-semibold text-gray-900 mb-4">Rating</h3>
              <div className="space-y-2">
                {{[5, 4, 3, 2, 1].map((stars) => (
                  <label key={{stars}} className="flex items-center space-x-2 cursor-pointer">
                    <input type="checkbox" className="rounded" />
                    <div className="flex text-yellow-400">
                      {{[...Array(stars)].map((_, i) => (
                        <Star key={{i}} className="w-4 h-4 fill-current" />
                      ))}}
                      {{[...Array(5 - stars)].map((_, i) => (
                        <Star key={{i}} className="w-4 h-4" />
                      ))}}
                    </div>
                    <span className="text-sm text-gray-600">& up</span>
                  </label>
                ))}}
              </div>
            </div>
          </div>

          {/* Products Grid */}
          <div className="flex-1">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {{products.map((product) => (
                <div key={{product.id}} className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow overflow-hidden">
                  <div className="aspect-square bg-gray-200"></div>
                  <div className="p-4">
                    <h3 className="font-semibold text-lg mb-1 line-clamp-2">{{product.name}}</h3>
                    <p className="text-sm text-gray-600 mb-2">by {{product.vendor}}</p>
                    
                    <div className="flex items-center mb-3">
                      <div className="flex text-yellow-400">
                        {{[...Array(5)].map((_, i) => (
                          <Star key={{i}} className={{`w-4 h-4 ${{i < Math.floor(product.rating) ? "fill-current" : ""}}`}} />
                        ))}}
                      </div>
                      <span className="text-sm text-gray-600 ml-2">{{product.rating}} ({{product.reviews}})</span>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-xl font-bold text-gray-900">${{product.price}}</span>
                      <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm">
                        Add to Cart
                      </button>
                    </div>
                  </div>
                </div>
              ))}}
            </div>

            {/* Pagination */}
            <div className="flex justify-center mt-12">
              <div className="flex space-x-1">
                <button className="px-3 py-2 rounded border hover:bg-gray-50">Previous</button>
                <button className="px-3 py-2 rounded bg-blue-600 text-white">1</button>
                <button className="px-3 py-2 rounded border hover:bg-gray-50">2</button>
                <button className="px-3 py-2 rounded border hover:bg-gray-50">3</button>
                <button className="px-3 py-2 rounded border hover:bg-gray-50">Next</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}}'''
                        }
                    }
                },
                "tailwind.config.js": '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}''',
            },
            "README.md": "# {name} Marketplace\n\nMulti-vendor marketplace platform with Stripe Connect integration.\n\n## Features\n\n- 🏪 **Multi-vendor Support**: Sellers can register and manage their own stores\n- 💳 **Stripe Connect**: Automated payment splits with marketplace fees\n- 🛍️ **Full E-commerce**: Product listings, cart, checkout, order management\n- ⭐ **Reviews & Ratings**: Customer feedback system\n- 📊 **Analytics**: Vendor and admin dashboards\n- 🔍 **Search & Filter**: Advanced product discovery\n\n## Quick Start\n\n1. **Database Setup**\n   ```bash\n   docker-compose up -d postgres\n   ```\n\n2. **Backend Setup**\n   ```bash\n   cd backend\n   python -m venv venv\n   source venv/bin/activate\n   pip install -r requirements.txt\n   cp .env.example .env\n   # Configure your environment variables\n   python main.py\n   ```\n\n3. **Frontend Setup**\n   ```bash\n   cd frontend\n   npm install\n   npm run dev\n   ```\n\n## Environment Setup\n\n### Stripe Connect Configuration\n\n1. Create a Stripe account\n2. Enable Stripe Connect in your dashboard\n3. Set up webhook endpoints for order processing\n4. Configure your platform fee percentage\n\n### Required Environment Variables\n\n```bash\n# Stripe\nSTRIPE_SECRET_KEY=sk_test_...\nSTRIPE_PUBLISHABLE_KEY=pk_test_...\nSTRIPE_WEBHOOK_SECRET=whsec_...\n\n# Database\nDATABASE_URL=postgresql://user:pass@localhost/marketplace\n\n# File Storage (AWS S3)\nAWS_ACCESS_KEY_ID=your_key\nAWS_SECRET_ACCESS_KEY=your_secret\nAWS_S3_BUCKET=marketplace-images\n```\n\n## Core Workflows\n\n### Vendor Onboarding\n1. Vendor registers with basic info\n2. Admin approves vendor application\n3. Vendor completes Stripe Connect onboarding\n4. Vendor can start listing products\n\n### Order Processing\n1. Customer adds products to cart\n2. Checkout creates Stripe payment intent\n3. Payment is split between vendor and marketplace\n4. Order is created and notifications sent\n5. Vendor fulfills order\n\n### Commission Structure\n- **Marketplace Fee**: 10% of each sale\n- **Payment Processing**: 2.9% + $0.30 (Stripe standard)\n- **Vendor Payout**: Remaining amount after fees\n\n## Tech Stack\n\n- **Frontend**: Next.js 14, Tailwind CSS, TypeScript\n- **Backend**: FastAPI, PostgreSQL, SQLAlchemy\n- **Payments**: Stripe Connect\n- **File Storage**: AWS S3\n- **Database**: PostgreSQL\n",
            ".gitignore": "node_modules/\nvenv/\n.env\n.env.local\n*.pyc\n__pycache__/\n.next/\ndist/\n*.log\nuploads/\n",
        },
    },
    "mobile": {
        "description": "React Native / Expo mobile app starter",
        "structure": {
            ".planning": {
                "PROJECT.md": "# {name} Mobile App\n\n## Vision\nCross-platform mobile app built with React Native and Expo.\n\n## Features\n- Cross-platform (iOS & Android)\n- Modern UI with native feel\n- Push notifications\n- Offline support\n- API integration\n- Navigation\n\n## Tech Stack\n- React Native\n- Expo SDK 50+\n- TypeScript\n- React Navigation\n- AsyncStorage\n- Expo Notifications\n\n## Goals\n- [ ] Basic navigation setup\n- [ ] Authentication screens\n- [ ] Main app features\n- [ ] Push notifications\n- [ ] App store deployment\n",
                "ROADMAP.md": "# Mobile App Roadmap\n\n## Phase 1: Foundation\n- [ ] Expo project setup\n- [ ] Navigation structure\n- [ ] Basic screens\n\n## Phase 2: Core Features\n- [ ] User authentication\n- [ ] API integration\n- [ ] Local storage\n\n## Phase 3: Enhanced UX\n- [ ] Push notifications\n- [ ] Offline support\n- [ ] App icons and splash\n\n## Phase 4: Deployment\n- [ ] App store submission\n- [ ] Beta testing\n- [ ] Production release\n",
                "STATE.md": "# Mobile App State\n\n## Current Phase\nPhase 1: Foundation\n\n## Last Updated\n{date}\n\n## Platform Status\n- iOS: Development\n- Android: Development\n- Expo: Latest SDK\n",
            },
            "mobile": {
                "package.json": """{
  "name": "{name_lower}-mobile",
  "version": "1.0.0",
  "main": "node_modules/expo/AppEntry.js",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "build:android": "eas build --platform android",
    "build:ios": "eas build --platform ios",
    "submit": "eas submit"
  },
  "dependencies": {
    "expo": "~50.0.0",
    "react": "18.2.0",
    "react-native": "0.73.0",
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/stack": "^6.3.20",
    "@react-navigation/bottom-tabs": "^6.5.11",
    "react-native-screens": "~3.29.0",
    "react-native-safe-area-context": "4.8.2",
    "expo-status-bar": "~1.11.1",
    "expo-font": "~11.10.0",
    "expo-splash-screen": "~0.26.0",
    "expo-constants": "~15.4.0",
    "expo-notifications": "~0.27.0",
    "@expo/vector-icons": "^14.0.0",
    "react-native-async-storage/async-storage": "1.21.0",
    "expo-secure-store": "~12.9.0"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@types/react": "~18.2.45",
    "typescript": "^5.1.3"
  }
}""",
                "app.json": """{
  "expo": {
    "name": "{name}",
    "slug": "{name_lower}",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "assetBundlePatterns": [
      "**/*"
    ],
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.example.{name_lower}"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#FFFFFF"
      },
      "package": "com.example.{name_lower}"
    },
    "web": {
      "favicon": "./assets/favicon.png"
    },
    "plugins": [
      "expo-notifications"
    ],
    "extra": {
      "eas": {
        "projectId": "your-project-id"
      }
    }
  }
}""",
                "App.tsx": '''import React, {{ useEffect }} from 'react';
import {{ NavigationContainer }} from '@react-navigation/native';
import {{ createBottomTabNavigator }} from '@react-navigation/bottom-tabs';
import {{ createStackNavigator }} from '@react-navigation/stack';
import {{ Ionicons }} from '@expo/vector-icons';
import * as SplashScreen from 'expo-splash-screen';

// Screens
import HomeScreen from './src/screens/HomeScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import LoginScreen from './src/screens/LoginScreen';

// Types
import {{ RootStackParamList, MainTabParamList }} from './src/types/navigation';

const Stack = createStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

// Keep splash screen visible while app loads
SplashScreen.preventAutoHideAsync();

function MainTabs() {{
  return (
    <Tab.Navigator
      screenOptions={{{{ route }}) => ({{
        tabBarIcon: ({{ focused, color, size }}) => {{
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Home') {{
            iconName = focused ? 'home' : 'home-outline';
          }} else if (route.name === 'Profile') {{
            iconName = focused ? 'person' : 'person-outline';
          }} else if (route.name === 'Settings') {{
            iconName = focused ? 'settings' : 'settings-outline';
          }} else {{
            iconName = 'help-outline';
          }}

          return <Ionicons name={{iconName}} size={{size}} color={{color}} />;
        }},
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      }})}
    >
      <Tab.Screen name="Home" component={{HomeScreen}} />
      <Tab.Screen name="Profile" component={{ProfileScreen}} />
      <Tab.Screen name="Settings" component={{SettingsScreen}} />
    </Tab.Navigator>
  );
}}

export default function App() {{
  useEffect(() => {{
    // Hide splash screen after app loads
    SplashScreen.hideAsync();
  }}, []);

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{{{ headerShown: false }}}}>
        <Stack.Screen name="Login" component={{LoginScreen}} />
        <Stack.Screen name="Main" component={{MainTabs}} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}}''',
                "src": {
                    "types": {
                        "navigation.ts": '''export type RootStackParamList = {
  Login: undefined;
  Main: undefined;
};

export type MainTabParamList = {
  Home: undefined;
  Profile: undefined;
  Settings: undefined;
};'''
                    },
                    "screens": {
                        "HomeScreen.tsx": '''import React from 'react';
import {{
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
}} from 'react-native';
import {{ Ionicons }} from '@expo/vector-icons';

export default function HomeScreen() {{
  const features = [
    {{ icon: 'flash', title: 'Fast Performance', description: 'Lightning fast app performance' }},
    {{ icon: 'shield-checkmark', title: 'Secure', description: 'Your data is safe with us' }},
    {{ icon: 'cloud', title: 'Cloud Sync', description: 'Access your data anywhere' }},
  ];

  return (
    <SafeAreaView style={{styles.container}}>
      <ScrollView contentContainerStyle={{styles.content}}>
        <View style={{styles.header}}>
          <Text style={{styles.title}}>Welcome to {name}</Text>
          <Text style={{styles.subtitle}}>Your mobile companion</Text>
        </View>

        <View style={{styles.featuresContainer}}>
          <Text style={{styles.sectionTitle}}>Features</Text>
          {{features.map((feature, index) => (
            <TouchableOpacity key={{index}} style={{styles.featureCard}}>
              <View style={{styles.featureIcon}}>
                <Ionicons name={{feature.icon as any}} size={{24}} color="#007AFF" />
              </View>
              <View style={{styles.featureContent}}>
                <Text style={{styles.featureTitle}}>{{feature.title}}</Text>
                <Text style={{styles.featureDescription}}>{{feature.description}}</Text>
              </View>
              <Ionicons name="chevron-forward" size={{20}} color="#C7C7CC" />
            </TouchableOpacity>
          ))}}
        </View>

        <TouchableOpacity style={{styles.actionButton}}>
          <Text style={{styles.actionButtonText}}>Get Started</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: '#F2F2F7',
  }},
  content: {{
    padding: 20,
  }},
  header: {{
    alignItems: 'center',
    marginBottom: 30,
    paddingTop: 20,
  }},
  title: {{
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 8,
  }},
  subtitle: {{
    fontSize: 16,
    color: '#8E8E93',
  }},
  featuresContainer: {{
    marginBottom: 30,
  }},
  sectionTitle: {{
    fontSize: 20,
    fontWeight: '600',
    color: '#000',
    marginBottom: 15,
  }},
  featureCard: {{
    backgroundColor: '#FFF',
    padding: 16,
    marginBottom: 10,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {{ width: 0, height: 1 }},
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  }},
  featureIcon: {{
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#E3F2FD',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  }},
  featureContent: {{
    flex: 1,
  }},
  featureTitle: {{
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
    marginBottom: 2,
  }},
  featureDescription: {{
    fontSize: 14,
    color: '#8E8E93',
  }},
  actionButton: {{
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  }},
  actionButtonText: {{
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  }},
}});''',
                        "LoginScreen.tsx": '''import React, {{ useState }} from 'react';
import {{
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
}} from 'react-native';
import {{ useNavigation }} from '@react-navigation/native';

export default function LoginScreen() {{
  const navigation = useNavigation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {{
    if (!email || !password) {{
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }}

    // TODO: Implement actual authentication
    console.log('Login attempt:', {{ email, password }});
    
    // Navigate to main app
    navigation.navigate('Main' as never);
  }};

  return (
    <SafeAreaView style={{styles.container}}>
      <View style={{styles.content}}>
        <View style={{styles.header}}>
          <Text style={{styles.title}}>{name}</Text>
          <Text style={{styles.subtitle}}>Sign in to your account</Text>
        </View>

        <View style={{styles.form}}>
          <View style={{styles.inputGroup}}>
            <Text style={{styles.label}}>Email</Text>
            <TextInput
              style={{styles.input}}
              placeholder="Enter your email"
              value={{email}}
              onChangeText={{setEmail}}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={{false}}
            />
          </View>

          <View style={{styles.inputGroup}}>
            <Text style={{styles.label}}>Password</Text>
            <TextInput
              style={{styles.input}}
              placeholder="Enter your password"
              value={{password}}
              onChangeText={{setPassword}}
              secureTextEntry
              autoCapitalize="none"
            />
          </View>

          <TouchableOpacity style={{styles.loginButton}} onPress={{handleLogin}}>
            <Text style={{styles.loginButtonText}}>Sign In</Text>
          </TouchableOpacity>

          <TouchableOpacity style={{styles.forgotButton}}>
            <Text style={{styles.forgotButtonText}}>Forgot Password?</Text>
          </TouchableOpacity>
        </View>

        <View style={{styles.footer}}>
          <Text style={{styles.footerText}}>Don't have an account?</Text>
          <TouchableOpacity>
            <Text style={{styles.signupText}}> Sign Up</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: '#FFF',
  }},
  content: {{
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  }},
  header: {{
    alignItems: 'center',
    marginBottom: 40,
  }},
  title: {{
    fontSize: 32,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 8,
  }},
  subtitle: {{
    fontSize: 16,
    color: '#8E8E93',
  }},
  form: {{
    marginBottom: 30,
  }},
  inputGroup: {{
    marginBottom: 20,
  }},
  label: {{
    fontSize: 14,
    fontWeight: '600',
    color: '#000',
    marginBottom: 8,
  }},
  input: {{
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    backgroundColor: '#F2F2F7',
  }},
  loginButton: {{
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  }},
  loginButtonText: {{
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
  }},
  forgotButton: {{
    alignItems: 'center',
  }},
  forgotButtonText: {{
    color: '#007AFF',
    fontSize: 14,
  }},
  footer: {{
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  }},
  footerText: {{
    color: '#8E8E93',
    fontSize: 14,
  }},
  signupText: {{
    color: '#007AFF',
    fontSize: 14,
    fontWeight: '600',
  }},
}});''',
                        "ProfileScreen.tsx": '''import React from 'react';
import {{
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Image,
}} from 'react-native';
import {{ Ionicons }} from '@expo/vector-icons';

export default function ProfileScreen() {{
  const menuItems = [
    {{ icon: 'person-outline', title: 'Edit Profile', hasChevron: true }},
    {{ icon: 'notifications-outline', title: 'Notifications', hasChevron: true }},
    {{ icon: 'lock-closed-outline', title: 'Privacy & Security', hasChevron: true }},
    {{ icon: 'help-circle-outline', title: 'Help & Support', hasChevron: true }},
    {{ icon: 'information-circle-outline', title: 'About', hasChevron: true }},
    {{ icon: 'log-out-outline', title: 'Sign Out', hasChevron: false, isDestructive: true }},
  ];

  return (
    <SafeAreaView style={{styles.container}}>
      <ScrollView contentContainerStyle={{styles.content}}>
        <View style={{styles.header}}>
          <View style={{styles.profileImageContainer}}>
            <View style={{styles.profileImagePlaceholder}}>
              <Ionicons name="person" size={{40}} color="#8E8E93" />
            </View>
          </View>
          <Text style={{styles.name}}>John Doe</Text>
          <Text style={{styles.email}}>john@example.com</Text>
        </View>

        <View style={{styles.menuContainer}}>
          {{menuItems.map((item, index) => (
            <TouchableOpacity 
              key={{index}} 
              style={{[
                styles.menuItem,
                index === menuItems.length - 1 && styles.lastMenuItem
              ]}}
            >
              <View style={{styles.menuItemContent}}>
                <View style={{styles.menuItemLeft}}>
                  <Ionicons 
                    name={{item.icon as any}} 
                    size={{24}} 
                    color={{item.isDestructive ? '#FF3B30' : '#007AFF'}} 
                  />
                  <Text style={{[
                    styles.menuItemText,
                    item.isDestructive && styles.destructiveText
                  ]}}>
                    {{item.title}}
                  </Text>
                </View>
                {{item.hasChevron && (
                  <Ionicons name="chevron-forward" size={{20}} color="#C7C7CC" />
                )}}
              </View>
            </TouchableOpacity>
          ))}}
        </View>

        <View style={{styles.appInfo}}>
          <Text style={{styles.appVersion}}>Version 1.0.0</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: '#F2F2F7',
  }},
  content: {{
    paddingBottom: 20,
  }},
  header: {{
    alignItems: 'center',
    backgroundColor: '#FFF',
    paddingVertical: 30,
    marginBottom: 20,
  }},
  profileImageContainer: {{
    marginBottom: 16,
  }},
  profileImagePlaceholder: {{
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#F2F2F7',
    justifyContent: 'center',
    alignItems: 'center',
  }},
  name: {{
    fontSize: 22,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 4,
  }},
  email: {{
    fontSize: 16,
    color: '#8E8E93',
  }},
  menuContainer: {{
    backgroundColor: '#FFF',
    marginHorizontal: 20,
    borderRadius: 12,
    overflow: 'hidden',
  }},
  menuItem: {{
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  }},
  lastMenuItem: {{
    borderBottomWidth: 0,
  }},
  menuItemContent: {{
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
  }},
  menuItemLeft: {{
    flexDirection: 'row',
    alignItems: 'center',
  }},
  menuItemText: {{
    fontSize: 16,
    color: '#000',
    marginLeft: 12,
  }},
  destructiveText: {{
    color: '#FF3B30',
  }},
  appInfo: {{
    alignItems: 'center',
    marginTop: 30,
  }},
  appVersion: {{
    fontSize: 14,
    color: '#8E8E93',
  }},
}});''',
                        "SettingsScreen.tsx": '''import React, {{ useState }} from 'react';
import {{
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Switch,
  TouchableOpacity,
}} from 'react-native';
import {{ Ionicons }} from '@expo/vector-icons';

export default function SettingsScreen() {{
  const [pushNotifications, setPushNotifications] = useState(true);
  const [emailNotifications, setEmailNotifications] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [locationServices, setLocationServices] = useState(true);

  const settingSections = [
    {{
      title: 'Notifications',
      items: [
        {{
          title: 'Push Notifications',
          subtitle: 'Receive notifications on your device',
          type: 'switch',
          value: pushNotifications,
          onToggle: setPushNotifications,
        }},
        {{
          title: 'Email Notifications',
          subtitle: 'Receive updates via email',
          type: 'switch',
          value: emailNotifications,
          onToggle: setEmailNotifications,
        }},
      ],
    }},
    {{
      title: 'Appearance',
      items: [
        {{
          title: 'Dark Mode',
          subtitle: 'Use dark theme',
          type: 'switch',
          value: darkMode,
          onToggle: setDarkMode,
        }},
      ],
    }},
    {{
      title: 'Privacy',
      items: [
        {{
          title: 'Location Services',
          subtitle: 'Allow app to access your location',
          type: 'switch',
          value: locationServices,
          onToggle: setLocationServices,
        }},
        {{
          title: 'Data & Privacy',
          subtitle: 'Manage your data and privacy settings',
          type: 'navigation',
        }},
      ],
    }},
    {{
      title: 'Support',
      items: [
        {{
          title: 'Contact Support',
          subtitle: 'Get help with your account',
          type: 'navigation',
        }},
        {{
          title: 'Terms of Service',
          subtitle: 'Read our terms and conditions',
          type: 'navigation',
        }},
        {{
          title: 'Privacy Policy',
          subtitle: 'Learn how we protect your privacy',
          type: 'navigation',
        }},
      ],
    }},
  ];

  const renderSettingItem = (item: any, isLast: boolean) => {{
    return (
      <View style={{[styles.settingItem, isLast && styles.lastSettingItem]}}>
        <View style={{styles.settingContent}}>
          <Text style={{styles.settingTitle}}>{{item.title}}</Text>
          <Text style={{styles.settingSubtitle}}>{{item.subtitle}}</Text>
        </View>
        {{item.type === 'switch' ? (
          <Switch
            value={{item.value}}
            onValueChange={{item.onToggle}}
            trackColor={{{{ false: '#E5E5EA', true: '#007AFF' }}}}
            thumbColor="#FFF"
          />
        ) : (
          <Ionicons name="chevron-forward" size={{20}} color="#C7C7CC" />
        )}}
      </View>
    );
  }};

  return (
    <SafeAreaView style={{styles.container}}>
      <ScrollView contentContainerStyle={{styles.content}}>
        <View style={{styles.header}}>
          <Text style={{styles.title}}>Settings</Text>
        </View>

        {{settingSections.map((section, sectionIndex) => (
          <View key={{sectionIndex}} style={{styles.section}}>
            <Text style={{styles.sectionTitle}}>{{section.title}}</Text>
            <View style={{styles.sectionContent}}>
              {{section.items.map((item, itemIndex) => (
                <TouchableOpacity
                  key={{itemIndex}}
                  disabled={{item.type === 'switch'}}
                  style={{styles.touchableItem}}
                >
                  {{renderSettingItem(item, itemIndex === section.items.length - 1)}}
                </TouchableOpacity>
              ))}}
            </View>
          </View>
        ))}}
      </ScrollView>
    </SafeAreaView>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: '#F2F2F7',
  }},
  content: {{
    paddingBottom: 20,
  }},
  header: {{
    backgroundColor: '#FFF',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  }},
  title: {{
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000',
  }},
  section: {{
    marginTop: 20,
  }},
  sectionTitle: {{
    fontSize: 16,
    fontWeight: '600',
    color: '#8E8E93',
    marginHorizontal: 20,
    marginBottom: 8,
  }},
  sectionContent: {{
    backgroundColor: '#FFF',
    marginHorizontal: 20,
    borderRadius: 12,
    overflow: 'hidden',
  }},
  touchableItem: {{
    // Empty style for consistency
  }},
  settingItem: {{
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  }},
  lastSettingItem: {{
    borderBottomWidth: 0,
  }},
  settingContent: {{
    flex: 1,
  }},
  settingTitle: {{
    fontSize: 16,
    fontWeight: '400',
    color: '#000',
    marginBottom: 2,
  }},
  settingSubtitle: {{
    fontSize: 14,
    color: '#8E8E93',
  }},
}});''',
                    },
                },
                "assets": {
                    ".gitkeep": ""
                },
                "eas.json": """{
  "cli": {
    "version": ">= 5.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {}
  },
  "submit": {
    "production": {}
  }
}""",
            },
            "README.md": "# {name} Mobile App\n\nBuilt with React Native and Expo.\n\n## Quick Start\n\n```bash\nnpm install\nnpm start\n```\n",
            ".gitignore": "node_modules/\n.expo/\ndist/\nnpm-debug.*\n*.jks\n*.p8\n*.p12\n*.key\n*.mobileprovision\n*.orig.*\nweb-build/\n.env.*\n",
        },
    },
}


def create_structure(path: Path, structure: Dict[str, Any], context: Dict[str, str]):
    """Recursively create directory structure."""
    for name, content in structure.items():
        item_path = path / name

        if isinstance(content, dict):
            # It's a directory
            item_path.mkdir(parents=True, exist_ok=True)
            create_structure(item_path, content, context)
        else:
            # It's a file
            item_path.parent.mkdir(parents=True, exist_ok=True)
            # Use manual replacement to handle templates with literal braces
            # (e.g. JSON, Python dicts) that break str.format()
            formatted_content = content
            for key, value in context.items():
                formatted_content = formatted_content.replace("{" + key + "}", value)
            
            # FIXED: Convert double braces back to single braces for JSON/Python dicts
            formatted_content = formatted_content.replace("{{", "{").replace("}}", "}")
            
            item_path.write_text(formatted_content)


def create_project(name: str, template: str = "basic", use_current_dir: bool = False) -> bool:
    """Create a new project from template."""
    # Validate template
    if template not in TEMPLATES:
        print(f"❌ Unknown template: {template}")
        print(f"   Available: {', '.join(TEMPLATES.keys())}")
        return False

    # Validate project name
    import re
    if not name or not re.match(r'^[a-z0-9]([a-z0-9]|-(?!-))*[a-z0-9]$|^[a-z0-9]$', name) or not any(c.isalpha() for c in name):
        print(f"❌ Invalid project name: '{name}'")
        print("   Project names must:")
        print("   • Be lowercase letters, numbers, and hyphens only")
        print("   • Start and end with a letter or number")
        print("   • Not contain spaces or special characters")
        print(f"   Examples: my-app, api-server, todo-list")
        return False

    # FIXED: Use current directory instead of global PROJECTS_DIR
    if use_current_dir:
        project_path = Path.cwd() / name
    else:
        project_path = PROJECTS_DIR / name

    # Check for existing project
    if project_path.exists():
        print(f"❌ Project already exists: {project_path}")
        print(f"   Choose a different name or delete the existing project")
        return False

    # Prepare context
    context = {
        "name": name,
        "name_lower": name.lower().replace("-", "_").replace(" ", "_"),
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    template_data = TEMPLATES[template]
    structure = template_data["structure"]

    # Handle combined templates
    if isinstance(structure, str) and structure.startswith("COMBINE:"):
        templates_to_combine = structure.replace("COMBINE:", "").split("+")
        structure = {}
        for t in templates_to_combine:
            if t in TEMPLATES:
                t_structure = TEMPLATES[t]["structure"]
                if isinstance(t_structure, dict):
                    # Merge structures
                    for key, value in t_structure.items():
                        if (
                            key in structure
                            and isinstance(structure[key], dict)
                            and isinstance(value, dict)
                        ):
                            structure[key].update(value)
                        else:
                            structure[key] = value

    # Create project directory
    project_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Creating project: {name}")

    # Create structure
    create_structure(project_path, structure, context)

    # Make shell scripts executable
    for script in project_path.rglob("*.sh"):
        script.chmod(0o755)

    # Initialize git repository
    try:
        import subprocess
        subprocess.run(["git", "init", "-q"], cwd=project_path, check=True, 
                      capture_output=True, text=True)
        print(f"📦 Git repository initialized")
        
        # Add initial commit
        subprocess.run(["git", "add", "."], cwd=project_path, check=True,
                      capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", f"Initial commit: {template} template"], 
                      cwd=project_path, check=True, capture_output=True, text=True)
        print(f"💡 Initial commit created")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"⚠️  Could not initialize git repository (git not found or error)")

    print(f"✅ Project created at: {project_path}")

    # Check .env configuration
    env_file = MYWORK_ROOT / ".env"
    if not env_file.exists():
        print(f"\n   ⚠️  No .env file found!")
        print(f"   Run 'mw setup' to configure your API keys and environment.")

    print(f"\n   Next steps:")
    if use_current_dir:
        print(f"   1. cd {name}")
    else:
        print(f"   1. cd projects/{name}")
    print(f"   2. Review .planning/PROJECT.md")
    print(f"   3. Run /gsd:plan-phase 1")

    return True


def list_templates():
    """List available templates."""
    print("\n📋 Available Templates")
    print("=" * 50)

    for name, data in TEMPLATES.items():
        print(f"\n   {name}")
        print(f"   └─ {data['description']}")

    print("\n   Usage: python scaffold.py new <project-name> <template>")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "new":
        if len(sys.argv) < 3:
            print("Usage: python scaffold.py new <name> [template] [--current-dir]")
            sys.exit(1)

        name = sys.argv[2]
        template = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else "basic"
        use_current_dir = "--current-dir" in sys.argv
        success = create_project(name, template, use_current_dir)
        if not success:
            sys.exit(1)

    elif command == "list":
        list_templates()

    elif command == "from-module":
        if len(sys.argv) < 4:
            print("Usage: python scaffold.py from-module <name> <module_id>")
            sys.exit(1)
        print("🚧 Module-based scaffolding coming soon!")
        print("   Use 'python module_registry.py search' to find modules")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

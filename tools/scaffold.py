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
            "README.md": "# {name}\n\nCreated with MyWork Framework on {date}\n\n## Getting Started\n\n```bash\ncd projects/{name}\n# Start development\n```\n\n## Structure\n\n```\n{name}/\n├── .planning/     # GSD state files\n└── README.md\n```\n",
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
            "README.md": "# {name}\n\n## Setup\n\n```bash\ncd backend\npython -m venv venv\nsource venv/bin/activate\npip install -r requirements.txt\npython main.py\n```\n\nAPI available at http://localhost:8000\n",
            ".gitignore": "venv/\n.env\n*.db\n__pycache__/\n*.pyc\n",
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
            try:
                formatted_content = content.format(**context)
            except (KeyError, ValueError):
                # Template contains literal braces (e.g. dicts in code), skip formatting
                formatted_content = content
            item_path.write_text(formatted_content)


def create_project(name: str, template: str = "basic") -> bool:
    """Create a new project from template."""
    # Validate template
    if template not in TEMPLATES:
        print(f"❌ Unknown template: {template}")
        print(f"   Available: {', '.join(TEMPLATES.keys())}")
        return False

    # Validate project name
    import re
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$', name):
        print(f"❌ Invalid project name: '{name}'")
        print("   Project names must:")
        print("   • Be lowercase letters, numbers, and hyphens only")
        print("   • Start and end with a letter or number")
        print("   • Not contain spaces or special characters")
        print(f"   Examples: my-app, api-server, todo-list")
        return False

    # Check for existing project
    project_path = PROJECTS_DIR / name
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

    print(f"✅ Project created at: {project_path}")

    # Check .env configuration
    env_file = MYWORK_ROOT / ".env"
    if not env_file.exists():
        print(f"\n   ⚠️  No .env file found!")
        print(f"   Run 'mw setup' to configure your API keys and environment.")

    print(f"\n   Next steps:")
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
            print("Usage: python scaffold.py new <name> [template]")
            sys.exit(1)

        name = sys.argv[2]
        template = sys.argv[3] if len(sys.argv) > 3 else "basic"
        success = create_project(name, template)
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

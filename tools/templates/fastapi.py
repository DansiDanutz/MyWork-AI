#!/usr/bin/env python3
"""Working FastAPI template."""
from datetime import datetime

def create_fastapi_project(name, target_dir):
    """Create a complete, runnable FastAPI project."""
    from pathlib import Path
    
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    files = {
        "main.py": f"""# {name} - FastAPI Application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="{name} API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {{"message": "Welcome to {name} API", "docs": "/docs"}}

@app.get("/health")
async def health():
    return {{"status": "healthy", "timestamp": datetime.utcnow()}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
""",
        "requirements.txt": """fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-dotenv>=1.0.0
""",
        "README.md": f"""# {name}

A FastAPI application.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Open http://localhost:8000/docs for API documentation.

## Testing

Visit the `/health` endpoint to verify the API is running.
""",
        ".gitignore": """__pycache__/
*.pyc
.env
*.db
""",
    }
    
    for filename, content in files.items():
        file_path = target_path / filename
        file_path.write_text(content)
    
    # Also create .planning directory
    planning_dir = target_path / ".planning"
    planning_dir.mkdir(exist_ok=True)
    
    planning_files = {
        "PROJECT.md": f"# {name}\n\nFastAPI project created by MyWork-AI.\n",
        "ROADMAP.md": f"# {name} Roadmap\n\n## Phase 1: Setup\n- [x] Initial FastAPI setup\n",
        "STATE.md": f"# {name} State\n\nCurrent Phase: Phase 1\nLast Updated: {datetime.now().strftime('%Y-%m-%d')}\n",
    }
    
    for filename, content in planning_files.items():
        file_path = planning_dir / filename
        file_path.write_text(content)
    
    print(f"✅ Created FastAPI project: {target_path}")
    return True

if __name__ == "__main__":
    create_fastapi_project("test", "/tmp/test")

#!/usr/bin/env python3
"""
AI Documentation Generator
==========================
Scans a project directory and uses AI to generate comprehensive documentation.

Usage:
    python ai_docs.py <project_path>        # Generate docs for project
    python ai_docs.py --current             # Generate docs for current directory
    mw docs generate <project>              # Via CLI
"""

import os
import sys
import json
import urllib.request
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

# OpenRouter API configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.0-flash-001"

# File patterns to analyze
SOURCE_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs', 
                    '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.dart', '.scala', '.r'}
CONFIG_FILES = {'package.json', 'requirements.txt', 'Cargo.toml', 'pom.xml', 'build.gradle', 
               'composer.json', 'Gemfile', 'go.mod', 'pubspec.yaml', 'setup.py', 'pyproject.toml'}
IGNORE_DIRS = {'node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build', 
              '.next', 'target', 'vendor', 'coverage'}

def call_openrouter_api(prompt: str) -> str:
    """Call OpenRouter API with the given prompt."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    
    try:
        req = urllib.request.Request(OPENROUTER_URL, data=data, headers=headers)
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return "Error: No response from API"
    
    except Exception as e:
        return f"Error: Failed to call OpenRouter API - {str(e)}"

def scan_project(project_path: str) -> Dict[str, Any]:
    """Scan project directory and collect information."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"error": f"Project path does not exist: {project_path}"}
    
    project_info = {
        "name": project_path.name,
        "path": str(project_path),
        "structure": {},
        "files": [],
        "languages": set(),
        "frameworks": [],
        "config_files": [],
        "dependencies": {},
        "entry_points": []
    }
    
    # Scan directory structure
    for root, dirs, files in os.walk(project_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        root_path = Path(root)
        rel_path = root_path.relative_to(project_path)
        
        for file in files:
            file_path = root_path / file
            rel_file_path = rel_path / file
            
            # Analyze file
            file_info = analyze_file(file_path, rel_file_path)
            if file_info:
                project_info["files"].append(file_info)
                
                # Collect languages
                if file_info.get("language"):
                    project_info["languages"].add(file_info["language"])
                
                # Collect config files
                if file in CONFIG_FILES:
                    project_info["config_files"].append(str(rel_file_path))
                    
                    # Extract dependencies
                    deps = extract_dependencies(file_path, file)
                    if deps:
                        project_info["dependencies"].update(deps)
    
    # Detect frameworks and entry points
    project_info["languages"] = list(project_info["languages"])
    project_info["frameworks"] = detect_frameworks(project_info)
    project_info["entry_points"] = find_entry_points(project_info)
    
    return project_info

def analyze_file(file_path: Path, rel_path: Path) -> Optional[Dict[str, Any]]:
    """Analyze a single file."""
    try:
        # Skip large files
        if file_path.stat().st_size > 1024 * 1024:  # 1MB
            return None
        
        # Get file info
        file_info = {
            "path": str(rel_path),
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "extension": file_path.suffix,
            "language": detect_language(str(file_path))
        }
        
        # Read source files for analysis
        if file_path.suffix in SOURCE_EXTENSIONS:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_info["lines"] = len(content.splitlines())
                    file_info["functions"] = extract_functions(content, file_info["language"])
                    file_info["classes"] = extract_classes(content, file_info["language"])
                    file_info["imports"] = extract_imports(content, file_info["language"])
            except UnicodeDecodeError:
                pass  # Skip binary files
        
        return file_info
    
    except Exception:
        return None

def detect_language(file_path: str) -> str:
    """Detect programming language from file extension."""
    ext = Path(file_path).suffix.lower()
    
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React JSX',
        '.tsx': 'React TSX',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.dart': 'Dart'
    }
    
    return language_map.get(ext, '')

def extract_functions(content: str, language: str) -> List[str]:
    """Extract function names from code (basic regex-based)."""
    import re
    
    functions = []
    
    if language == 'Python':
        pattern = r'def\s+([a-zA-Z_]\w*)\s*\('
    elif language in ['JavaScript', 'TypeScript']:
        pattern = r'(?:function\s+([a-zA-Z_]\w*)|([a-zA-Z_]\w*)\s*=\s*(?:function|\([^)]*\)\s*=>)|([a-zA-Z_]\w*)\s*\([^)]*\)\s*{)'
    elif language == 'Java':
        pattern = r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+([a-zA-Z_]\w*)\s*\('
    else:
        return functions
    
    matches = re.findall(pattern, content)
    for match in matches:
        if isinstance(match, tuple):
            func_name = next((m for m in match if m), None)
            if func_name:
                functions.append(func_name)
        else:
            functions.append(match)
    
    return list(set(functions))

def extract_classes(content: str, language: str) -> List[str]:
    """Extract class names from code."""
    import re
    
    if language == 'Python':
        pattern = r'class\s+([a-zA-Z_]\w*)'
    elif language in ['JavaScript', 'TypeScript']:
        pattern = r'class\s+([a-zA-Z_]\w*)'
    elif language == 'Java':
        pattern = r'(?:public|private)?\s*class\s+([a-zA-Z_]\w*)'
    else:
        return []
    
    return re.findall(pattern, content)

def extract_imports(content: str, language: str) -> List[str]:
    """Extract import statements from code."""
    import re
    
    imports = []
    
    if language == 'Python':
        patterns = [r'import\s+([^\s,]+)', r'from\s+([^\s]+)\s+import']
    elif language in ['JavaScript', 'TypeScript']:
        patterns = [r'import.*from\s+["\']([^"\']+)["\']', r'import\s+["\']([^"\']+)["\']']
    else:
        return imports
    
    for pattern in patterns:
        imports.extend(re.findall(pattern, content))
    
    return list(set(imports))

def extract_dependencies(file_path: Path, filename: str) -> Dict[str, str]:
    """Extract dependencies from config files."""
    try:
        if filename == 'package.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
                deps = data.get('dependencies', {})
                dev_deps = data.get('devDependencies', {})
                return {**deps, **dev_deps}
        
        elif filename == 'requirements.txt':
            deps = {}
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '==' in line:
                            name, version = line.split('==', 1)
                            deps[name] = version
                        else:
                            deps[line] = 'latest'
            return deps
        
        elif filename == 'pyproject.toml':
            # Basic TOML parsing for dependencies
            deps = {}
            with open(file_path, 'r') as f:
                content = f.read()
                # This is a simplified parser - in production, use tomllib
                import re
                matches = re.findall(r'"([^"]+)"\s*=\s*"([^"]+)"', content)
                for name, version in matches:
                    deps[name] = version
            return deps
    
    except Exception:
        pass
    
    return {}

def detect_frameworks(project_info: Dict[str, Any]) -> List[str]:
    """Detect frameworks based on dependencies and file structure."""
    frameworks = []
    deps = project_info.get("dependencies", {})
    files = [f["path"] for f in project_info.get("files", [])]
    
    # Frontend frameworks
    if "react" in deps:
        frameworks.append("React")
    if "vue" in deps:
        frameworks.append("Vue.js")
    if "angular" in deps or "@angular/core" in deps:
        frameworks.append("Angular")
    if "next" in deps:
        frameworks.append("Next.js")
    if "nuxt" in deps:
        frameworks.append("Nuxt.js")
    
    # Backend frameworks
    if "express" in deps:
        frameworks.append("Express.js")
    if "fastapi" in deps:
        frameworks.append("FastAPI")
    if "django" in deps:
        frameworks.append("Django")
    if "flask" in deps:
        frameworks.append("Flask")
    
    # Mobile frameworks
    if "react-native" in deps:
        frameworks.append("React Native")
    if "expo" in deps:
        frameworks.append("Expo")
    
    # Build tools
    if "webpack" in deps:
        frameworks.append("Webpack")
    if "vite" in deps:
        frameworks.append("Vite")
    
    # File-based detection
    if "tailwind.config.js" in files:
        frameworks.append("Tailwind CSS")
    if "docker-compose.yml" in files:
        frameworks.append("Docker")
    
    return frameworks

def find_entry_points(project_info: Dict[str, Any]) -> List[str]:
    """Find entry points of the application."""
    entry_points = []
    files = [f["path"] for f in project_info.get("files", [])]
    
    # Common entry points
    common_entries = [
        "main.py", "app.py", "index.js", "index.ts", "server.js", 
        "app.js", "main.js", "index.html", "App.tsx", "App.jsx"
    ]
    
    for entry in common_entries:
        if entry in files:
            entry_points.append(entry)
    
    return entry_points

def generate_readme(project_info: Dict[str, Any]) -> str:
    """Generate README.md using AI."""
    prompt = f"""Generate a comprehensive README.md for this project based on the analysis below.

PROJECT ANALYSIS:
- Name: {project_info['name']}
- Languages: {', '.join(project_info.get('languages', []))}
- Frameworks: {', '.join(project_info.get('frameworks', []))}
- Entry Points: {', '.join(project_info.get('entry_points', []))}
- Total Files: {len(project_info.get('files', []))}
- Config Files: {', '.join(project_info.get('config_files', []))}

KEY DEPENDENCIES:
{json.dumps(project_info.get('dependencies', {}), indent=2)}

FILE STRUCTURE:
{format_file_structure(project_info.get('files', []))}

Generate a professional README.md with:

# Project Name

## Description
[Brief description of what this project does]

## Features
- [Key features based on analysis]

## Tech Stack
[List technologies, frameworks, languages]

## Getting Started

### Prerequisites
[Required software/tools]

### Installation
```bash
# Step-by-step installation commands
```

### Usage
```bash
# How to run the project
```

## Project Structure
```
[Directory tree showing key files and folders]
```

## API Documentation
[If backend API detected]

## Configuration
[Environment variables, config files]

## Contributing
[Contributing guidelines]

## License
[License information]

Make it professional, informative, and easy to follow. Use proper markdown formatting with badges, code blocks, and clear sections."""

    return call_openrouter_api(prompt)

def generate_api_docs(project_info: Dict[str, Any]) -> str:
    """Generate API documentation if backend detected."""
    if not any(fw in ['FastAPI', 'Express.js', 'Django', 'Flask'] for fw in project_info.get('frameworks', [])):
        return ""
    
    prompt = f"""Generate API documentation for this backend project:

PROJECT ANALYSIS:
- Frameworks: {', '.join(project_info.get('frameworks', []))}
- Languages: {', '.join(project_info.get('languages', []))}
- Entry Points: {', '.join(project_info.get('entry_points', []))}

BACKEND FILES:
{format_backend_files(project_info.get('files', []))}

Generate comprehensive API documentation including:

# API Documentation

## Base URL
```
http://localhost:PORT
```

## Authentication
[Authentication method if detected]

## Endpoints

### GET /endpoint
- Description: [Purpose]
- Parameters: [Query/path parameters]
- Response: [Response format]
- Example:
  ```bash
  curl -X GET "http://localhost:PORT/endpoint"
  ```

[Continue for all detected endpoints...]

## Error Handling
[Common error responses]

## Rate Limiting
[If applicable]

## Examples
[Usage examples in different languages]

Base this on the actual code structure and common patterns for the detected framework."""

    return call_openrouter_api(prompt)

def generate_setup_guide(project_info: Dict[str, Any]) -> str:
    """Generate detailed setup guide."""
    prompt = f"""Create a detailed SETUP.md guide for this project:

PROJECT INFO:
- Languages: {', '.join(project_info.get('languages', []))}
- Frameworks: {', '.join(project_info.get('frameworks', []))}
- Dependencies: {json.dumps(project_info.get('dependencies', {}), indent=2)}
- Config Files: {', '.join(project_info.get('config_files', []))}

Generate a comprehensive setup guide with:

# Setup Guide

## System Requirements
[OS, software versions]

## Step-by-Step Setup

### 1. Environment Setup
[Environment preparation]

### 2. Dependencies Installation
[How to install dependencies]

### 3. Configuration
[Environment variables, config files]

### 4. Database Setup
[If database detected]

### 5. First Run
[How to start the application]

## Development Setup
[Development-specific setup]

## Production Setup
[Production deployment]

## Troubleshooting
[Common issues and solutions]

## Verification
[How to verify everything works]

Make it beginner-friendly with clear commands and explanations."""

    return call_openrouter_api(prompt)

def format_file_structure(files: List[Dict[str, Any]]) -> str:
    """Format file structure for display."""
    structure = {}
    
    for file_info in files[:20]:  # Limit to first 20 files
        path_parts = file_info["path"].split(os.sep)
        current = structure
        
        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[path_parts[-1]] = f"({file_info.get('language', 'file')})"
    
    return json.dumps(structure, indent=2)

def format_backend_files(files: List[Dict[str, Any]]) -> str:
    """Format backend-related files."""
    backend_files = []
    
    for file_info in files:
        if file_info.get("language") in ["Python", "JavaScript", "TypeScript", "Java"]:
            backend_files.append(f"- {file_info['path']}: {len(file_info.get('functions', []))} functions, {len(file_info.get('classes', []))} classes")
    
    return "\n".join(backend_files[:10])  # Limit to 10 files

def save_documentation(project_path: str, docs: Dict[str, str]) -> Dict[str, str]:
    """Save generated documentation to files."""
    project_path = Path(project_path)
    saved_files = {}
    
    for doc_type, content in docs.items():
        if content and not content.startswith("Error:"):
            filename = f"{doc_type.upper()}.md"
            file_path = project_path / filename
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                saved_files[doc_type] = str(file_path)
            except Exception as e:
                saved_files[doc_type] = f"Error saving {filename}: {str(e)}"
    
    return saved_files

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python ai_docs.py <project_path>    # Generate docs for project")
        print("  python ai_docs.py --current         # Generate docs for current directory")
        sys.exit(1)
    
    if sys.argv[1] == "--current":
        project_path = "."
    elif sys.argv[1] in ["-h", "--help"]:
        print(__doc__)
        sys.exit(0)
    else:
        project_path = sys.argv[1]
    
    print(f"🔍 Scanning project: {project_path}")
    
    # Scan project
    project_info = scan_project(project_path)
    
    if "error" in project_info:
        print(f"❌ {project_info['error']}")
        sys.exit(1)
    
    print(f"✅ Found {len(project_info['files'])} files")
    print(f"📋 Languages: {', '.join(project_info['languages'])}")
    print(f"🛠️ Frameworks: {', '.join(project_info['frameworks'])}")
    
    # Generate documentation
    print("\n🤖 Generating documentation...")
    
    docs = {}
    
    # Always generate README
    print("  📄 Generating README.md...")
    docs["readme"] = generate_readme(project_info)
    
    # Generate API docs if backend detected
    if any(fw in ['FastAPI', 'Express.js', 'Django', 'Flask'] for fw in project_info['frameworks']):
        print("  🔌 Generating API documentation...")
        docs["api"] = generate_api_docs(project_info)
    
    # Generate setup guide
    print("  ⚙️ Generating setup guide...")
    docs["setup"] = generate_setup_guide(project_info)
    
    # Save documentation
    print("\n💾 Saving documentation...")
    saved_files = save_documentation(project_path, docs)
    
    for doc_type, file_path in saved_files.items():
        if file_path.startswith("Error"):
            print(f"  ❌ {file_path}")
        else:
            print(f"  ✅ {doc_type.upper()}: {file_path}")
    
    print(f"\n🎉 Documentation generation complete!")

if __name__ == "__main__":
    main()
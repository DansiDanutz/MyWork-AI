#!/usr/bin/env python3
"""
Deploy Helper
=============
One-command deploy to various platforms (Vercel, Railway, Render).
Auto-detects project type and generates appropriate config files.

Usage:
    python deploy.py <project_path> --platform vercel      # Deploy to Vercel
    python deploy.py <project_path> --platform railway     # Deploy to Railway
    python deploy.py <project_path> --platform render      # Deploy to Render
    python deploy.py --current --platform vercel           # Deploy current directory
    mw deploy <project> --platform vercel                  # Via CLI
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class ProjectDeployHelper:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.project_type = None
        self.framework = None
        self.language = None
        
        if not self.project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

    def detect_project_type(self) -> Dict[str, Any]:
        """Detect project type, framework, and language."""
        print("🔍 Detecting project type...")
        
        detection_result = {
            "type": "unknown",
            "framework": "none",
            "language": "unknown",
            "build_command": "",
            "start_command": "",
            "output_directory": "",
            "port": None
        }
        
        # Check for package.json (Node.js projects)
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    package_data = json.load(f)
                
                detection_result["language"] = "javascript"
                
                scripts = package_data.get("scripts", {})
                dependencies = package_data.get("dependencies", {})
                dev_dependencies = package_data.get("devDependencies", {})
                
                # Detect framework
                if "next" in dependencies:
                    detection_result.update({
                        "type": "frontend",
                        "framework": "nextjs",
                        "build_command": "npm run build",
                        "start_command": "npm start",
                        "output_directory": ".next"
                    })
                elif "react" in dependencies and "react-scripts" in dependencies:
                    detection_result.update({
                        "type": "frontend", 
                        "framework": "create-react-app",
                        "build_command": "npm run build",
                        "start_command": "npm start",
                        "output_directory": "build"
                    })
                elif "vue" in dependencies:
                    detection_result.update({
                        "type": "frontend",
                        "framework": "vue",
                        "build_command": "npm run build",
                        "start_command": "npm start",
                        "output_directory": "dist"
                    })
                elif "express" in dependencies:
                    detection_result.update({
                        "type": "backend",
                        "framework": "express",
                        "build_command": "",
                        "start_command": "npm start",
                        "port": 3000
                    })
                elif "vite" in dev_dependencies:
                    detection_result.update({
                        "type": "frontend",
                        "framework": "vite",
                        "build_command": "npm run build",
                        "start_command": "npm run preview",
                        "output_directory": "dist"
                    })
                elif "nuxt" in dependencies:
                    detection_result.update({
                        "type": "frontend",
                        "framework": "nuxt",
                        "build_command": "npm run build",
                        "start_command": "npm start",
                        "output_directory": ".output"
                    })
                
            except Exception as e:
                print(f"⚠️ Error reading package.json: {e}")
        
        # Check for Python projects
        elif (self.project_path / "requirements.txt").exists() or (self.project_path / "pyproject.toml").exists():
            detection_result["language"] = "python"
            
            # Check for specific Python frameworks
            requirements = []
            
            if (self.project_path / "requirements.txt").exists():
                try:
                    with open(self.project_path / "requirements.txt") as f:
                        requirements = [line.strip().split("==")[0].lower() for line in f 
                                     if line.strip() and not line.startswith("#")]
                except Exception:
                    pass
            
            if "fastapi" in requirements:
                detection_result.update({
                    "type": "backend",
                    "framework": "fastapi",
                    "build_command": "",
                    "start_command": "uvicorn main:app --host 0.0.0.0 --port $PORT",
                    "port": 8000
                })
            elif "django" in requirements:
                detection_result.update({
                    "type": "backend",
                    "framework": "django",
                    "build_command": "python manage.py collectstatic --noinput",
                    "start_command": "gunicorn myproject.wsgi --bind 0.0.0.0:$PORT",
                    "port": 8000
                })
            elif "flask" in requirements:
                detection_result.update({
                    "type": "backend",
                    "framework": "flask",
                    "build_command": "",
                    "start_command": "gunicorn app:app --bind 0.0.0.0:$PORT",
                    "port": 5000
                })
            elif "streamlit" in requirements:
                detection_result.update({
                    "type": "frontend",
                    "framework": "streamlit",
                    "build_command": "",
                    "start_command": "streamlit run app.py --server.port $PORT",
                    "port": 8501
                })
        
        # Check for Go projects
        elif (self.project_path / "go.mod").exists():
            detection_result.update({
                "language": "go",
                "type": "backend",
                "framework": "go",
                "build_command": "go build -o main .",
                "start_command": "./main",
                "port": 8080
            })
        
        # Check for static HTML projects
        elif (self.project_path / "index.html").exists():
            detection_result.update({
                "type": "frontend",
                "framework": "static",
                "language": "html",
                "build_command": "",
                "start_command": "",
                "output_directory": "."
            })
        
        self.project_type = detection_result["type"]
        self.framework = detection_result["framework"] 
        self.language = detection_result["language"]
        
        return detection_result

    def generate_vercel_config(self, project_info: Dict[str, Any]) -> str:
        """Generate vercel.json configuration."""
        config = {
            "version": 2,
        }
        
        if project_info["type"] == "frontend":
            if project_info["framework"] == "nextjs":
                # Next.js auto-detection, minimal config needed
                config = {
                    "framework": "nextjs"
                }
            elif project_info["framework"] == "create-react-app":
                config.update({
                    "builds": [
                        {
                            "src": "package.json",
                            "use": "@vercel/static-build",
                            "env": {
                                "ENABLE_FILE_SYSTEM_API": "1"
                            }
                        }
                    ],
                    "routes": [
                        {
                            "src": "/(.*)",
                            "dest": "/index.html"
                        }
                    ]
                })
            elif project_info["framework"] == "vite":
                config.update({
                    "buildCommand": "npm run build",
                    "outputDirectory": "dist",
                    "devCommand": "npm run dev"
                })
            elif project_info["framework"] == "static":
                config.update({
                    "builds": [
                        {
                            "src": "**/*",
                            "use": "@vercel/static"
                        }
                    ]
                })
        
        elif project_info["type"] == "backend":
            if project_info["framework"] == "express":
                config.update({
                    "builds": [
                        {
                            "src": "index.js",
                            "use": "@vercel/node"
                        }
                    ],
                    "routes": [
                        {
                            "src": "/(.*)",
                            "dest": "/index.js"
                        }
                    ]
                })
            elif project_info["framework"] == "fastapi":
                config.update({
                    "builds": [
                        {
                            "src": "main.py",
                            "use": "@vercel/python"
                        }
                    ],
                    "routes": [
                        {
                            "src": "/(.*)",
                            "dest": "/main.py"
                        }
                    ]
                })
        
        return json.dumps(config, indent=2)

    def generate_railway_config(self, project_info: Dict[str, Any]) -> Dict[str, str]:
        """Generate Railway configuration files."""
        configs = {}
        
        # railway.json
        railway_config = {
            "build": {
                "builder": "NIXPACKS"
            },
            "deploy": {
                "startCommand": project_info["start_command"],
                "healthcheckPath": "/health" if project_info["type"] == "backend" else None
            }
        }
        
        if project_info["build_command"]:
            railway_config["build"]["buildCommand"] = project_info["build_command"]
        
        configs["railway.json"] = json.dumps(railway_config, indent=2)
        
        # Dockerfile (optional, for more control)
        if project_info["language"] == "python":
            dockerfile = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE $PORT

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
"""
            configs["Dockerfile"] = dockerfile
            
        elif project_info["language"] == "javascript":
            dockerfile = f"""FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

{f'RUN {project_info["build_command"]}' if project_info["build_command"] else ''}

EXPOSE $PORT

CMD {json.dumps(project_info["start_command"].split())}
"""
            configs["Dockerfile"] = dockerfile
        
        return configs

    def generate_render_config(self, project_info: Dict[str, Any]) -> str:
        """Generate render.yaml configuration."""
        if project_info["type"] == "frontend":
            service_type = "static_site"
            config = {
                "services": [
                    {
                        "type": service_type,
                        "name": self.project_path.name,
                        "env": "static",
                        "buildCommand": project_info["build_command"] or "npm install && npm run build",
                        "publishDir": project_info["output_directory"] or "build"
                    }
                ]
            }
        else:
            service_type = "web_service"
            config = {
                "services": [
                    {
                        "type": service_type,
                        "name": self.project_path.name,
                        "env": "docker" if (self.project_path / "Dockerfile").exists() else "python",
                        "buildCommand": project_info["build_command"],
                        "startCommand": project_info["start_command"],
                        "plan": "free"
                    }
                ]
            }
        
        # Add environment variables section
        config["services"][0]["envVars"] = [
            {
                "key": "NODE_ENV",
                "value": "production"
            }
        ]
        
        import yaml
        return yaml.dump(config, default_flow_style=False)

    def create_config_files(self, platform: str, project_info: Dict[str, Any]) -> List[str]:
        """Create configuration files for the specified platform."""
        created_files = []
        
        if platform == "vercel":
            vercel_config = self.generate_vercel_config(project_info)
            vercel_path = self.project_path / "vercel.json"
            
            with open(vercel_path, 'w') as f:
                f.write(vercel_config)
            created_files.append("vercel.json")
            
        elif platform == "railway":
            configs = self.generate_railway_config(project_info)
            
            for filename, content in configs.items():
                file_path = self.project_path / filename
                with open(file_path, 'w') as f:
                    f.write(content)
                created_files.append(filename)
                
        elif platform == "render":
            try:
                import yaml
                render_config = self.generate_render_config(project_info)
                render_path = self.project_path / "render.yaml"
                
                with open(render_path, 'w') as f:
                    f.write(render_config)
                created_files.append("render.yaml")
            except ImportError:
                print("⚠️ PyYAML not installed. Install with: pip install PyYAML")
                return []
        
        return created_files

    def check_deployment_readiness(self, project_info: Dict[str, Any]) -> List[str]:
        """Check if project is ready for deployment."""
        issues = []
        
        # Check for environment variables
        env_files = ['.env.example', '.env.template']
        if not any((self.project_path / env).exists() for env in env_files):
            issues.append("Consider adding .env.example to document required environment variables")
        
        # Check for .gitignore
        if not (self.project_path / '.gitignore').exists():
            issues.append("Add .gitignore file to exclude sensitive files")
        
        # Framework-specific checks
        if project_info["framework"] == "nextjs":
            if not (self.project_path / 'next.config.js').exists():
                issues.append("Consider adding next.config.js for configuration")
                
        elif project_info["framework"] == "fastapi":
            # Check for main.py or app.py
            if not (self.project_path / 'main.py').exists() and not (self.project_path / 'app.py').exists():
                issues.append("FastAPI projects typically need main.py or app.py")
                
        elif project_info["framework"] == "express":
            # Check for main entry file
            package_json = self.project_path / "package.json"
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        data = json.load(f)
                    main_file = data.get('main', 'index.js')
                    if not (self.project_path / main_file).exists():
                        issues.append(f"Main file {main_file} not found")
                except Exception:
                    pass
        
        # Check for package-lock.json or yarn.lock for Node.js projects
        if (self.project_path / 'package.json').exists():
            lock_files = ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml']
            if not any((self.project_path / lock).exists() for lock in lock_files):
                issues.append("Add package-lock.json or yarn.lock for consistent dependencies")
        
        return issues

    def get_deployment_instructions(self, platform: str, project_info: Dict[str, Any]) -> List[str]:
        """Get deployment instructions for the platform."""
        instructions = []
        
        if platform == "vercel":
            instructions = [
                "🚀 **Deploy to Vercel:**",
                "",
                "1. Install Vercel CLI:",
                "   ```bash",
                "   npm install -g vercel",
                "   ```",
                "",
                "2. Login to Vercel:",
                "   ```bash", 
                "   vercel login",
                "   ```",
                "",
                "3. Deploy:",
                "   ```bash",
                "   vercel",
                "   ```",
                "",
                "4. For production deployment:",
                "   ```bash",
                "   vercel --prod",
                "   ```",
                "",
                "📝 **Alternative: GitHub Integration**",
                "1. Push your code to GitHub",
                "2. Connect repository at https://vercel.com/dashboard",
                "3. Automatic deployments on every push!"
            ]
            
        elif platform == "railway":
            instructions = [
                "🚀 **Deploy to Railway:**",
                "",
                "1. Install Railway CLI:",
                "   ```bash",
                "   npm install -g @railway/cli",
                "   ```",
                "",
                "2. Login to Railway:",
                "   ```bash",
                "   railway login",
                "   ```",
                "",
                "3. Initialize and deploy:",
                "   ```bash",
                "   railway link  # Link to existing project or create new",
                "   railway up    # Deploy",
                "   ```",
                "",
                "📝 **Alternative: GitHub Integration**",
                "1. Push code to GitHub",
                "2. Connect repository at https://railway.app/dashboard",
                "3. Automatic deployments on every push!"
            ]
            
        elif platform == "render":
            instructions = [
                "🚀 **Deploy to Render:**",
                "",
                "1. Push your code to GitHub",
                "2. Go to https://dashboard.render.com",
                "3. Click 'New +' and select 'Web Service'",
                "4. Connect your GitHub repository",
                f"5. Render will auto-detect your {project_info['framework']} app",
                "6. Configure environment variables if needed",
                "7. Click 'Deploy Web Service'",
                "",
                "📝 **Manual Configuration:**",
                f"- Build Command: {project_info['build_command'] or 'Auto-detected'}",
                f"- Start Command: {project_info['start_command'] or 'Auto-detected'}"
            ]
        
        return instructions

def print_project_info(project_info: Dict[str, Any]):
    """Print detected project information."""
    print(f"\n📊 **Project Analysis:**")
    print(f"Type: {project_info['type'].title()}")
    print(f"Framework: {project_info['framework'].title().replace('_', ' ')}")
    print(f"Language: {project_info['language'].title()}")
    
    if project_info['build_command']:
        print(f"Build Command: {project_info['build_command']}")
    if project_info['start_command']:
        print(f"Start Command: {project_info['start_command']}")
    if project_info['output_directory']:
        print(f"Output Directory: {project_info['output_directory']}")
    if project_info['port']:
        print(f"Default Port: {project_info['port']}")

def main():
    """Main function."""
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python deploy.py <project_path> --platform <vercel|railway|render>")
        print("  python deploy.py --current --platform <platform>")
        print("  python deploy.py --help")
        sys.exit(1)
    
    if sys.argv[1] == "--help":
        print(__doc__)
        sys.exit(0)
    
    # Parse arguments
    if sys.argv[1] == "--current":
        project_path = "."
        platform_arg = sys.argv[2]
    else:
        project_path = sys.argv[1]
        platform_arg = sys.argv[2]
    
    if platform_arg != "--platform" or len(sys.argv) < 4:
        print("Error: --platform flag required")
        sys.exit(1)
    
    platform = sys.argv[3].lower()
    if platform not in ["vercel", "railway", "render"]:
        print("Error: Platform must be one of: vercel, railway, render")
        sys.exit(1)
    
    try:
        # Initialize deploy helper
        deployer = ProjectDeployHelper(project_path)
        
        # Detect project type
        project_info = deployer.detect_project_type()
        print_project_info(project_info)
        
        if project_info["type"] == "unknown":
            print("\n⚠️ **Warning:** Could not auto-detect project type.")
            print("You may need to manually configure deployment settings.")
        
        # Check deployment readiness
        issues = deployer.check_deployment_readiness(project_info)
        if issues:
            print(f"\n⚠️ **Deployment Readiness Issues:**")
            for issue in issues:
                print(f"  - {issue}")
            print()
        
        # Create configuration files
        print(f"\n⚙️ **Generating {platform.title()} configuration...**")
        created_files = deployer.create_config_files(platform, project_info)
        
        if created_files:
            print("✅ Created configuration files:")
            for file in created_files:
                print(f"  - {file}")
        else:
            print("❌ Failed to create configuration files")
            sys.exit(1)
        
        # Show deployment instructions
        instructions = deployer.get_deployment_instructions(platform, project_info)
        print(f"\n{chr(10).join(instructions)}")
        
        print(f"\n🎉 **Ready to deploy to {platform.title()}!**")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
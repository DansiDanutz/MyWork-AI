#!/usr/bin/env python3
"""
Project Comparison Tool
======================
Compare two projects side by side (file count, test count, dependencies, size).

Usage:
    python3 project_compare.py <project1> <project2>
    python3 project_compare.py --help

Examples:
    python3 project_compare.py my-api blog-platform
    python3 project_compare.py ../project1 /path/to/project2
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from config import MYWORK_ROOT, PROJECTS_DIR
except ImportError:
    def _get_mywork_root() -> Path:
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        if script_dir.name == "tools":
            potential_root = script_dir.parent
            if (potential_root / "CLAUDE.md").exists():
                return potential_root
        return Path.home() / "MyWork"
    
    MYWORK_ROOT = _get_mywork_root()
    PROJECTS_DIR = MYWORK_ROOT / "projects"

class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"

def color(text: str, color_code: str) -> str:
    """Apply color to text."""
    return f"{color_code}{text}{Colors.ENDC}"

def analyze_project(project_path: Path) -> Dict[str, Any]:
    """Analyze a single project and return metrics."""
    if not project_path.exists():
        return {"error": f"Project not found: {project_path}"}
    
    if not project_path.is_dir():
        return {"error": f"Not a directory: {project_path}"}
    
    metrics = {
        "name": project_path.name,
        "path": str(project_path),
        "total_files": 0,
        "total_lines": 0,
        "file_types": {},
        "test_files": 0,
        "test_lines": 0,
        "dependencies": {},
        "size_mb": 0.0,
        "git_commits": 0,
        "has_readme": False,
        "has_tests": False,
        "has_ci": False,
        "languages": [],
        "structure": {}
    }
    
    # Count files and analyze structure
    for root, dirs, files in os.walk(project_path):
        # Skip common ignore directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env', 'dist', 'build']]
        
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(project_path)
            
            # Count total files
            metrics["total_files"] += 1
            
            # File extension analysis
            ext = file_path.suffix.lower()
            if ext:
                metrics["file_types"][ext] = metrics["file_types"].get(ext, 0) + 1
            
            # Count lines for text files
            if ext in ['.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.html', '.css', '.scss', '.md', '.txt', '.json', '.yaml', '.yml']:
                try:
                    lines = len(file_path.read_text(encoding='utf-8', errors='ignore').splitlines())
                    metrics["total_lines"] += lines
                    
                    # Test file detection
                    if any(test_keyword in file.lower() for test_keyword in ['test_', '_test', 'spec_', '_spec', 'tests']):
                        metrics["test_files"] += 1
                        metrics["test_lines"] += lines
                        metrics["has_tests"] = True
                except:
                    continue
        
        # Check for README
        for file in files:
            if file.lower().startswith('readme'):
                metrics["has_readme"] = True
    
    # Detect dependencies
    dep_files = {
        'package.json': 'nodejs',
        'requirements.txt': 'python',
        'pyproject.toml': 'python',
        'Pipfile': 'python',
        'Gemfile': 'ruby',
        'composer.json': 'php',
        'pom.xml': 'java',
        'build.gradle': 'java',
        'Cargo.toml': 'rust',
        'go.mod': 'go'
    }
    
    for dep_file, lang in dep_files.items():
        dep_path = project_path / dep_file
        if dep_path.exists():
            metrics["languages"].append(lang)
            try:
                if dep_file == 'package.json':
                    pkg_data = json.loads(dep_path.read_text())
                    deps = list((pkg_data.get('dependencies', {}).keys())) + list(pkg_data.get('devDependencies', {}).keys())
                    metrics["dependencies"]['nodejs'] = deps
                elif dep_file == 'requirements.txt':
                    deps = [line.split('==')[0].split('>=')[0].strip() for line in dep_path.read_text().splitlines() if line.strip() and not line.startswith('#')]
                    metrics["dependencies"]['python'] = deps
            except:
                pass
    
    # Check for CI configuration
    ci_indicators = [
        '.github/workflows',
        '.gitlab-ci.yml',
        'bitbucket-pipelines.yml',
        'Jenkinsfile',
        '.travis.yml',
        'circle.yml'
    ]
    
    for ci_path in ci_indicators:
        if (project_path / ci_path).exists():
            metrics["has_ci"] = True
            break
    
    # Get project size
    try:
        result = subprocess.run(['du', '-sm', str(project_path)], capture_output=True, text=True)
        if result.returncode == 0:
            metrics["size_mb"] = float(result.stdout.split()[0])
    except:
        pass
    
    # Get git commit count
    try:
        if (project_path / '.git').exists():
            result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], cwd=project_path, capture_output=True, text=True)
            if result.returncode == 0:
                metrics["git_commits"] = int(result.stdout.strip())
    except:
        pass
    
    # Detect primary language
    if metrics["file_types"]:
        # Map extensions to languages
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.vue': 'Vue.js'
        }
        
        lang_counts = {}
        for ext, count in metrics["file_types"].items():
            lang = lang_map.get(ext, ext[1:] if ext.startswith('.') else ext)
            lang_counts[lang] = lang_counts.get(lang, 0) + count
        
        if lang_counts:
            primary_lang = max(lang_counts.items(), key=lambda x: x[1])[0]
            if primary_lang not in metrics["languages"]:
                metrics["languages"].insert(0, primary_lang)
    
    return metrics

def format_number(num: int) -> str:
    """Format number with commas."""
    return f"{num:,}"

def format_size(size_mb: float) -> str:
    """Format size in human readable format."""
    if size_mb < 1:
        return f"{size_mb * 1024:.0f}KB"
    elif size_mb < 1024:
        return f"{size_mb:.1f}MB"
    else:
        return f"{size_mb / 1024:.1f}GB"

def print_comparison(project1: Dict[str, Any], project2: Dict[str, Any]) -> None:
    """Print detailed comparison of two projects."""
    
    if "error" in project1:
        print(f"{Colors.RED}Error analyzing project 1: {project1['error']}{Colors.ENDC}")
        return
    
    if "error" in project2:
        print(f"{Colors.RED}Error analyzing project 2: {project2['error']}{Colors.ENDC}")
        return
    
    print(f"{Colors.BOLD}{Colors.BLUE}📊 Project Comparison{Colors.ENDC}")
    print(f"{Colors.BLUE}{'=' * 80}{Colors.ENDC}")
    
    # Header
    print(f"\n{Colors.BOLD}{'Metric':<25} {'Project 1':<25} {'Project 2':<25} {'Winner':<10}{Colors.ENDC}")
    print("-" * 85)
    
    # Helper function to determine winner
    def winner_indicator(val1, val2, higher_is_better=True):
        if val1 == val2:
            return "📊 Tie"
        elif (val1 > val2) == higher_is_better:
            return f"{Colors.GREEN}👑 Left{Colors.ENDC}"
        else:
            return f"{Colors.GREEN}👑 Right{Colors.ENDC}"
    
    # Project names
    print(f"{'📂 Name':<25} {project1['name']:<25} {project2['name']:<25} {'':<10}")
    
    # File metrics
    print(f"{'📄 Total Files':<25} {format_number(project1['total_files']):<25} {format_number(project2['total_files']):<25} {winner_indicator(project1['total_files'], project2['total_files'])}")
    print(f"{'📝 Total Lines':<25} {format_number(project1['total_lines']):<25} {format_number(project2['total_lines']):<25} {winner_indicator(project1['total_lines'], project2['total_lines'])}")
    print(f"{'✅ Test Files':<25} {format_number(project1['test_files']):<25} {format_number(project2['test_files']):<25} {winner_indicator(project1['test_files'], project2['test_files'])}")
    print(f"{'🧪 Test Lines':<25} {format_number(project1['test_lines']):<25} {format_number(project2['test_lines']):<25} {winner_indicator(project1['test_lines'], project2['test_lines'])}")
    
    # Size and commits
    print(f"{'💽 Size':<25} {format_size(project1['size_mb']):<25} {format_size(project2['size_mb']):<25} {winner_indicator(project1['size_mb'], project2['size_mb'], False)}")
    print(f"{'🔄 Git Commits':<25} {format_number(project1['git_commits']):<25} {format_number(project2['git_commits']):<25} {winner_indicator(project1['git_commits'], project2['git_commits'])}")
    
    # Quality indicators
    readme1 = "✅" if project1['has_readme'] else "❌"
    readme2 = "✅" if project2['has_readme'] else "❌"
    print(f"{'📖 Has README':<25} {readme1:<25} {readme2:<25} {'':<10}")
    
    tests1 = "✅" if project1['has_tests'] else "❌"
    tests2 = "✅" if project2['has_tests'] else "❌"
    print(f"{'🧪 Has Tests':<25} {tests1:<25} {tests2:<25} {'':<10}")
    
    ci1 = "✅" if project1['has_ci'] else "❌"
    ci2 = "✅" if project2['has_ci'] else "❌"
    print(f"{'🔄 Has CI':<25} {ci1:<25} {ci2:<25} {'':<10}")
    
    # Languages
    langs1 = ", ".join(project1['languages'][:3]) if project1['languages'] else "None detected"
    langs2 = ", ".join(project2['languages'][:3]) if project2['languages'] else "None detected"
    print(f"{'💻 Languages':<25} {langs1:<25} {langs2:<25} {'':<10}")
    
    # File type breakdown
    print(f"\n{Colors.BOLD}📁 File Type Breakdown:{Colors.ENDC}")
    all_extensions = set(project1['file_types'].keys()) | set(project2['file_types'].keys())
    
    if all_extensions:
        print(f"{'Extension':<15} {'Project 1':<15} {'Project 2':<15}")
        print("-" * 45)
        for ext in sorted(all_extensions):
            count1 = project1['file_types'].get(ext, 0)
            count2 = project2['file_types'].get(ext, 0)
            print(f"{ext:<15} {count1:<15} {count2:<15}")
    
    # Dependencies
    print(f"\n{Colors.BOLD}📦 Dependencies:{Colors.ENDC}")
    all_langs = set(project1['dependencies'].keys()) | set(project2['dependencies'].keys())
    
    if all_langs:
        for lang in all_langs:
            deps1 = project1['dependencies'].get(lang, [])
            deps2 = project2['dependencies'].get(lang, [])
            
            print(f"\n{Colors.BLUE}{lang.title()}:{Colors.ENDC}")
            print(f"  Project 1: {len(deps1)} dependencies")
            print(f"  Project 2: {len(deps2)} dependencies")
            
            # Show common dependencies
            common_deps = set(deps1) & set(deps2)
            if common_deps:
                print(f"  Common: {', '.join(sorted(list(common_deps))[:5])}")
                if len(common_deps) > 5:
                    print(f"          ... and {len(common_deps) - 5} more")
    else:
        print("  No dependency files detected in either project")
    
    # Summary
    print(f"\n{Colors.BOLD}🏆 Summary:{Colors.ENDC}")
    
    score1 = 0
    score2 = 0
    
    # Calculate simple scores
    metrics_to_score = [
        ('total_files', True),
        ('total_lines', True),
        ('test_files', True),
        ('git_commits', True),
        ('has_readme', True),
        ('has_tests', True),
        ('has_ci', True)
    ]
    
    for metric, higher_is_better in metrics_to_score:
        val1 = project1.get(metric, 0)
        val2 = project2.get(metric, 0)
        
        if isinstance(val1, bool):
            val1 = int(val1)
            val2 = int(val2)
        
        if val1 != val2:
            if (val1 > val2) == higher_is_better:
                score1 += 1
            else:
                score2 += 1
    
    print(f"  {project1['name']}: {score1}/{len(metrics_to_score)} points")
    print(f"  {project2['name']}: {score2}/{len(metrics_to_score)} points")
    
    if score1 > score2:
        print(f"  🏆 {Colors.GREEN}{project1['name']} wins!{Colors.ENDC}")
    elif score2 > score1:
        print(f"  🏆 {Colors.GREEN}{project2['name']} wins!{Colors.ENDC}")
    else:
        print(f"  🤝 {Colors.YELLOW}It's a tie!{Colors.ENDC}")

def resolve_project_path(project_name: str) -> Optional[Path]:
    """Resolve project name to full path."""
    # If it's already a path, use it
    project_path = Path(project_name)
    if project_path.exists():
        return project_path.resolve()
    
    # Try in projects directory
    projects_path = PROJECTS_DIR / project_name
    if projects_path.exists():
        return projects_path
    
    # Try relative to current directory
    current_path = Path.cwd() / project_name
    if current_path.exists():
        return current_path
    
    return None

def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    
    if sys.argv[1] in ["--help", "-h"]:
        print(__doc__)
        return 0
    
    project1_name = sys.argv[1]
    project2_name = sys.argv[2]
    
    # Resolve project paths
    project1_path = resolve_project_path(project1_name)
    project2_path = resolve_project_path(project2_name)
    
    if not project1_path:
        print(f"{Colors.RED}❌ Project not found: {project1_name}{Colors.ENDC}")
        return 1
    
    if not project2_path:
        print(f"{Colors.RED}❌ Project not found: {project2_name}{Colors.ENDC}")
        return 1
    
    print(f"{Colors.BOLD}🔍 Analyzing projects...{Colors.ENDC}")
    print(f"  Project 1: {project1_path}")
    print(f"  Project 2: {project2_path}")
    
    # Analyze both projects
    project1_metrics = analyze_project(project1_path)
    project2_metrics = analyze_project(project2_path)
    
    # Print comparison
    print_comparison(project1_metrics, project2_metrics)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
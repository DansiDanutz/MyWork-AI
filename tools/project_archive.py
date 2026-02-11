#!/usr/bin/env python3
"""
Project Archiver
================
Archive a project to zip with metadata.

Usage:
    python3 project_archive.py <project-name> [options]
    python3 project_archive.py --help

Options:
    --output <path>      Output archive path (default: ./archives/)
    --include-git        Include .git directory in archive
    --exclude <pattern>  Exclude files matching pattern (can be used multiple times)
    --compress-level <n> Compression level 0-9 (default: 6)
    --metadata-only      Only generate metadata, don't create archive
    --help               Show this help

Examples:
    python3 project_archive.py my-api
    python3 project_archive.py blog-platform --output /backups/
    python3 project_archive.py my-app --include-git --compress-level 9
    python3 project_archive.py test-project --exclude "*.log" --exclude "node_modules"
"""

import os
import sys
import json
import zipfile
import shutil
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

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

class ProjectArchiver:
    """Archive projects with comprehensive metadata."""
    
    def __init__(self):
        self.exclude_patterns = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".DS_Store",
            "Thumbs.db",
            "*.log",
            ".coverage",
            "htmlcov",
            ".pytest_cache",
            ".tox",
            "venv",
            "env",
            ".venv",
            ".env",
            "node_modules",
            "dist",
            "build",
            "*.egg-info"
        ]
    
    def should_exclude(self, file_path: Path, custom_excludes: List[str] = None) -> bool:
        """Check if a file should be excluded from the archive."""
        excludes = self.exclude_patterns + (custom_excludes or [])
        
        # Check against each exclude pattern
        for pattern in excludes:
            if pattern.startswith("*."):
                # File extension pattern
                if file_path.name.endswith(pattern[1:]):
                    return True
            elif pattern in str(file_path):
                # Path contains pattern
                return True
            elif file_path.name == pattern:
                # Exact filename match
                return True
        
        return False
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""
    
    def get_git_info(self, project_path: Path) -> Dict[str, Any]:
        """Get git repository information."""
        git_info = {
            "is_git_repo": False,
            "current_branch": "",
            "current_commit": "",
            "remote_url": "",
            "total_commits": 0,
            "uncommitted_changes": False,
            "last_commit_date": "",
            "contributors": []
        }
        
        if not (project_path / ".git").exists():
            return git_info
        
        git_info["is_git_repo"] = True
        
        try:
            # Current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=project_path, capture_output=True, text=True
            )
            if result.returncode == 0:
                git_info["current_branch"] = result.stdout.strip()
            
            # Current commit
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=project_path, capture_output=True, text=True
            )
            if result.returncode == 0:
                git_info["current_commit"] = result.stdout.strip()
            
            # Remote URL
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=project_path, capture_output=True, text=True
            )
            if result.returncode == 0:
                git_info["remote_url"] = result.stdout.strip()
            
            # Total commits
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=project_path, capture_output=True, text=True
            )
            if result.returncode == 0:
                git_info["total_commits"] = int(result.stdout.strip())
            
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_path, capture_output=True, text=True
            )
            if result.returncode == 0:
                git_info["uncommitted_changes"] = bool(result.stdout.strip())
            
            # Last commit date
            result = subprocess.run(
                ["git", "log", "-1", "--format=%cd", "--date=iso"],
                cwd=project_path, capture_output=True, text=True
            )
            if result.returncode == 0:
                git_info["last_commit_date"] = result.stdout.strip()
            
            # Contributors
            result = subprocess.run(
                ["git", "log", "--format=%an <%ae>", "--all"],
                cwd=project_path, capture_output=True, text=True
            )
            if result.returncode == 0:
                contributors = list(set(result.stdout.strip().split('\n')))
                git_info["contributors"] = [c for c in contributors if c.strip()]
        
        except Exception:
            pass
        
        return git_info
    
    def get_project_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Get project dependencies information."""
        deps_info = {
            "python": {},
            "nodejs": {},
            "other": {}
        }
        
        # Python dependencies
        requirements_txt = project_path / "requirements.txt"
        if requirements_txt.exists():
            try:
                deps = []
                for line in requirements_txt.read_text().splitlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        deps.append(line)
                deps_info["python"]["requirements_txt"] = deps
            except Exception:
                pass
        
        pyproject_toml = project_path / "pyproject.toml"
        if pyproject_toml.exists():
            deps_info["python"]["has_pyproject_toml"] = True
        
        # Node.js dependencies
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                package_data = json.loads(package_json.read_text())
                deps_info["nodejs"]["name"] = package_data.get("name", "")
                deps_info["nodejs"]["version"] = package_data.get("version", "")
                deps_info["nodejs"]["dependencies"] = list(package_data.get("dependencies", {}).keys())
                deps_info["nodejs"]["dev_dependencies"] = list(package_data.get("devDependencies", {}).keys())
                deps_info["nodejs"]["scripts"] = list(package_data.get("scripts", {}).keys())
            except Exception:
                pass
        
        # Other dependency files
        for dep_file in ["Gemfile", "composer.json", "pom.xml", "build.gradle", "Cargo.toml", "go.mod"]:
            if (project_path / dep_file).exists():
                deps_info["other"][dep_file] = True
        
        return deps_info
    
    def analyze_project_structure(self, project_path: Path, include_git: bool = False, 
                                 custom_excludes: List[str] = None) -> Dict[str, Any]:
        """Analyze project structure and generate metadata."""
        print(f"   🔍 Analyzing project structure...")
        
        analysis = {
            "project_name": project_path.name,
            "project_path": str(project_path),
            "archive_timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "total_size_bytes": 0,
            "file_types": {},
            "directory_structure": {},
            "git_info": self.get_git_info(project_path),
            "dependencies": self.get_project_dependencies(project_path),
            "files": []
        }
        
        # Walk through all files
        for root, dirs, files in os.walk(project_path):
            # Skip .git if not including it
            if not include_git and '.git' in dirs:
                dirs.remove('.git')
            
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not self.should_exclude(Path(root) / d, custom_excludes)]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(project_path)
                
                # Skip excluded files
                if self.should_exclude(file_path, custom_excludes):
                    continue
                
                try:
                    file_stat = file_path.stat()
                    file_size = file_stat.st_size
                    file_ext = file_path.suffix.lower()
                    
                    analysis["total_files"] += 1
                    analysis["total_size_bytes"] += file_size
                    
                    # Track file types
                    if file_ext:
                        analysis["file_types"][file_ext] = analysis["file_types"].get(file_ext, 0) + 1
                    
                    # Add to files list
                    file_info = {
                        "path": str(rel_path),
                        "size_bytes": file_size,
                        "modified_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        "sha256": self.calculate_file_hash(file_path) if file_size < 50 * 1024 * 1024 else ""  # Skip hash for large files
                    }
                    analysis["files"].append(file_info)
                
                except Exception:
                    continue
        
        # Build directory structure
        dirs_found = set()
        for file_info in analysis["files"]:
            path_parts = Path(file_info["path"]).parts
            for i in range(1, len(path_parts)):
                dir_path = "/".join(path_parts[:i])
                dirs_found.add(dir_path)
        
        analysis["directory_structure"] = {
            "total_directories": len(dirs_found),
            "directories": sorted(list(dirs_found))
        }
        
        return analysis
    
    def create_archive(self, project_path: Path, output_path: Path, 
                      include_git: bool = False, custom_excludes: List[str] = None,
                      compression_level: int = 6) -> Tuple[Path, Dict[str, Any]]:
        """Create project archive with metadata."""
        
        if not project_path.exists() or not project_path.is_dir():
            raise ValueError(f"Project path does not exist or is not a directory: {project_path}")
        
        # Generate metadata
        metadata = self.analyze_project_structure(project_path, include_git, custom_excludes)
        
        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate archive filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{project_path.name}_{timestamp}.zip"
        archive_path = output_path / archive_name
        
        print(f"   📦 Creating archive: {archive_path}")
        
        # Create zip archive
        with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED, 
                           compresslevel=compression_level) as zipf:
            
            # Add metadata file
            metadata_json = json.dumps(metadata, indent=2)
            zipf.writestr(f"{project_path.name}/ARCHIVE_METADATA.json", metadata_json)
            
            # Add all project files
            files_added = 0
            for root, dirs, files in os.walk(project_path):
                # Skip .git if not including it
                if not include_git and '.git' in dirs:
                    dirs.remove('.git')
                
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not self.should_exclude(Path(root) / d, custom_excludes)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Skip excluded files
                    if self.should_exclude(file_path, custom_excludes):
                        continue
                    
                    try:
                        # Calculate relative path for archive
                        rel_path = file_path.relative_to(project_path)
                        archive_file_path = f"{project_path.name}/{rel_path}"
                        
                        # Add file to archive
                        zipf.write(file_path, archive_file_path)
                        files_added += 1
                        
                        if files_added % 100 == 0:
                            print(f"     Added {files_added} files...")
                    
                    except Exception as e:
                        print(f"     Warning: Could not add {file_path}: {e}")
        
        # Final stats
        archive_stat = archive_path.stat()
        compression_ratio = (1 - archive_stat.st_size / metadata["total_size_bytes"]) * 100 if metadata["total_size_bytes"] > 0 else 0
        
        final_metadata = {
            **metadata,
            "archive_info": {
                "archive_path": str(archive_path),
                "archive_size_bytes": archive_stat.st_size,
                "files_archived": files_added,
                "compression_ratio_percent": round(compression_ratio, 1),
                "compression_level": compression_level
            }
        }
        
        # Save standalone metadata file
        metadata_path = output_path / f"{project_path.name}_{timestamp}_metadata.json"
        metadata_path.write_text(json.dumps(final_metadata, indent=2))
        
        print(f"   ✅ Archive created successfully!")
        print(f"   📁 Archive: {archive_path}")
        print(f"   📊 Metadata: {metadata_path}")
        print(f"   📦 Files archived: {files_added}")
        print(f"   💾 Original size: {metadata['total_size_bytes'] / 1024 / 1024:.1f} MB")
        print(f"   🗜️  Archive size: {archive_stat.st_size / 1024 / 1024:.1f} MB")
        print(f"   📉 Compression: {compression_ratio:.1f}%")
        
        return archive_path, final_metadata
    
    def generate_metadata_only(self, project_path: Path, output_path: Path,
                             include_git: bool = False, custom_excludes: List[str] = None) -> Path:
        """Generate only metadata without creating archive."""
        
        if not project_path.exists() or not project_path.is_dir():
            raise ValueError(f"Project path does not exist or is not a directory: {project_path}")
        
        # Generate metadata
        metadata = self.analyze_project_structure(project_path, include_git, custom_excludes)
        
        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate metadata filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metadata_name = f"{project_path.name}_{timestamp}_metadata.json"
        metadata_path = output_path / metadata_name
        
        # Save metadata file
        metadata_path.write_text(json.dumps(metadata, indent=2))
        
        print(f"   ✅ Metadata generated successfully!")
        print(f"   📊 Metadata: {metadata_path}")
        print(f"   📦 Total files: {metadata['total_files']}")
        print(f"   💾 Total size: {metadata['total_size_bytes'] / 1024 / 1024:.1f} MB")
        
        return metadata_path

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
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Archive a project to zip with comprehensive metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 project_archive.py my-api
    python3 project_archive.py blog-platform --output /backups/
    python3 project_archive.py my-app --include-git --compress-level 9
    python3 project_archive.py test-project --exclude "*.log" --exclude "node_modules"
"""
    )
    
    parser.add_argument("project", help="Project name or path to archive")
    parser.add_argument("--output", default="./archives", help="Output directory for archives (default: ./archives)")
    parser.add_argument("--include-git", action="store_true", help="Include .git directory in archive")
    parser.add_argument("--exclude", action="append", default=[], help="Exclude files matching pattern (can be used multiple times)")
    parser.add_argument("--compress-level", type=int, default=6, choices=range(0, 10), 
                       help="Compression level 0-9 (default: 6)")
    parser.add_argument("--metadata-only", action="store_true", help="Only generate metadata, don't create archive")
    
    args = parser.parse_args()
    
    # Resolve project path
    project_path = resolve_project_path(args.project)
    if not project_path:
        print(f"{color('❌ Project not found:', Colors.RED)} {args.project}")
        return 1
    
    output_path = Path(args.output)
    
    print(f"{color('📦 Project Archiver', Colors.BOLD)}")
    print(f"   Project: {project_path}")
    print(f"   Output: {output_path}")
    
    if args.include_git:
        print(f"   Including .git directory")
    
    if args.exclude:
        print(f"   Excluding patterns: {', '.join(args.exclude)}")
    
    try:
        archiver = ProjectArchiver()
        
        if args.metadata_only:
            metadata_path = archiver.generate_metadata_only(
                project_path, output_path, args.include_git, args.exclude
            )
        else:
            archive_path, metadata = archiver.create_archive(
                project_path, output_path, args.include_git, 
                args.exclude, args.compress_level
            )
        
        return 0
        
    except Exception as e:
        print(f"{color('❌ Error:', Colors.RED)} {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Project Health Scorer
=====================
Analyzes a project and scores its health based on various criteria.

Scoring Criteria (Total: 100 points):
- Has README (10 points)
- Has tests (15 points)
- Has CI/CD config (10 points)
- Code quality (20 points)
- Documentation (15 points)
- Security (15 points)
- Dependencies up to date (15 points)

Usage:
    python project_health.py <project_path>     # Score specific project
    python project_health.py --current          # Score current directory
    mw health <project>                          # Via CLI
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta

# File patterns and configurations
README_FILES = {'readme.md', 'readme.txt', 'readme.rst', 'readme'}
TEST_DIRS = {'test', 'tests', '__tests__', 'spec', 'specs'}
TEST_FILES = {'test_*.py', '*_test.py', '*.test.js', '*.test.ts', '*.spec.js', '*.spec.ts'}
CI_FILES = {'.github/workflows', '.gitlab-ci.yml', '.travis.yml', 'circle.yml', '.circleci', 
           'jenkinsfile', 'azure-pipelines.yml', '.buildkite'}
SECURITY_FILES = {'.github/dependabot.yml', '.snyk', 'security.md', '.security.md'}
DOC_DIRS = {'docs', 'doc', 'documentation'}
CONFIG_FILES = {'package.json', 'requirements.txt', 'cargo.toml', 'pom.xml', 'go.mod', 'composer.json'}

class ProjectHealthScorer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.score = 0
        self.max_score = 100
        self.results = {}
        
        if not self.project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")

    def analyze(self) -> Dict[str, Any]:
        """Run complete project health analysis."""
        print(f"🏥 Analyzing project health: {self.project_path.name}")
        
        # Run all checks
        self.check_readme()
        self.check_tests()
        self.check_ci_cd()
        self.check_code_quality()
        self.check_documentation()
        self.check_security()
        self.check_dependencies()
        
        # Calculate final score and rating
        score_percentage = (self.score / self.max_score) * 100
        rating = self.get_health_rating(score_percentage)
        
        return {
            "project": self.project_path.name,
            "path": str(self.project_path),
            "score": self.score,
            "max_score": self.max_score,
            "percentage": round(score_percentage, 1),
            "rating": rating,
            "results": self.results,
            "timestamp": datetime.now().isoformat()
        }

    def check_readme(self) -> None:
        """Check for README file (10 points)."""
        print("  📄 Checking README...")
        
        readme_files = []
        for file in self.project_path.iterdir():
            if file.is_file() and file.name.lower() in README_FILES:
                readme_files.append(file.name)
        
        score = 0
        details = []
        
        if readme_files:
            score = 10
            details.append(f"✅ Found README: {', '.join(readme_files)}")
            
            # Check README quality
            main_readme = None
            for readme in readme_files:
                if readme.lower() == 'readme.md':
                    main_readme = self.project_path / readme
                    break
            
            if not main_readme:
                main_readme = self.project_path / readme_files[0]
            
            try:
                content = main_readme.read_text(encoding='utf-8')
                word_count = len(content.split())
                
                if word_count < 50:
                    details.append("⚠️ README is quite short (< 50 words)")
                    score -= 2
                elif word_count > 200:
                    details.append("✅ README is comprehensive (> 200 words)")
                    
                # Check for common sections
                content_lower = content.lower()
                sections = ['installation', 'usage', 'setup', 'getting started', 'api', 'contributing']
                found_sections = [s for s in sections if s in content_lower]
                
                if found_sections:
                    details.append(f"✅ Found sections: {', '.join(found_sections)}")
                else:
                    details.append("⚠️ Missing common sections (installation, usage, etc.)")
                    score -= 1
                    
            except Exception as e:
                details.append(f"⚠️ Could not analyze README content: {str(e)}")
        else:
            details.append("❌ No README file found")
        
        self.score += score
        self.results["readme"] = {
            "score": score,
            "max_score": 10,
            "details": details
        }

    def check_tests(self) -> None:
        """Check for tests (15 points)."""
        print("  🧪 Checking tests...")
        
        test_files = []
        test_directories = []
        
        # Check for test directories
        for item in self.project_path.iterdir():
            if item.is_dir() and item.name.lower() in TEST_DIRS:
                test_directories.append(item.name)
                # Count test files in directory
                for test_file in item.rglob("*"):
                    if test_file.is_file() and self._is_test_file(test_file.name):
                        test_files.append(str(test_file.relative_to(self.project_path)))
        
        # Check for test files in root and subdirectories
        for file in self.project_path.rglob("*"):
            if file.is_file() and self._is_test_file(file.name):
                rel_path = str(file.relative_to(self.project_path))
                if rel_path not in test_files:
                    test_files.append(rel_path)
        
        score = 0
        details = []
        
        if test_directories:
            details.append(f"✅ Found test directories: {', '.join(test_directories)}")
            score += 5
        
        if test_files:
            details.append(f"✅ Found {len(test_files)} test files")
            score += min(10, len(test_files) * 2)  # Up to 10 points for test files
            
            # Show some test files as examples
            if len(test_files) <= 5:
                details.append(f"Test files: {', '.join(test_files)}")
            else:
                details.append(f"Example test files: {', '.join(test_files[:3])}... (+{len(test_files)-3} more)")
        else:
            details.append("❌ No test files found")
            
        # Check for test configuration
        test_configs = ['jest.config.js', 'pytest.ini', 'phpunit.xml', 'test_config.py', '.rspec']
        found_configs = [config for config in test_configs if (self.project_path / config).exists()]
        
        if found_configs:
            details.append(f"✅ Found test configuration: {', '.join(found_configs)}")
            score += 2
        
        self.score += score
        self.results["tests"] = {
            "score": score,
            "max_score": 15,
            "details": details,
            "test_files_count": len(test_files),
            "test_directories": test_directories
        }

    def check_ci_cd(self) -> None:
        """Check for CI/CD configuration (10 points)."""
        print("  🚀 Checking CI/CD...")
        
        ci_configs = []
        
        # Check for various CI/CD configurations
        ci_patterns = [
            ('.github/workflows', 'GitHub Actions'),
            ('.gitlab-ci.yml', 'GitLab CI'),
            ('.travis.yml', 'Travis CI'),
            ('circle.yml', 'CircleCI'),
            ('.circleci/config.yml', 'CircleCI'),
            ('azure-pipelines.yml', 'Azure Pipelines'),
            ('Jenkinsfile', 'Jenkins'),
            ('.buildkite/pipeline.yml', 'Buildkite')
        ]
        
        for pattern, name in ci_patterns:
            path = self.project_path / pattern
            if path.exists():
                ci_configs.append(name)
        
        score = 0
        details = []
        
        if ci_configs:
            score = 10
            details.append(f"✅ Found CI/CD: {', '.join(ci_configs)}")
            
            # Check GitHub Actions workflows specifically
            gh_workflows_dir = self.project_path / '.github' / 'workflows'
            if gh_workflows_dir.exists():
                workflow_files = list(gh_workflows_dir.glob('*.yml')) + list(gh_workflows_dir.glob('*.yaml'))
                if workflow_files:
                    details.append(f"✅ GitHub Actions workflows: {len(workflow_files)} files")
        else:
            details.append("❌ No CI/CD configuration found")
        
        self.score += score
        self.results["ci_cd"] = {
            "score": score,
            "max_score": 10,
            "details": details,
            "ci_systems": ci_configs
        }

    def check_code_quality(self) -> None:
        """Check code quality indicators (20 points)."""
        print("  📊 Checking code quality...")
        
        details = []
        score = 0
        
        # Check for linting configuration
        linting_configs = [
            '.eslintrc.js', '.eslintrc.json', '.eslintrc.yml', '.eslintrc',
            '.pylintrc', 'setup.cfg', 'tox.ini', '.flake8',
            '.prettierrc', '.prettierrc.json', '.prettier.config.js',
            'rustfmt.toml', '.rustfmt.toml'
        ]
        
        found_linters = []
        for config in linting_configs:
            if (self.project_path / config).exists():
                found_linters.append(config)
        
        if found_linters:
            score += 5
            details.append(f"✅ Found linting config: {', '.join(found_linters)}")
        else:
            details.append("⚠️ No linting configuration found")
        
        # Check for formatting tools
        formatting_configs = ['.editorconfig', '.clang-format', 'black.toml']
        found_formatters = [c for c in formatting_configs if (self.project_path / c).exists()]
        
        if found_formatters:
            score += 3
            details.append(f"✅ Found formatting config: {', '.join(found_formatters)}")
        
        # Check for type checking (TypeScript, mypy, etc.)
        type_configs = ['tsconfig.json', 'mypy.ini', '.mypy.ini']
        found_type_checkers = [c for c in type_configs if (self.project_path / c).exists()]
        
        if found_type_checkers:
            score += 4
            details.append(f"✅ Found type checking: {', '.join(found_type_checkers)}")
        
        # Analyze code structure
        source_files = self._get_source_files()
        if source_files:
            # Basic metrics
            total_lines = 0
            files_with_comments = 0
            
            for file_path in source_files[:20]:  # Analyze first 20 files
                try:
                    content = file_path.read_text(encoding='utf-8')
                    lines = content.splitlines()
                    total_lines += len(lines)
                    
                    # Check for comments
                    if self._has_meaningful_comments(content, file_path.suffix):
                        files_with_comments += 1
                        
                except Exception:
                    continue
            
            if files_with_comments > 0:
                comment_ratio = files_with_comments / min(len(source_files), 20)
                if comment_ratio > 0.5:
                    score += 4
                    details.append(f"✅ Good commenting: {files_with_comments}/{min(len(source_files), 20)} files have comments")
                elif comment_ratio > 0.2:
                    score += 2
                    details.append(f"⚠️ Some commenting: {files_with_comments}/{min(len(source_files), 20)} files have comments")
            
            # Check for reasonable file sizes
            large_files = [f for f in source_files if f.stat().st_size > 10000]  # > 10KB
            if len(large_files) < len(source_files) * 0.1:  # Less than 10% are large
                score += 2
                details.append("✅ Good file sizes (most files < 10KB)")
            
            # Check for code organization
            if len(source_files) > 5:  # Multi-file project
                directories = set()
                for file_path in source_files:
                    if len(file_path.parts) > 1:
                        directories.add(file_path.parts[0])
                
                if len(directories) > 1:
                    score += 2
                    details.append(f"✅ Good organization: code spread across {len(directories)} directories")
        
        self.score += score
        self.results["code_quality"] = {
            "score": score,
            "max_score": 20,
            "details": details,
            "linters": found_linters,
            "formatters": found_formatters,
            "type_checkers": found_type_checkers
        }

    def check_documentation(self) -> None:
        """Check for documentation (15 points)."""
        print("  📚 Checking documentation...")
        
        details = []
        score = 0
        
        # Check for documentation directories
        doc_dirs = []
        for item in self.project_path.iterdir():
            if item.is_dir() and item.name.lower() in DOC_DIRS:
                doc_dirs.append(item.name)
                score += 5
        
        if doc_dirs:
            details.append(f"✅ Found documentation directories: {', '.join(doc_dirs)}")
        else:
            details.append("⚠️ No dedicated documentation directory found")
        
        # Check for inline documentation
        source_files = self._get_source_files()
        documented_files = 0
        
        for file_path in source_files[:10]:  # Check first 10 source files
            try:
                content = file_path.read_text(encoding='utf-8')
                if self._has_docstrings(content, file_path.suffix):
                    documented_files += 1
            except Exception:
                continue
        
        if documented_files > 0 and source_files:
            doc_ratio = documented_files / min(len(source_files), 10)
            if doc_ratio > 0.7:
                score += 6
                details.append(f"✅ Excellent inline documentation: {documented_files}/{min(len(source_files), 10)} files")
            elif doc_ratio > 0.3:
                score += 3
                details.append(f"✅ Good inline documentation: {documented_files}/{min(len(source_files), 10)} files")
            else:
                score += 1
                details.append(f"⚠️ Limited inline documentation: {documented_files}/{min(len(source_files), 10)} files")
        
        # Check for API documentation tools
        api_doc_configs = ['swagger.yaml', 'openapi.yaml', 'apidoc.json', 'docs/api.md']
        found_api_docs = [c for c in api_doc_configs if (self.project_path / c).exists()]
        
        if found_api_docs:
            score += 4
            details.append(f"✅ Found API documentation: {', '.join(found_api_docs)}")
        
        self.score += score
        self.results["documentation"] = {
            "score": score,
            "max_score": 15,
            "details": details,
            "doc_directories": doc_dirs,
            "documented_files_ratio": documented_files / max(len(source_files[:10]), 1)
        }

    def check_security(self) -> None:
        """Check for security measures (15 points)."""
        print("  🔒 Checking security...")
        
        details = []
        score = 0
        
        # Check for security-related files
        security_files = []
        for sec_file in SECURITY_FILES:
            if (self.project_path / sec_file).exists():
                security_files.append(sec_file)
                score += 2
        
        if security_files:
            details.append(f"✅ Found security files: {', '.join(security_files)}")
        
        # Check for dependency scanning
        if (self.project_path / '.github' / 'dependabot.yml').exists():
            score += 3
            details.append("✅ Dependabot configured for dependency updates")
        
        # Check for secrets in config
        config_files = ['.env.example', '.env.template', 'config.example.json']
        example_configs = [c for c in config_files if (self.project_path / c).exists()]
        
        if example_configs:
            score += 2
            details.append(f"✅ Found example config files: {', '.join(example_configs)}")
        
        # Check for .gitignore
        gitignore_path = self.project_path / '.gitignore'
        if gitignore_path.exists():
            score += 2
            details.append("✅ .gitignore file present")
            
            # Check for common security patterns in .gitignore
            try:
                gitignore_content = gitignore_path.read_text(encoding='utf-8').lower()
                security_patterns = ['.env', 'secret', 'key', 'password', 'token']
                found_patterns = [p for p in security_patterns if p in gitignore_content]
                
                if found_patterns:
                    score += 2
                    details.append(f"✅ .gitignore includes security patterns: {', '.join(found_patterns)}")
                    
            except Exception:
                pass
        else:
            details.append("⚠️ No .gitignore file found")
        
        # Check for HTTPS in URLs
        readme_files = [f for f in self.project_path.iterdir() 
                       if f.is_file() and f.name.lower().startswith('readme')]
        
        if readme_files:
            try:
                content = readme_files[0].read_text(encoding='utf-8').lower()
                if 'https://' in content and 'http://' not in content.replace('http://localhost', ''):
                    score += 2
                    details.append("✅ Uses HTTPS URLs in documentation")
            except Exception:
                pass
        
        # Check for license
        license_files = ['LICENSE', 'LICENSE.md', 'LICENSE.txt', 'COPYING']
        license_found = any((self.project_path / lic).exists() for lic in license_files)
        
        if license_found:
            score += 2
            details.append("✅ License file present")
        else:
            details.append("⚠️ No license file found")
        
        if not details:
            details.append("⚠️ No security measures detected")
        
        self.score += score
        self.results["security"] = {
            "score": score,
            "max_score": 15,
            "details": details,
            "security_files": security_files
        }

    def check_dependencies(self) -> None:
        """Check if dependencies are up to date (15 points)."""
        print("  📦 Checking dependencies...")
        
        details = []
        score = 0
        
        # Check for dependency files
        dep_files = []
        for config in CONFIG_FILES:
            config_path = self.project_path / config
            if config_path.exists():
                dep_files.append(config)
        
        if not dep_files:
            details.append("⚠️ No dependency files found")
            self.score += score
            self.results["dependencies"] = {
                "score": score,
                "max_score": 15,
                "details": details
            }
            return
        
        details.append(f"✅ Found dependency files: {', '.join(dep_files)}")
        score += 5
        
        # Analyze package.json if present
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    package_data = json.load(f)
                
                deps = package_data.get('dependencies', {})
                dev_deps = package_data.get('devDependencies', {})
                total_deps = len(deps) + len(dev_deps)
                
                if total_deps > 0:
                    score += 3
                    details.append(f"✅ {total_deps} dependencies in package.json")
                    
                    # Check for lock file
                    lock_files = ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml']
                    found_lock = [lf for lf in lock_files if (self.project_path / lf).exists()]
                    
                    if found_lock:
                        score += 3
                        details.append(f"✅ Lock file present: {', '.join(found_lock)}")
                    else:
                        details.append("⚠️ No lock file found (package-lock.json, yarn.lock)")
                        
                    # Check for version pinning (basic check)
                    pinned_deps = sum(1 for v in {**deps, **dev_deps}.values() 
                                    if not v.startswith('^') and not v.startswith('~'))
                    
                    if pinned_deps > total_deps * 0.5:
                        score += 2
                        details.append(f"✅ Good version pinning: {pinned_deps}/{total_deps} dependencies")
                    
            except Exception as e:
                details.append(f"⚠️ Error analyzing package.json: {str(e)}")
        
        # Check requirements.txt if present
        req_file = self.project_path / 'requirements.txt'
        if req_file.exists():
            try:
                content = req_file.read_text(encoding='utf-8')
                lines = [line.strip() for line in content.splitlines() 
                        if line.strip() and not line.startswith('#')]
                
                if lines:
                    score += 3
                    details.append(f"✅ {len(lines)} dependencies in requirements.txt")
                    
                    # Check for version pinning
                    pinned = sum(1 for line in lines if '==' in line)
                    if pinned > len(lines) * 0.5:
                        score += 2
                        details.append(f"✅ Good version pinning: {pinned}/{len(lines)} dependencies")
                        
            except Exception as e:
                details.append(f"⚠️ Error analyzing requirements.txt: {str(e)}")
        
        # Additional points for having both dev and prod dependencies clearly separated
        if package_json.exists():
            try:
                with open(package_json) as f:
                    package_data = json.load(f)
                    
                if package_data.get('dependencies') and package_data.get('devDependencies'):
                    score += 2
                    details.append("✅ Dev and production dependencies separated")
                    
            except Exception:
                pass
        
        self.score += score
        self.results["dependencies"] = {
            "score": score,
            "max_score": 15,
            "details": details,
            "dependency_files": dep_files
        }

    def _is_test_file(self, filename: str) -> bool:
        """Check if a file is likely a test file."""
        filename_lower = filename.lower()
        return (
            filename_lower.startswith('test_') or
            filename_lower.endswith('_test.py') or
            filename_lower.endswith('.test.js') or
            filename_lower.endswith('.test.ts') or
            filename_lower.endswith('.spec.js') or
            filename_lower.endswith('.spec.ts') or
            'test' in filename_lower
        )

    def _get_source_files(self) -> List[Path]:
        """Get all source files in the project."""
        source_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', 
                           '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt'}
        
        source_files = []
        for file_path in self.project_path.rglob("*"):
            if (file_path.is_file() and 
                file_path.suffix.lower() in source_extensions and
                not any(ignore in file_path.parts for ignore in {'node_modules', '.git', '__pycache__'})):
                source_files.append(file_path)
        
        return source_files

    def _has_meaningful_comments(self, content: str, extension: str) -> bool:
        """Check if file has meaningful comments."""
        lines = content.splitlines()
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if extension == '.py' and stripped.startswith('#'):
                comment_lines += 1
            elif extension in ['.js', '.ts', '.jsx', '.tsx'] and (stripped.startswith('//') or '/*' in stripped):
                comment_lines += 1
            elif extension in ['.java', '.cpp', '.c', '.cs'] and (stripped.startswith('//') or '/*' in stripped):
                comment_lines += 1
        
        return comment_lines > max(3, len(lines) * 0.05)  # At least 5% comments or 3 lines

    def _has_docstrings(self, content: str, extension: str) -> bool:
        """Check if file has docstrings/documentation."""
        if extension == '.py':
            return '"""' in content or "'''" in content
        elif extension in ['.js', '.ts', '.jsx', '.tsx']:
            return '/**' in content or '@param' in content or '@returns' in content
        elif extension == '.java':
            return '/**' in content or '@param' in content or '@return' in content
        
        return False

    def get_health_rating(self, percentage: float) -> str:
        """Get health rating based on percentage score."""
        if percentage >= 90:
            return "🟢 Excellent"
        elif percentage >= 80:
            return "🟡 Good"
        elif percentage >= 65:
            return "🟠 Fair"
        elif percentage >= 50:
            return "🔴 Poor"
        else:
            return "💀 Critical"

def print_results(results: Dict[str, Any]) -> None:
    """Print formatted results."""
    print(f"\n🏥 **Project Health Report**")
    print(f"Project: {results['project']}")
    print(f"Score: {results['score']}/{results['max_score']} ({results['percentage']}%)")
    print(f"Rating: {results['rating']}")
    print(f"Analyzed: {results['timestamp'][:19]}")
    
    print(f"\n📊 **Detailed Breakdown:**")
    
    for category, data in results['results'].items():
        category_name = category.replace('_', ' ').title()
        score_info = f"{data['score']}/{data['max_score']}"
        print(f"\n**{category_name}** - {score_info} points:")
        
        for detail in data['details']:
            print(f"  {detail}")
    
    print(f"\n💡 **Recommendations:**")
    
    # Generate recommendations based on low scores
    recommendations = []
    
    for category, data in results['results'].items():
        percentage = (data['score'] / data['max_score']) * 100
        if percentage < 70:
            if category == 'readme':
                recommendations.append("📄 Improve README: Add installation, usage, and contribution sections")
            elif category == 'tests':
                recommendations.append("🧪 Add tests: Create test files and test directories")
            elif category == 'ci_cd':
                recommendations.append("🚀 Set up CI/CD: Add GitHub Actions or similar automation")
            elif category == 'code_quality':
                recommendations.append("📊 Improve code quality: Add linting, formatting, and type checking")
            elif category == 'documentation':
                recommendations.append("📚 Add documentation: Create docs directory and inline comments")
            elif category == 'security':
                recommendations.append("🔒 Enhance security: Add .gitignore, example configs, and Dependabot")
            elif category == 'dependencies':
                recommendations.append("📦 Manage dependencies: Pin versions and add lock files")
    
    if recommendations:
        for rec in recommendations:
            print(f"  {rec}")
    else:
        print("  🎉 Great job! Your project health looks good!")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python project_health.py <project_path>    # Score specific project")
        print("  python project_health.py --current         # Score current directory")
        sys.exit(1)
    
    if sys.argv[1] == "--current":
        project_path = "."
    elif sys.argv[1] in ["-h", "--help"]:
        print(__doc__)
        sys.exit(0)
    else:
        project_path = sys.argv[1]
    
    try:
        scorer = ProjectHealthScorer(project_path)
        results = scorer.analyze()
        print_results(results)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
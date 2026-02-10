#!/usr/bin/env python3
"""
Code Review Skill - Main Review Script
=====================================
Automated code review with quality, security, and best practice analysis.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any
import re

class CodeReviewer:
    def __init__(self, path: str = "."):
        self.path = Path(path).resolve()
        self.issues = []
        self.stats = {
            'files_reviewed': 0,
            'total_lines': 0,
            'issues_found': 0
        }
        
        # Load configuration
        config_path = Path(os.environ.get('SKILL_PATH', '.')) / 'config.json'
        if config_path.exists():
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            self.config = self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for code review."""
        return {
            "enabled_checks": [
                "security",
                "performance", 
                "style",
                "documentation",
                "complexity"
            ],
            "file_extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c"],
            "ignore_patterns": ["*/node_modules/*", "*/.git/*", "*/venv/*", "*/__pycache__/*"],
            "severity_levels": ["low", "medium", "high", "critical"],
            "max_line_length": 120,
            "max_function_length": 50,
            "max_complexity": 10
        }

    def review(self) -> Dict[str, Any]:
        """Main review function."""
        print(f"🔍 Starting code review of: {self.path}")
        
        # Find files to review
        files_to_review = self._find_files()
        
        for file_path in files_to_review:
            self._review_file(file_path)
            
        # Generate summary
        self._print_summary()
        
        return {
            'issues': self.issues,
            'stats': self.stats,
            'path': str(self.path)
        }

    def _find_files(self) -> List[Path]:
        """Find files to review based on configuration."""
        files = []
        
        for ext in self.config['file_extensions']:
            pattern = f"**/*{ext}"
            for file_path in self.path.glob(pattern):
                if self._should_review_file(file_path):
                    files.append(file_path)
                    
        return sorted(files)

    def _should_review_file(self, file_path: Path) -> bool:
        """Check if file should be reviewed based on ignore patterns."""
        file_str = str(file_path)
        
        for pattern in self.config['ignore_patterns']:
            # Simple pattern matching
            pattern_regex = pattern.replace('*', '.*')
            if re.match(pattern_regex, file_str):
                return False
                
        return True

    def _review_file(self, file_path: Path):
        """Review a single file."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            self.stats['files_reviewed'] += 1
            self.stats['total_lines'] += len(lines)
            
            # Run enabled checks
            if "security" in self.config['enabled_checks']:
                self._check_security(file_path, content, lines)
            if "performance" in self.config['enabled_checks']:
                self._check_performance(file_path, content, lines)
            if "style" in self.config['enabled_checks']:
                self._check_style(file_path, content, lines)
            if "documentation" in self.config['enabled_checks']:
                self._check_documentation(file_path, content, lines)
            if "complexity" in self.config['enabled_checks']:
                self._check_complexity(file_path, content, lines)
                
        except Exception as e:
            self._add_issue(file_path, 0, "error", f"Failed to review file: {e}")

    def _check_security(self, file_path: Path, content: str, lines: List[str]):
        """Check for security issues."""
        security_patterns = [
            (r'eval\s*\(', 'high', 'Use of eval() can be dangerous'),
            (r'exec\s*\(', 'high', 'Use of exec() can be dangerous'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'critical', 'Hardcoded password detected'),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'high', 'Hardcoded API key detected'),
            (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', 'medium', 'Shell injection risk'),
            (r'sql.*\+.*["\']', 'high', 'Potential SQL injection'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, severity, message in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self._add_issue(file_path, i, severity, f"Security: {message}")

    def _check_performance(self, file_path: Path, content: str, lines: List[str]):
        """Check for performance issues."""
        performance_patterns = [
            (r'time\.sleep\s*\(\s*[0-9]+\s*\)', 'medium', 'Long sleep() calls can impact performance'),
            (r'\.replace\s*\(.*\)\.replace', 'low', 'Multiple replace() calls, consider regex'),
            (r'for.*in.*\.keys\s*\(\s*\):', 'low', 'Iterating over dict.keys() is inefficient'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, severity, message in performance_patterns:
                if re.search(pattern, line):
                    self._add_issue(file_path, i, severity, f"Performance: {message}")

    def _check_style(self, file_path: Path, content: str, lines: List[str]):
        """Check for style issues."""
        for i, line in enumerate(lines, 1):
            # Line length
            if len(line) > self.config['max_line_length']:
                self._add_issue(file_path, i, 'low', 
                             f"Line too long ({len(line)} > {self.config['max_line_length']})")
            
            # Trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                self._add_issue(file_path, i, 'low', 'Trailing whitespace')

    def _check_documentation(self, file_path: Path, content: str, lines: List[str]):
        """Check for documentation issues."""
        if file_path.suffix == '.py':
            # Check for missing docstrings in functions
            function_pattern = r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
            
            for i, line in enumerate(lines):
                if re.match(function_pattern, line):
                    # Check if next non-empty line is a docstring
                    has_docstring = False
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if lines[j].strip():
                            if lines[j].strip().startswith('"""') or lines[j].strip().startswith("'''"):
                                has_docstring = True
                            break
                    
                    if not has_docstring:
                        func_name = re.match(function_pattern, line).group(1)
                        if not func_name.startswith('_'):  # Skip private functions
                            self._add_issue(file_path, i + 1, 'medium', 
                                         f'Function "{func_name}" missing docstring')

    def _check_complexity(self, file_path: Path, content: str, lines: List[str]):
        """Check for complexity issues."""
        if file_path.suffix == '.py':
            # Simple function length check
            in_function = False
            function_start = 0
            indent_level = 0
            
            for i, line in enumerate(lines):
                if re.match(r'^\s*def\s+', line):
                    if in_function:
                        # Previous function ended
                        length = i - function_start
                        if length > self.config['max_function_length']:
                            self._add_issue(file_path, function_start + 1, 'medium',
                                         f'Function too long ({length} lines > {self.config["max_function_length"]})')
                    
                    in_function = True
                    function_start = i
                    indent_level = len(line) - len(line.lstrip())
                elif in_function and line.strip() and len(line) - len(line.lstrip()) <= indent_level and not line.strip().startswith('#'):
                    # Function ended
                    length = i - function_start
                    if length > self.config['max_function_length']:
                        self._add_issue(file_path, function_start + 1, 'medium',
                                     f'Function too long ({length} lines > {self.config["max_function_length"]})')
                    in_function = False

    def _add_issue(self, file_path: Path, line_number: int, severity: str, message: str):
        """Add an issue to the list."""
        self.issues.append({
            'file': str(file_path.relative_to(self.path)),
            'line': line_number,
            'severity': severity,
            'message': message
        })
        self.stats['issues_found'] += 1

    def _print_summary(self):
        """Print review summary."""
        print(f"\n📊 Code Review Summary")
        print("=" * 50)
        print(f"Files reviewed: {self.stats['files_reviewed']}")
        print(f"Total lines: {self.stats['total_lines']}")
        print(f"Issues found: {self.stats['issues_found']}")
        
        if self.issues:
            print(f"\n🔴 Issues by severity:")
            severity_counts = {}
            for issue in self.issues:
                severity = issue['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            for severity in ['critical', 'high', 'medium', 'low']:
                if severity in severity_counts:
                    print(f"  {severity.upper()}: {severity_counts[severity]}")
            
            print(f"\n📝 Detailed Issues:")
            for issue in sorted(self.issues, key=lambda x: (x['severity'], x['file'], x['line'])):
                print(f"  {issue['file']}:{issue['line']} [{issue['severity'].upper()}] {issue['message']}")
        else:
            print("✅ No issues found!")


def main():
    """Main review function."""
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    reviewer = CodeReviewer(path)
    result = reviewer.review()
    
    # Exit with error code if issues found
    return 1 if result['stats']['issues_found'] > 0 else 0

if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/env python3
"""
Doc Generator Skill - Main Generator
===================================
Auto-generate documentation from code analysis.
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class DocumentationGenerator:
    def __init__(self, path: str = "."):
        self.path = Path(path).resolve()
        self.docs = {
            'modules': [],
            'functions': [],
            'classes': [],
            'apis': [],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'path': str(self.path)
            }
        }
        
    def generate(self, doc_type: str = "all") -> Dict[str, Any]:
        """Generate documentation of specified type."""
        print(f"📚 Generating {doc_type} documentation for: {self.path}")
        
        if doc_type in ["all", "code"]:
            self._analyze_python_code()
            self._analyze_javascript_code()
            
        if doc_type in ["all", "api"]:
            self._extract_api_documentation()
            
        if doc_type in ["all", "readme"]:
            self._generate_readme_content()
            
        self._save_documentation(doc_type)
        
        return self.docs

    def _analyze_python_code(self):
        """Analyze Python files for documentation."""
        print("🐍 Analyzing Python code...")
        
        for py_file in self.path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content, filename=str(py_file))
                
                module_info = {
                    'file': str(py_file.relative_to(self.path)),
                    'docstring': ast.get_docstring(tree) or "",
                    'functions': [],
                    'classes': []
                }
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_info = self._extract_function_info(node, py_file)
                        module_info['functions'].append(func_info)
                        self.docs['functions'].append(func_info)
                        
                    elif isinstance(node, ast.ClassDef):
                        class_info = self._extract_class_info(node, py_file)
                        module_info['classes'].append(class_info)
                        self.docs['classes'].append(class_info)
                
                self.docs['modules'].append(module_info)
                
            except Exception as e:
                print(f"⚠️ Error analyzing {py_file}: {e}")

    def _analyze_javascript_code(self):
        """Analyze JavaScript/TypeScript files for documentation."""
        print("🟨 Analyzing JavaScript/TypeScript code...")
        
        js_patterns = ["*.js", "*.ts", "*.jsx", "*.tsx"]
        
        for pattern in js_patterns:
            for js_file in self.path.rglob(pattern):
                if self._should_skip_file(js_file):
                    continue
                    
                try:
                    content = js_file.read_text(encoding='utf-8', errors='ignore')
                    
                    # Extract function documentation (basic regex parsing)
                    functions = self._extract_js_functions(content, js_file)
                    self.docs['functions'].extend(functions)
                    
                    # Extract API endpoints
                    apis = self._extract_js_apis(content, js_file)
                    self.docs['apis'].extend(apis)
                    
                except Exception as e:
                    print(f"⚠️ Error analyzing {js_file}: {e}")

    def _extract_function_info(self, node: ast.FunctionDef, file_path: Path) -> Dict[str, Any]:
        """Extract information about a Python function."""
        return {
            'name': node.name,
            'file': str(file_path.relative_to(self.path)),
            'line': node.lineno,
            'docstring': ast.get_docstring(node) or "",
            'args': [arg.arg for arg in node.args.args],
            'returns': self._get_return_annotation(node),
            'decorators': [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list],
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'is_method': False,  # Will be updated if inside a class
            'visibility': 'private' if node.name.startswith('_') else 'public'
        }

    def _extract_class_info(self, node: ast.ClassDef, file_path: Path) -> Dict[str, Any]:
        """Extract information about a Python class."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_function_info(item, file_path)
                method_info['is_method'] = True
                methods.append(method_info)
        
        return {
            'name': node.name,
            'file': str(file_path.relative_to(self.path)),
            'line': node.lineno,
            'docstring': ast.get_docstring(node) or "",
            'methods': methods,
            'bases': [base.id if hasattr(base, 'id') else str(base) for base in node.bases],
            'decorators': [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list]
        }

    def _extract_js_functions(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract JavaScript/TypeScript function documentation."""
        functions = []
        
        # Basic regex patterns for function definitions
        patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)\s*{',
            r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*{',
            r'(\w+)\s*:\s*function\s*\(([^)]*)\)',
            r'async\s+function\s+(\w+)\s*\(([^)]*)\)'
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    # Look for JSDoc comments above
                    jsdoc = self._extract_jsdoc(lines, i - 1)
                    
                    functions.append({
                        'name': match.group(1),
                        'file': str(file_path.relative_to(self.path)),
                        'line': i,
                        'args': [arg.strip() for arg in match.group(2).split(',') if arg.strip()],
                        'docstring': jsdoc,
                        'language': 'javascript',
                        'is_async': 'async' in line
                    })
                    
        return functions

    def _extract_js_apis(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract API endpoint documentation from JavaScript."""
        apis = []
        
        # Look for common API patterns
        api_patterns = [
            (r'app\.(get|post|put|delete)\s*\(\s*[\'"]([^\'"]+)[\'"]', 'express'),
            (r'router\.(get|post|put|delete)\s*\(\s*[\'"]([^\'"]+)[\'"]', 'express'),
            (r'@(Get|Post|Put|Delete)\s*\(\s*[\'"]([^\'"]+)[\'"]', 'decorator'),
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern, framework in api_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    method = match.group(1).upper()
                    endpoint = match.group(2)
                    
                    # Look for comments above
                    comment = self._extract_api_comment(lines, i - 1)
                    
                    apis.append({
                        'method': method,
                        'endpoint': endpoint,
                        'file': str(file_path.relative_to(self.path)),
                        'line': i,
                        'framework': framework,
                        'description': comment
                    })
                    
        return apis

    def _extract_jsdoc(self, lines: List[str], line_index: int) -> str:
        """Extract JSDoc comment above a function."""
        jsdoc_lines = []
        i = line_index - 1
        
        while i >= 0 and (lines[i].strip().startswith('*') or 
                         lines[i].strip().startswith('//') or
                         lines[i].strip() == ''):
            if lines[i].strip().startswith('/**'):
                break
            if lines[i].strip().startswith('*') or lines[i].strip().startswith('//'):
                jsdoc_lines.insert(0, lines[i].strip())
            i -= 1
            
        return '\n'.join(jsdoc_lines)

    def _extract_api_comment(self, lines: List[str], line_index: int) -> str:
        """Extract API description from comments."""
        comment_lines = []
        i = line_index - 1
        
        while i >= 0 and (lines[i].strip().startswith('//') or 
                         lines[i].strip().startswith('/*') or
                         lines[i].strip() == ''):
            if lines[i].strip().startswith('//') or lines[i].strip().startswith('/*'):
                comment_lines.insert(0, lines[i].strip())
            i -= 1
            if len(comment_lines) > 5:  # Limit search
                break
                
        return '\n'.join(comment_lines)

    def _extract_api_documentation(self):
        """Extract API documentation from various sources."""
        print("🔗 Extracting API documentation...")
        
        # Look for OpenAPI/Swagger files
        api_files = [
            "openapi.yaml", "openapi.yml", "swagger.yaml", "swagger.yml",
            "api.yaml", "api.yml", "openapi.json", "swagger.json"
        ]
        
        for api_file in api_files:
            api_path = self.path / api_file
            if api_path.exists():
                try:
                    if api_file.endswith('.json'):
                        with open(api_path) as f:
                            api_spec = json.load(f)
                    else:
                        # Would need yaml library for full parsing
                        content = api_path.read_text()
                        api_spec = {"raw": content}
                    
                    self.docs['apis'].append({
                        'type': 'openapi',
                        'file': api_file,
                        'spec': api_spec
                    })
                    
                except Exception as e:
                    print(f"⚠️ Error parsing {api_file}: {e}")

    def _generate_readme_content(self):
        """Generate README.md content from project analysis."""
        print("📖 Generating README content...")
        
        project_name = self.path.name
        
        # Basic README structure
        readme_content = f"""# {project_name}

## Overview

Auto-generated documentation for {project_name}.

## Project Structure

"""
        
        # Add module information
        if self.docs['modules']:
            readme_content += "### Modules\n\n"
            for module in self.docs['modules'][:10]:  # Limit to first 10
                readme_content += f"- **{module['file']}**"
                if module['docstring']:
                    readme_content += f": {module['docstring'].split('.')[0]}"
                readme_content += "\n"
            readme_content += "\n"
        
        # Add API information
        if self.docs['apis']:
            readme_content += "### API Endpoints\n\n"
            for api in self.docs['apis'][:10]:
                if 'endpoint' in api:
                    readme_content += f"- `{api.get('method', 'GET')} {api['endpoint']}`"
                    if api.get('description'):
                        readme_content += f" - {api['description'][:100]}"
                    readme_content += "\n"
            readme_content += "\n"
        
        readme_content += f"""## Installation

```bash
# Installation instructions here
```

## Usage

```bash
# Usage examples here
```

## Documentation

- Functions: {len(self.docs['functions'])}
- Classes: {len(self.docs['classes'])}
- Modules: {len(self.docs['modules'])}

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.docs['readme_content'] = readme_content

    def _get_return_annotation(self, node: ast.FunctionDef) -> str:
        """Get return type annotation from function."""
        if node.returns:
            if hasattr(node.returns, 'id'):
                return node.returns.id
            else:
                return str(node.returns)
        return ""

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            '__pycache__',
            '.git',
            'node_modules',
            '.pytest_cache',
            'venv',
            '.venv',
            'test_',
            '_test.py'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)

    def _save_documentation(self, doc_type: str):
        """Save generated documentation to files."""
        output_dir = self.path / "docs" / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON documentation
        json_path = output_dir / f"documentation-{doc_type}.json"
        with open(json_path, 'w') as f:
            json.dump(self.docs, f, indent=2)
        
        print(f"✅ Documentation saved to: {json_path}")
        
        # Save README if generated
        if 'readme_content' in self.docs:
            readme_path = self.path / "README-generated.md"
            with open(readme_path, 'w') as f:
                f.write(self.docs['readme_content'])
            print(f"✅ README saved to: {readme_path}")


def main():
    """Main documentation generation function."""
    doc_type = sys.argv[1] if len(sys.argv) > 1 else "all"
    path = sys.argv[2] if len(sys.argv) > 2 else "."
    
    valid_types = ["all", "code", "api", "readme"]
    if doc_type not in valid_types:
        print(f"❌ Invalid documentation type: {doc_type}")
        print(f"Valid types: {', '.join(valid_types)}")
        return 1
    
    generator = DocumentationGenerator(path)
    result = generator.generate(doc_type)
    
    print(f"\n📊 Documentation Generation Summary:")
    print(f"Modules: {len(result['modules'])}")
    print(f"Functions: {len(result['functions'])}")
    print(f"Classes: {len(result['classes'])}")
    print(f"APIs: {len(result['apis'])}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
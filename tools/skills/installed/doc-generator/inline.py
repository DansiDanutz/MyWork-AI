#!/usr/bin/env python3
"""
Doc Generator Skill - Inline Documentation
==========================================
Generate inline code documentation and docstrings.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

def generate_inline_docs(path: str = "."):
    """Generate inline documentation for Python files."""
    print(f"📝 Generating inline documentation for: {path}")
    
    target_path = Path(path)
    if target_path.is_file() and target_path.suffix == '.py':
        files_to_process = [target_path]
    else:
        files_to_process = list(target_path.rglob("*.py"))
    
    total_functions = 0
    documented_functions = 0
    
    for py_file in files_to_process:
        if _should_skip_file(py_file):
            continue
            
        print(f"Processing: {py_file}")
        funcs_in_file, docs_in_file = _process_file(py_file)
        total_functions += funcs_in_file
        documented_functions += docs_in_file
    
    print(f"\n📊 Inline Documentation Summary:")
    print(f"Total functions: {total_functions}")
    print(f"Documented functions: {documented_functions}")
    
    if total_functions > 0:
        percentage = (documented_functions / total_functions) * 100
        print(f"Documentation coverage: {percentage:.1f}%")
        
        if percentage < 50:
            print("🔴 Low documentation coverage - consider adding more docstrings")
        elif percentage < 80:
            print("🟡 Moderate documentation coverage - room for improvement")  
        else:
            print("🟢 Good documentation coverage!")
    
    return 0

def _process_file(file_path: Path) -> Tuple[int, int]:
    """Process a single Python file and generate documentation suggestions."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(content, filename=str(file_path))
        
        functions_count = 0
        documented_count = 0
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions_count += 1
                
                if ast.get_docstring(node):
                    documented_count += 1
                else:
                    # Generate docstring suggestion
                    suggestion = _generate_docstring_suggestion(node, content)
                    suggestions.append((node.lineno, node.name, suggestion))
        
        # Print suggestions for this file
        if suggestions:
            print(f"  📝 Docstring suggestions for {file_path}:")
            for line_no, func_name, suggestion in suggestions:
                print(f"    Line {line_no}: {func_name}")
                print(f"      Suggested docstring:")
                for line in suggestion.split('\n'):
                    print(f"        {line}")
                print()
        
        return functions_count, documented_count
        
    except Exception as e:
        print(f"  ⚠️ Error processing {file_path}: {e}")
        return 0, 0

def _generate_docstring_suggestion(node: ast.FunctionDef, file_content: str) -> str:
    """Generate a docstring suggestion for a function."""
    func_name = node.name
    args = [arg.arg for arg in node.args.args]
    
    # Analyze function complexity and purpose
    purpose = _infer_function_purpose(func_name, args)
    
    # Generate basic docstring template
    docstring_lines = [f'"""', f'{purpose}']
    
    # Add parameter documentation if function has arguments
    if args and args != ['self']:  # Skip 'self' for methods
        docstring_lines.extend(['', 'Args:'])
        for arg in args:
            if arg != 'self':
                arg_desc = _infer_arg_purpose(arg)
                docstring_lines.append(f'    {arg}: {arg_desc}')
    
    # Add return documentation if function might return something
    if _might_return_value(node):
        docstring_lines.extend(['', 'Returns:', '    Description of return value'])
    
    # Add raises section for functions that might raise exceptions
    if _might_raise_exceptions(node, file_content):
        docstring_lines.extend(['', 'Raises:', '    Exception: Description of when raised'])
    
    docstring_lines.append('"""')
    
    return '\n'.join(docstring_lines)

def _infer_function_purpose(func_name: str, args: List[str]) -> str:
    """Infer function purpose from name and arguments."""
    name_lower = func_name.lower()
    
    # Common patterns
    if name_lower.startswith('get_'):
        return f"Get {func_name[4:].replace('_', ' ')}."
    elif name_lower.startswith('set_'):
        return f"Set {func_name[4:].replace('_', ' ')}."
    elif name_lower.startswith('is_') or name_lower.startswith('has_'):
        return f"Check if {func_name[3:].replace('_', ' ')}."
    elif name_lower.startswith('create_'):
        return f"Create {func_name[7:].replace('_', ' ')}."
    elif name_lower.startswith('delete_') or name_lower.startswith('remove_'):
        return f"Delete {func_name[7:].replace('_', ' ')}."
    elif name_lower.startswith('update_'):
        return f"Update {func_name[7:].replace('_', ' ')}."
    elif name_lower.startswith('validate_'):
        return f"Validate {func_name[9:].replace('_', ' ')}."
    elif name_lower.startswith('parse_'):
        return f"Parse {func_name[6:].replace('_', ' ')}."
    elif name_lower.startswith('load_'):
        return f"Load {func_name[5:].replace('_', ' ')}."
    elif name_lower.startswith('save_'):
        return f"Save {func_name[5:].replace('_', ' ')}."
    elif name_lower == 'main':
        return "Main function."
    elif name_lower in ['__init__', 'init']:
        return "Initialize the object."
    elif len(args) > 0:
        return f"Process {func_name.replace('_', ' ')} with given parameters."
    else:
        return f"Execute {func_name.replace('_', ' ')} operation."

def _infer_arg_purpose(arg_name: str) -> str:
    """Infer argument purpose from name."""
    name_lower = arg_name.lower()
    
    if 'path' in name_lower or 'file' in name_lower:
        return "Path to file or directory"
    elif 'url' in name_lower:
        return "URL string"
    elif 'data' in name_lower:
        return "Data to process"
    elif 'config' in name_lower:
        return "Configuration object"
    elif 'id' in name_lower:
        return "Identifier"
    elif 'name' in name_lower:
        return "Name string"
    elif 'count' in name_lower or 'num' in name_lower:
        return "Number/count value"
    elif 'flag' in name_lower or name_lower.startswith('is_') or name_lower.startswith('enable'):
        return "Boolean flag"
    elif 'list' in name_lower or 'items' in name_lower:
        return "List of items"
    else:
        return f"The {arg_name} parameter"

def _might_return_value(node: ast.FunctionDef) -> bool:
    """Check if function might return a value."""
    # Look for return statements
    for child in ast.walk(node):
        if isinstance(child, ast.Return) and child.value:
            return True
    return False

def _might_raise_exceptions(node: ast.FunctionDef, file_content: str) -> bool:
    """Check if function might raise exceptions."""
    # Look for raise statements or common exception-raising patterns
    for child in ast.walk(node):
        if isinstance(child, ast.Raise):
            return True
        elif isinstance(child, ast.Call):
            if hasattr(child.func, 'id') and child.func.id in ['open', 'requests.get', 'json.loads']:
                return True
    return False

def _should_skip_file(file_path: Path) -> bool:
    """Check if file should be skipped."""
    skip_patterns = [
        '__pycache__',
        '.git',
        'venv',
        '.venv',
        'test_',
        '_test.py',
        '.pytest_cache'
    ]
    
    file_str = str(file_path)
    return any(pattern in file_str for pattern in skip_patterns)

def main():
    """Main inline documentation function."""
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    return generate_inline_docs(path)

if __name__ == '__main__':
    sys.exit(main())
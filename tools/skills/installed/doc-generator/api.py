#!/usr/bin/env python3
"""
Doc Generator Skill - API Documentation
======================================
Generate API documentation from code analysis.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def generate_api_docs(format_type: str = "markdown"):
    """Generate API documentation in specified format."""
    print(f"🔗 Generating API documentation in {format_type} format...")
    
    # Run main generator to analyze code
    generate_script = Path(__file__).parent / "generate.py"
    result = subprocess.run([sys.executable, str(generate_script), "api", "."], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Failed to analyze code for API documentation")
        return 1
        
    # Load generated documentation
    docs_path = Path("docs/generated/documentation-api.json")
    if docs_path.exists():
        with open(docs_path) as f:
            docs = json.load(f)
    else:
        docs = {"apis": [], "functions": []}
    
    if format_type == "openapi":
        generate_openapi_spec(docs)
    elif format_type == "html":
        generate_html_docs(docs)
    else:  # markdown (default)
        generate_markdown_docs(docs)
    
    return 0

def generate_openapi_spec(docs):
    """Generate OpenAPI 3.0 specification."""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": f"{Path.cwd().name} API",
            "description": "Auto-generated API documentation",
            "version": "1.0.0"
        },
        "servers": [
            {"url": "http://localhost:3000", "description": "Development server"}
        ],
        "paths": {}
    }
    
    for api in docs.get('apis', []):
        if 'endpoint' in api:
            endpoint = api['endpoint']
            method = api.get('method', 'GET').lower()
            
            if endpoint not in spec['paths']:
                spec['paths'][endpoint] = {}
                
            spec['paths'][endpoint][method] = {
                "summary": api.get('description', f"{method.upper()} {endpoint}"),
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
    
    print(json.dumps(spec, indent=2))

def generate_html_docs(docs):
    """Generate HTML API documentation."""
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - {Path.cwd().name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .endpoint {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .method {{ display: inline-block; padding: 4px 8px; border-radius: 3px; color: white; font-weight: bold; }}
        .get {{ background: #28a745; }}
        .post {{ background: #007bff; }}
        .put {{ background: #ffc107; color: black; }}
        .delete {{ background: #dc3545; }}
        .function {{ background: #e9ecef; padding: 10px; margin: 5px 0; border-left: 4px solid #007bff; }}
    </style>
</head>
<body>
    <h1>🔗 API Documentation</h1>
    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Endpoints</h2>
"""
    
    for api in docs.get('apis', []):
        if 'endpoint' in api:
            method = api.get('method', 'GET').lower()
            html += f"""
    <div class="endpoint">
        <span class="method {method}">{method.upper()}</span>
        <strong>{api['endpoint']}</strong>
        <p>{api.get('description', 'No description available')}</p>
        <small>File: {api.get('file', 'unknown')}</small>
    </div>
"""
    
    # Add function documentation
    api_functions = [f for f in docs.get('functions', []) if 'api' in f.get('name', '').lower()]
    if api_functions:
        html += "<h2>API Functions</h2>"
        for func in api_functions:
            html += f"""
    <div class="function">
        <strong>{func['name']}({', '.join(func.get('args', []))})</strong>
        <p>{func.get('docstring', 'No documentation available')}</p>
        <small>File: {func.get('file', 'unknown')}:{func.get('line', '?')}</small>
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    print(html)

def generate_markdown_docs(docs):
    """Generate Markdown API documentation."""
    markdown = f"""# 🔗 API Documentation

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Endpoints

"""
    
    for api in docs.get('apis', []):
        if 'endpoint' in api:
            method = api.get('method', 'GET')
            markdown += f"""### `{method} {api['endpoint']}`

{api.get('description', 'No description available')}

- **File:** `{api.get('file', 'unknown')}`
- **Line:** {api.get('line', '?')}

"""
    
    # Add function documentation
    api_functions = [f for f in docs.get('functions', []) if 'api' in f.get('name', '').lower()]
    if api_functions:
        markdown += "## API Functions\n\n"
        for func in api_functions:
            args_str = ', '.join(func.get('args', []))
            markdown += f"""### `{func['name']}({args_str})`

{func.get('docstring', 'No documentation available')}

- **File:** `{func.get('file', 'unknown')}`
- **Line:** {func.get('line', '?')}
- **Visibility:** {func.get('visibility', 'public')}

"""
    
    if not docs.get('apis') and not api_functions:
        markdown += "No API endpoints or functions found.\n"
    
    print(markdown)

def main():
    """Main API documentation function."""
    format_type = sys.argv[1] if len(sys.argv) > 1 else "markdown"
    
    if format_type not in ["markdown", "html", "openapi"]:
        print("❌ Invalid format. Use: markdown, html, or openapi")
        return 1
        
    return generate_api_docs(format_type)

if __name__ == '__main__':
    sys.exit(main())
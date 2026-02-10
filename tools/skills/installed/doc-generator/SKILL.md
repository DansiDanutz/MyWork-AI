# doc-generator

**Description:** Auto-generate documentation from code including API docs, README files, and inline documentation

**Version:** 1.0.0

**Author:** MyWork-AI Framework

## Dependencies

- python3
- mywork-ai

## Commands

### generate

**Script:** generate.py
**Usage:** mw skills run doc-generator generate [type] [path]

Generate documentation of specified type from code analysis.

### api

**Script:** api.py
**Usage:** mw skills run doc-generator api [format]

Generate API documentation from code (openapi, markdown, html).

### readme

**Script:** readme.py
**Usage:** mw skills run doc-generator readme

Auto-generate or update README.md from project analysis.

### inline

**Script:** inline.py
**Usage:** mw skills run doc-generator inline [path]

Generate inline code documentation and docstrings.

### help

**Script:** help.py
**Usage:** mw skills run doc-generator help

Show detailed help and usage information.

## Features

- API documentation generation (OpenAPI/Swagger)
- README.md auto-generation and updates
- Inline docstring generation
- Code comment analysis
- Multi-format output (HTML, Markdown, JSON)
- Language support (Python, JavaScript, TypeScript)
- Template customization

## Output Formats

- markdown
- html  
- json
- openapi
- postman

## Configuration

Edit `config.json` to customize templates, formats, and generation rules.
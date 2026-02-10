#!/usr/bin/env python3
"""
Doc Generator Skill - Help
=========================
"""

def main():
    """Show doc generator skill help."""
    print("""
📚 Doc Generator Skill Help
==========================

Auto-generate comprehensive documentation from code analysis 
including API docs, README files, and inline documentation.

COMMANDS:
  generate [type] [path]  - Generate documentation (all, code, api, readme)
  api [format]            - Generate API docs (markdown, html, openapi)
  readme                  - Auto-generate or update README.md
  inline [path]           - Generate inline docstring suggestions
  help                    - Show this help

EXAMPLES:
  mw skills run doc-generator generate
  mw skills run doc-generator generate code src/
  mw skills run doc-generator api openapi > api-spec.json
  mw skills run doc-generator readme
  mw skills run doc-generator inline src/main.py

DOCUMENTATION TYPES:
• all      - Complete documentation analysis
• code     - Code structure and function documentation  
• api      - API endpoint documentation
• readme   - Project README generation

API FORMATS:
• markdown - Human-readable API documentation
• html     - Interactive HTML documentation
• openapi  - OpenAPI 3.0 specification (JSON)

FEATURES:
• Multi-language support (Python, JavaScript, TypeScript)
• API endpoint auto-discovery
• Docstring generation suggestions
• README.md auto-generation
• Code structure analysis
• Function and class documentation
• OpenAPI/Swagger spec generation

ANALYSIS CAPABILITIES:
• Function signatures and parameters
• Class hierarchies and methods
• API endpoints and HTTP methods
• Module documentation and imports
• JSDoc and Python docstring extraction
• Type annotations and return values

OUTPUT LOCATIONS:
• Generated docs: docs/generated/
• README: README.md or README-generated.md
• API specs: stdout (redirect to save)
• Inline suggestions: console output

INTEGRATION:
Use in documentation workflows:
  mw skills run doc-generator generate && \
  mw skills run doc-generator api openapi > openapi.json

For more details, see the SKILL.md documentation.
""")
    return 0

if __name__ == '__main__':
    exit(main())
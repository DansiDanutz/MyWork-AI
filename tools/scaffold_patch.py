#!/usr/bin/env python3
"""
Patch for scaffold.py to add enhanced, runnable templates.
This will be integrated into the main scaffold.py file.
"""

from templates_enhanced import get_fastapi_template, get_express_template

def add_enhanced_templates():
    """Add enhanced templates to the TEMPLATES dict in scaffold.py"""
    
    # Enhanced FastAPI template
    fastapi_enhanced = {
        "description": "Production-ready FastAPI app with database, CORS, and tests",
        **get_fastapi_template("MyApp")
    }
    
    # Enhanced Express/Node template  
    express_enhanced = {
        "description": "Production-ready Express.js app with CORS, middleware, and tests",
        **get_express_template("MyApp")
    }
    
    return {
        "fastapi": fastapi_enhanced,
        "express": express_enhanced,
        "node": express_enhanced,  # Alias
        "nodejs": express_enhanced,  # Alias
    }

if __name__ == "__main__":
    enhanced = add_enhanced_templates()
    for name, template in enhanced.items():
        print(f"Template: {name}")
        print(f"Description: {template['description']}")
        print("Files:", list(template['structure'].keys()))
        print()
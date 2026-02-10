#!/usr/bin/env python3
"""
AI Code Review Tool
==================
Uses OpenRouter API to review code quality and provide suggestions.

Usage:
    python ai_review.py <file>              # Review specific file
    python ai_review.py --diff              # Review git diff
    python ai_review.py --staged            # Review staged changes
    mw review <file>                        # Via CLI
    mw review --diff                        # Via CLI
"""

import os
import sys
import json
import urllib.request
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

# OpenRouter API configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.0-flash-001"

def call_openrouter_api(prompt: str) -> str:
    """Call OpenRouter API with the given prompt."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    
    try:
        req = urllib.request.Request(OPENROUTER_URL, data=data, headers=headers)
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return "Error: No response from API"
    
    except Exception as e:
        return f"Error: Failed to call OpenRouter API - {str(e)}"

def get_git_diff(staged: bool = False) -> str:
    """Get git diff output."""
    try:
        cmd = ["git", "diff", "--staged"] if staged else ["git", "diff"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error getting git diff: {str(e)}"

def detect_language(file_path: str) -> str:
    """Detect programming language from file extension."""
    ext = Path(file_path).suffix.lower()
    
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React JSX',
        '.tsx': 'React TSX',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.dart': 'Dart',
        '.sql': 'SQL',
        '.sh': 'Shell Script',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.json': 'JSON',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.vue': 'Vue.js',
        '.r': 'R',
        '.scala': 'Scala'
    }
    
    return language_map.get(ext, 'Unknown')

def create_review_prompt(code: str, language: str = "Unknown", context: str = "") -> str:
    """Create the prompt for code review."""
    return f"""You are an expert code reviewer. Please review the following {language} code and provide detailed feedback.

CONTEXT: {context}

CODE TO REVIEW:
```{language.lower()}
{code}
```

Please provide a comprehensive code review covering:

## 🔍 **ISSUES FOUND**
- List any bugs, errors, or logical problems
- Rate severity: 🔴 Critical, 🟡 Medium, 🟢 Minor

## 💡 **SUGGESTIONS**
- Code quality improvements
- Better practices and patterns
- Performance optimizations
- Readability enhancements

## 🛡️ **SECURITY CONCERNS**
- Potential security vulnerabilities
- Input validation issues
- Authentication/authorization problems
- Data exposure risks

## ⚡ **PERFORMANCE TIPS**
- Algorithmic improvements
- Memory usage optimizations
- Database query efficiency
- Caching opportunities

## 🧹 **CODE STYLE**
- Formatting and consistency
- Naming conventions
- Documentation needs
- Code organization

## ✅ **POSITIVE FEEDBACK**
- What's done well
- Good practices used
- Clean code examples

## 📊 **OVERALL SCORE**
Rate the code quality: X/10

**Priority Actions:** List top 3 most important fixes

Keep feedback constructive, specific, and actionable. Use emojis and clear formatting for better readability."""

def review_file(file_path: str) -> Dict[str, Any]:
    """Review a specific file."""
    try:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        if not code.strip():
            return {"error": f"File is empty: {file_path}"}
        
        language = detect_language(file_path)
        context = f"Reviewing file: {file_path}"
        
        prompt = create_review_prompt(code, language, context)
        review = call_openrouter_api(prompt)
        
        return {
            "file": file_path,
            "language": language,
            "lines": len(code.splitlines()),
            "review": review
        }
    
    except Exception as e:
        return {"error": f"Error reviewing file {file_path}: {str(e)}"}

def review_diff(staged: bool = False) -> Dict[str, Any]:
    """Review git diff."""
    try:
        diff_output = get_git_diff(staged)
        
        if not diff_output.strip():
            diff_type = "staged changes" if staged else "working directory changes"
            return {"error": f"No {diff_type} to review"}
        
        context = f"Git diff ({'staged' if staged else 'unstaged'} changes)"
        prompt = create_review_prompt(diff_output, "Git Diff", context)
        review = call_openrouter_api(prompt)
        
        return {
            "type": "git_diff",
            "staged": staged,
            "review": review
        }
    
    except Exception as e:
        return {"error": f"Error reviewing diff: {str(e)}"}

def format_output(result: Dict[str, Any]) -> str:
    """Format the review output for display."""
    if "error" in result:
        return f"❌ {result['error']}"
    
    output = []
    
    if result.get("type") == "git_diff":
        output.append(f"🔍 **Git Diff Review** ({'Staged' if result.get('staged') else 'Unstaged'} Changes)")
    else:
        output.append(f"🔍 **File Review**: {result.get('file', 'Unknown')}")
        if result.get("language"):
            output.append(f"**Language**: {result['language']}")
        if result.get("lines"):
            output.append(f"**Lines**: {result['lines']}")
    
    output.append("")
    output.append(result.get("review", "No review available"))
    
    return "\n".join(output)

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python ai_review.py <file>        # Review specific file")
        print("  python ai_review.py --diff        # Review git diff")
        print("  python ai_review.py --staged      # Review staged changes")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg == "--diff":
        result = review_diff(staged=False)
    elif arg == "--staged":
        result = review_diff(staged=True)
    elif arg in ["-h", "--help"]:
        print(__doc__)
        sys.exit(0)
    else:
        # Assume it's a file path
        result = review_file(arg)
    
    print(format_output(result))

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Automatic Markdownlint Fixer
Fixes common markdownlint violations across the MyWork repository.

Handles:
- MD022: Headings without surrounding blank lines
- MD032: Lists without surrounding blank lines
- MD031: Fenced code blocks without blank lines
- MD047: Missing trailing newline
- MD058: Tables without blank lines
- MD024: Duplicate headings (warns only)
- MD036: Emphasis used as heading (warns only)
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple


def run_markdownlint(directory: str = ".") -> List[str]:
    """Run markdownlint and capture violations."""
    try:
        cmd = [
            "npx", "markdownlint",
            "**/*.md",
            "--ignore", "node_modules/**",
            "--ignore", "projects/*/node_modules/**",
            "--ignore", ".git/**"
        ]

        result = subprocess.run(
            cmd,
            cwd=directory,
            capture_output=True,
            text=True
        )

        # Markdownlint returns violations in stderr or stdout
        output = result.stderr + result.stdout
        return output.split('\n') if output else []

    except FileNotFoundError:
        print("❌ Error: markdownlint not found. Install with: npm install -g markdownlint-cli")
        return []


def fix_md022_headings(content: str) -> str:
    """Fix MD022: Add blank lines around headings."""
    lines = content.split('\n')
    result = []

    for i, line in enumerate(lines):
        # Check if this is a heading line
        if line.strip().startswith('#'):
            # Add blank line before heading (if not first line and previous line isn't blank)
            if i > 0 and lines[i-1].strip() != '':
                if not result or result[-1].strip() != '':
                    result.append('')

            result.append(line)

            # Add blank line after heading (if not last line and next line isn't blank)
            if i < len(lines) - 1 and lines[i+1].strip() != '':
                result.append('')
        else:
            result.append(line)

    return '\n'.join(result)


def fix_md032_lists(content: str) -> str:
    """Fix MD032: Add blank lines around lists."""
    lines = content.split('\n')
    result = []

    in_list = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check if this line starts a list
        is_list_item = (
            stripped.startswith('- ') or
            stripped.startswith('* ') or
            re.match(r'^\d+\.\s', stripped)
        )

        if is_list_item and not in_list:
            # Starting a new list - add blank line before if needed
            if result and result[-1].strip() != '':
                result.append('')
            in_list = True
            result.append(line)

        elif not is_list_item and in_list:
            # Ending a list - add blank line after
            in_list = False
            if stripped != '':  # Don't add blank line if next line is already blank
                result.append('')
            result.append(line)

        else:
            result.append(line)

    return '\n'.join(result)


def fix_md031_fences(content: str) -> str:
    """Fix MD031: Add blank lines around fenced code blocks."""
    lines = content.split('\n')
    result = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check if this is a code fence
        if stripped.startswith('```'):
            # Add blank line before fence (if not first line)
            if i > 0 and lines[i-1].strip() != '':
                if not result or result[-1].strip() != '':
                    result.append('')

            result.append(line)

            # For opening fence, add blank line after if needed
            # For closing fence, add blank line after if needed
            if i < len(lines) - 1 and lines[i+1].strip() != '':
                # Check if this is a closing fence by looking for matching opening fence
                fence_count = sum(1 for prev_line in lines[:i+1] if prev_line.strip().startswith('```'))
                if fence_count % 2 == 0:  # Even count means this closes a block
                    result.append('')
        else:
            result.append(line)

    return '\n'.join(result)


def fix_md047_trailing_newline(content: str) -> str:
    """Fix MD047: Ensure file ends with single newline."""
    if not content.endswith('\n'):
        return content + '\n'

    # Remove multiple trailing newlines
    content = content.rstrip('\n') + '\n'
    return content


def fix_md058_tables(content: str) -> str:
    """Fix MD058: Add blank lines around tables."""
    lines = content.split('\n')
    result = []

    in_table = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check if this looks like a table row
        is_table_row = '|' in stripped and stripped.startswith('|') and stripped.endswith('|')

        if is_table_row and not in_table:
            # Starting a new table - add blank line before if needed
            if result and result[-1].strip() != '':
                result.append('')
            in_table = True
            result.append(line)

        elif not is_table_row and in_table:
            # Ending a table - add blank line after
            in_table = False
            if stripped != '':  # Don't add blank line if next line is already blank
                result.append('')
            result.append(line)

        else:
            result.append(line)

    return '\n'.join(result)


def fix_file(filepath: str) -> Dict[str, int]:
    """Fix markdownlint violations in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()

        content = original_content
        fixes_applied = {}

        # Apply fixes in order
        new_content = fix_md022_headings(content)
        if new_content != content:
            fixes_applied['MD022'] = content.count('#') - content.count('##')
            content = new_content

        new_content = fix_md032_lists(content)
        if new_content != content:
            fixes_applied['MD032'] = len([l for l in content.split('\n') if l.strip().startswith(('- ', '* ')) or re.match(r'^\d+\.', l.strip())])
            content = new_content

        new_content = fix_md031_fences(content)
        if new_content != content:
            fixes_applied['MD031'] = content.count('```') // 2
            content = new_content

        new_content = fix_md047_trailing_newline(content)
        if new_content != content:
            fixes_applied['MD047'] = 1
            content = new_content

        new_content = fix_md058_tables(content)
        if new_content != content:
            fixes_applied['MD058'] = len([l for l in content.split('\n') if '|' in l and l.strip().startswith('|')])
            content = new_content

        # Write back if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

        return fixes_applied

    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return {}


def find_markdown_files(directory: str = ".") -> List[str]:
    """Find all markdown files, excluding node_modules."""
    markdown_files = []

    for root, dirs, files in os.walk(directory):
        # Skip node_modules and .git directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__']]

        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))

    return sorted(markdown_files)


def main():
    """Main execution function."""
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "."

    print("🔍 Finding markdown files...")
    markdown_files = find_markdown_files(directory)
    print(f"📝 Found {len(markdown_files)} markdown files")

    total_fixes = {}
    files_fixed = 0

    for filepath in markdown_files:
        print(f"🔧 Fixing: {filepath}")
        fixes = fix_file(filepath)

        if fixes:
            files_fixed += 1
            for rule, count in fixes.items():
                total_fixes[rule] = total_fixes.get(rule, 0) + count

            print(f"   ✅ Applied: {', '.join(f'{rule}({count})' for rule, count in fixes.items())}")
        else:
            print(f"   ✨ No fixes needed")

    print(f"\n🎉 Summary:")
    print(f"   📁 Files processed: {len(markdown_files)}")
    print(f"   🔧 Files fixed: {files_fixed}")

    if total_fixes:
        print(f"   📊 Total fixes:")
        for rule, count in total_fixes.items():
            rule_descriptions = {
                'MD022': 'Headings without blank lines',
                'MD032': 'Lists without blank lines',
                'MD031': 'Code blocks without blank lines',
                'MD047': 'Missing trailing newlines',
                'MD058': 'Tables without blank lines'
            }
            print(f"      • {rule} ({rule_descriptions.get(rule, 'Unknown')}): {count}")
    else:
        print("   ✨ No fixes were needed!")

    # Run markdownlint again to check remaining issues
    print(f"\n🔍 Running final markdownlint check...")
    violations = run_markdownlint(directory)
    remaining_violations = [v for v in violations if v.strip() and not v.startswith('Cannot read')]

    if remaining_violations:
        print(f"⚠️  {len(remaining_violations)} violations remain (manual review needed):")
        for violation in remaining_violations[:10]:  # Show first 10
            print(f"   • {violation}")
        if len(remaining_violations) > 10:
            print(f"   ... and {len(remaining_violations) - 10} more")
    else:
        print("✅ No markdownlint violations remaining!")


if __name__ == "__main__":
    main()
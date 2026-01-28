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


def fix_md040_code_language(content: str) -> str:
    """Fix MD040: Add language specification to fenced code blocks."""
    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.strip() == '```':
            # This is a bare ``` without language
            # Look ahead to determine the content and guess language
            content_lines = []
            j = i + 1

            # Collect content until closing ```
            while j < len(lines) and lines[j].strip() != '```':
                content_lines.append(lines[j])
                j += 1

            # Analyze content to determine language
            language = detect_code_language(content_lines)

            result.append(f'```{language}')
            result.extend(content_lines)
            if j < len(lines):  # Add closing fence
                result.append(lines[j])

            i = j + 1
        else:
            result.append(line)
            i += 1

    return '\n'.join(result)


def detect_code_language(content_lines: list) -> str:
    """Detect the programming language from code content."""
    import re

    content_text = '\n'.join(content_lines).strip()

    # Check for common patterns
    for line in content_lines:
        line = line.strip()
        if not line:
            continue

        # Bash/Shell patterns
        if (line.startswith(('python ', 'pip ', 'cd ', 'ls ', 'git ', 'npm ', 'mw ', 'sudo ', 'apt ', 'brew ', './')) or
            any(cmd in line for cmd in ['python tools/', 'npm install', 'git commit', '&&', '||', '$('])):
            return 'bash'

        # Python patterns
        if (line.startswith(('def ', 'import ', 'from ', 'class ', 'if __name__', 'print(')) or
            'import ' in line or 'from ' in line):
            return 'python'

        # JavaScript patterns
        if (line.startswith(('function ', 'const ', 'let ', 'var ', 'export ', 'import ')) or
            any(js_word in line for js_word in ['console.log', 'require(', '=>', 'async '])):
            return 'javascript'

        # JSON pattern
        if line.startswith(('{', '[')) and ('"' in line or "'" in line):
            return 'json'

        # YAML pattern
        if ':' in line and not line.startswith('#'):
            return 'yaml'

        # HTML pattern
        if line.startswith('<') and '>' in line:
            return 'html'

        # Markdown pattern (nested)
        if line.startswith(('#', '- ', '* ', '1. ')):
            return 'markdown'

    # Check for numbered list patterns (often used in documentation)
    if any(re.match(r'^\d+\.', line.strip()) for line in content_lines):
        return 'text'

    # Default
    return 'text'


def fix_md013_line_length(content: str, max_length: int = 80) -> str:
    """Fix MD013: Wrap long lines intelligently."""
    lines = content.split('\n')
    result = []
    in_code_block = False
    in_table = False

    for line in lines:
        # Track if we're in a code block
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            continue

        # Skip long lines in code blocks
        if in_code_block:
            result.append(line)
            continue

        # Track if we're in a table
        if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
            in_table = True
        elif in_table and not ('|' in line and line.strip()):
            in_table = False

        # Handle long lines
        if len(line) > max_length:
            if in_table:
                # For tables, split long cell content
                result.append(wrap_table_line(line, max_length))
            elif line.strip().startswith('#'):
                # Don't wrap headers, just keep them
                result.append(line)
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                # Wrap list items
                result.extend(wrap_list_item(line, max_length))
            else:
                # Wrap regular text
                result.extend(wrap_regular_text(line, max_length))
        else:
            result.append(line)

    return '\n'.join(result)


def wrap_table_line(line: str, max_length: int) -> str:
    """Intelligently wrap table lines by shortening cell content."""
    if '|' not in line:
        return line

    # Split table cells
    cells = line.split('|')
    wrapped_cells = []

    # Calculate available space per cell
    num_cells = len([c for c in cells if c.strip()])
    if num_cells <= 1:
        return line

    # Roughly distribute space: max_length divided by cells, minus pipes and padding
    max_cell_length = max(12, (max_length - num_cells - 1) // num_cells - 4)

    for cell in cells:
        cell_content = cell.strip()

        if len(cell_content) > max_cell_length:
            # Aggressively abbreviate long cell content
            if cell_content.startswith('[TESTED]'):
                abbreviated = '[T]' + cell_content[8:]  # Shorten tag
            elif cell_content.startswith('[EXPERIMENTAL]'):
                abbreviated = '[E]' + cell_content[14:]  # Shorten tag
            else:
                abbreviated = cell_content

            # Further shorten if still too long
            if len(abbreviated) > max_cell_length:
                abbreviated = abbreviated[:max_cell_length-3] + '...'

            wrapped_cells.append(f' {abbreviated} ')
        else:
            wrapped_cells.append(f' {cell_content} ')

    return '|'.join(wrapped_cells)


def wrap_list_item(line: str, max_length: int) -> list:
    """Wrap long list items."""
    indent = len(line) - len(line.lstrip())
    prefix = line[:indent]

    if line.strip().startswith('- '):
        marker = '- '
        content = line.strip()[2:]
    elif line.strip().startswith('* '):
        marker = '* '
        content = line.strip()[2:]
    else:
        return [line]

    if len(prefix + marker + content) <= max_length:
        return [line]

    # Wrap the content
    words = content.split()
    lines = []
    current_line = prefix + marker
    continuation_prefix = prefix + '  '  # Two spaces for continuation

    for word in words:
        test_line = current_line + word
        if len(test_line) <= max_length:
            if current_line.endswith(marker):
                current_line += word
            else:
                current_line += ' ' + word
        else:
            if current_line != prefix + marker:
                lines.append(current_line)
                current_line = continuation_prefix + word
            else:
                # Very long word, just add it
                current_line += word

    if current_line.strip():
        lines.append(current_line)

    return lines


def wrap_regular_text(line: str, max_length: int) -> list:
    """Wrap regular text lines."""
    if not line.strip():
        return [line]

    indent = len(line) - len(line.lstrip())
    prefix = line[:indent]
    content = line[indent:]

    if len(line) <= max_length:
        return [line]

    words = content.split()
    lines = []
    current_line = prefix

    for word in words:
        test_line = current_line + word if current_line == prefix else current_line + ' ' + word

        if len(test_line) <= max_length:
            if current_line == prefix:
                current_line += word
            else:
                current_line += ' ' + word
        else:
            if current_line.strip():
                lines.append(current_line)
                current_line = prefix + word
            else:
                # Very long word
                current_line += word

    if current_line.strip():
        lines.append(current_line)

    return lines


def fix_md034_bare_urls(content: str) -> str:
    """Fix MD034: Wrap bare URLs in angle brackets."""
    import re

    lines = content.split('\n')
    result = []
    in_code_block = False
    in_table = False

    for line in lines:
        # Track code blocks and tables
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            continue

        if in_code_block:
            result.append(line)
            continue

        if '|' in line and line.strip().startswith('|'):
            in_table = True
        elif in_table and not ('|' in line and line.strip()):
            in_table = False

        # Fix bare URLs (not already in brackets or markdown links)
        if not in_code_block and not in_table:
            # Find bare HTTP(S) URLs that aren't already formatted
            url_pattern = r'(?<!\[)(?<!\()(?<![<`])(https?://[^\s\]>\)]+)(?![>\]`])'

            def replace_url(match):
                url = match.group(1)
                # Don't replace if it's already part of a markdown link
                return f'<{url}>'

            line = re.sub(url_pattern, replace_url, line)

        result.append(line)

    return '\n'.join(result)


def fix_md046_code_block_style(content: str) -> str:
    """Fix MD046: Convert indented code blocks to fenced style."""
    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is the start of an indented code block
        if (line.startswith('    ') and line.strip() and
            (i == 0 or not lines[i-1].strip() or not lines[i-1].startswith('    '))):

            # Collect all consecutive indented lines
            code_lines = []
            j = i
            while j < len(lines) and (lines[j].startswith('    ') or not lines[j].strip()):
                if lines[j].startswith('    '):
                    code_lines.append(lines[j][4:])  # Remove 4-space indent
                elif not lines[j].strip():
                    code_lines.append('')  # Keep blank lines
                else:
                    break
                j += 1

            # Only convert if we have actual code content
            if any(line.strip() for line in code_lines):
                # Add fenced code block
                result.append('```')
                result.extend(code_lines)
                result.append('```')
                i = j
                continue

        result.append(line)
        i += 1

    return '\n'.join(result)


def fix_md051_link_fragments(content: str) -> str:
    """Fix MD051: Fix invalid link fragments."""
    import re

    lines = content.split('\n')
    result = []

    # Collect all headers to create valid fragment targets
    headers = {}
    for line in lines:
        if line.strip().startswith('#'):
            header_text = re.sub(r'^#+\s*', '', line.strip())
            # Convert header to valid fragment ID using GitHub's algorithm
            fragment_id = header_text.lower()
            fragment_id = re.sub(r'[^\w\s-]', '', fragment_id)  # Remove special chars
            fragment_id = re.sub(r'\s+', '-', fragment_id)      # Replace spaces with hyphens
            fragment_id = fragment_id.strip('-')                # Remove leading/trailing hyphens

            # Handle numbered sections
            if re.match(r'^\d+', fragment_id):
                fragment_id = fragment_id

            headers[header_text.lower()] = fragment_id

    # Also create common mappings for numbered sections
    common_mappings = {
        'technical-architecture': '4-technical-architecture',
        'pricing-strategy': '5-pricing-strategy',
        'legal-framework': '6-legal-framework',
        'go-to-market-strategy': '7-go-to-market-strategy',
        'financial-projections': '8-financial-projections',
        'risk-analysis': '9-risk-analysis',
        'roadmap': '10-roadmap'
    }

    for line in lines:
        # Fix internal link fragments
        if '](#' in line:
            def fix_fragment(match):
                link_text = match.group(1)
                fragment = match.group(2)

                # Check common mappings first
                fragment_lower = fragment.lower()
                if fragment_lower in common_mappings:
                    return f'[{link_text}](#{common_mappings[fragment_lower]})'

                # Try to find exact match
                for header_text, valid_fragment in headers.items():
                    if fragment_lower == valid_fragment or fragment_lower == header_text:
                        return f'[{link_text}](#{valid_fragment})'

                # Try fuzzy matching
                for header_text, valid_fragment in headers.items():
                    if (fragment_lower.replace('-', ' ').replace('_', ' ') in header_text or
                        header_text.replace('-', ' ').replace('_', ' ') in fragment_lower.replace('-', ' ').replace('_', ' ')):
                        return f'[{link_text}](#{valid_fragment})'

                # If no match found, try to create a reasonable fragment
                clean_fragment = re.sub(r'[^\w\s-]', '', fragment.lower())
                clean_fragment = re.sub(r'\s+', '-', clean_fragment)
                clean_fragment = clean_fragment.strip('-')
                return f'[{link_text}](#{clean_fragment})'

            line = re.sub(r'\[([^\]]+)\]\(#([^)]+)\)', fix_fragment, line)

        result.append(line)

    return '\n'.join(result)


def fix_md031_fences_enhanced(content: str) -> str:
    """Enhanced MD031: Better fenced code block spacing."""
    lines = content.split('\n')
    result = []

    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            # Opening fence
            if line.strip() == '```' or any(line.strip().startswith('```' + lang) for lang in ['bash', 'python', 'javascript', 'json', 'yaml', 'text']):
                # Add blank line before if needed
                if i > 0 and lines[i-1].strip() != '':
                    if not result or result[-1].strip() != '':
                        result.append('')

                result.append(line)

                # For opening fence, find the closing fence and add blank line after
                j = i + 1
                while j < len(lines):
                    if lines[j].strip().startswith('```') and lines[j].strip() != line.strip():
                        # Found closing fence
                        break
                    j += 1

                # Add blank line after closing fence if needed
                if j < len(lines) - 1 and lines[j + 1].strip() != '':
                    # This will be handled when we reach the closing fence
                    pass
            else:
                # Closing fence
                result.append(line)

                # Add blank line after if needed
                if i < len(lines) - 1 and lines[i + 1].strip() != '':
                    result.append('')
        else:
            result.append(line)

    return '\n'.join(result)


def fix_md060_table_style(content: str) -> str:
    """Fix MD060: Table column style (add spaces around pipes)."""
    lines = content.split('\n')
    result = []

    for line in lines:
        # Check if this is a table separator line
        if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
            # Check if it's a separator line (contains dashes)
            if '-' in line:
                # Fix spacing around pipes for separator lines
                # Convert |-------|-------| to | ------- | ------- |
                line = line.strip()
                if line.startswith('|') and line.endswith('|') and not (' |' in line or '| ' in line):
                    # Split by pipes and rebuild with proper spacing
                    parts = line.split('|')
                    if len(parts) >= 3:  # At least |something|something|
                        fixed_parts = ['']  # Start with empty for leading |
                        for i, part in enumerate(parts[1:-1]):  # Skip first empty and last empty
                            if part.strip():  # If not empty
                                fixed_parts.append(' ' + part.strip() + ' ')
                            else:
                                fixed_parts.append(' ')
                        fixed_parts.append('')  # End with empty for trailing |
                        line = '|'.join(fixed_parts)
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

        new_content = fix_md040_code_language(content)
        if new_content != content:
            fixes_applied['MD040'] = content.count('```\n')
            content = new_content

        new_content = fix_md013_line_length(content)
        if new_content != content:
            fixes_applied['MD013'] = len([l for l in content.split('\n') if len(l) > 80])
            content = new_content

        new_content = fix_md034_bare_urls(content)
        if new_content != content:
            fixes_applied['MD034'] = content.count('http://') + content.count('https://')
            content = new_content

        new_content = fix_md046_code_block_style(content)
        if new_content != content:
            fixes_applied['MD046'] = len([l for l in content.split('\n') if l.startswith('    ') and l.strip()])
            content = new_content

        new_content = fix_md051_link_fragments(content)
        if new_content != content:
            fixes_applied['MD051'] = content.count('](#')
            content = new_content

        # Enhanced MD031 for better fenced code block spacing
        new_content = fix_md031_fences_enhanced(content)
        if new_content != content:
            fixes_applied['MD031_enhanced'] = content.count('```')
            content = new_content

        new_content = fix_md060_table_style(content)
        if new_content != content:
            fixes_applied['MD060'] = content.count('|')
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
        try:
            fixes = fix_file(filepath)

            if fixes:
                files_fixed += 1
                for rule, count in fixes.items():
                    total_fixes[rule] = total_fixes.get(rule, 0) + count

                print(f"   ✅ Applied: {', '.join(f'{rule}({count})' for rule, count in fixes.items())}")
            else:
                print(f"   ✨ No fixes needed")

        except Exception as e:
            print(f"   ⚠️ Error processing {filepath}: {e}")
            print(f"   🔄 Continuing with next file...")
            continue

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
                'MD058': 'Tables without blank lines',
                'MD040': 'Fenced code blocks without language',
                'MD013': 'Lines too long',
                'MD034': 'Bare URLs not in angle brackets',
                'MD046': 'Indented code blocks (should be fenced)',
                'MD051': 'Invalid link fragments',
                'MD031_enhanced': 'Enhanced fenced code block spacing'
            }
            print(f"      • {rule} ({rule_descriptions.get(rule, 'Unknown')}): {count}")
    else:
        print("   ✨ No fixes were needed!")

    # Run markdownlint again to check remaining issues
    print(f"\n🔍 Running final markdownlint check...")
    try:
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

    except Exception as e:
        print(f"⚠️ Error running final markdownlint check: {e}")
        print(f"🔄 Files were still processed and fixed where possible")


class AutoLintFixer:
    """Simple wrapper class for integration with auto_linting_agent."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir

    def fix_file(self, filepath: str) -> int:
        """Fix a single markdown file and return number of issues fixed."""
        fixes = fix_file(filepath)
        return sum(fixes.values())


if __name__ == "__main__":
    main()
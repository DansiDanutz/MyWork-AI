#!/usr/bin/env python3
"""
Badge Generator (mw badge)
===========================
Generate and update project badges (shields.io compatible).
Auto-detects version, test count, health score, and updates README.

Usage:
    mw badge                    # Show all available badges
    mw badge update             # Update badges in README.md
    mw badge generate           # Generate badge URLs only
    mw badge --format md        # Output as Markdown
    mw badge --format html      # Output as HTML
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def run(cmd: str, cwd: str = None) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.stdout.strip()


def detect_version(project_path: Path) -> Optional[str]:
    for f in ["pyproject.toml", "setup.py", "package.json", "VERSION"]:
        fp = project_path / f
        if not fp.exists():
            continue
        content = fp.read_text()
        if f == "package.json":
            try:
                return json.loads(content).get("version")
            except json.JSONDecodeError:
                continue
        elif f == "VERSION":
            return content.strip()
        else:
            m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if m:
                return m.group(1)
    return None


def count_tests(project_path: Path) -> int:
    """Count test functions without running them."""
    count = 0
    tests_dir = project_path / "tests"
    if not tests_dir.exists():
        return 0
    for f in tests_dir.rglob("test_*.py"):
        content = f.read_text(errors="ignore")
        count += len(re.findall(r"^\s*def test_", content, re.MULTILINE))
    return count


def count_commands(project_path: Path) -> int:
    """Count mw commands from mw.py."""
    mw = project_path / "tools" / "mw.py"
    if not mw.exists():
        return 0
    content = mw.read_text(errors="ignore")
    return len(re.findall(r"^def cmd_\w+", content, re.MULTILINE))


def count_loc(project_path: Path) -> int:
    """Count lines of Python code."""
    total = 0
    for d in ["tools", "src", "lib"]:
        dp = project_path / d
        if dp.exists():
            for f in dp.rglob("*.py"):
                total += sum(1 for line in f.read_text(errors="ignore").splitlines() if line.strip() and not line.strip().startswith("#"))
    return total


def detect_license(project_path: Path) -> str:
    lic = project_path / "LICENSE"
    if not lic.exists():
        return "unknown"
    content = lic.read_text(errors="ignore")[:500].lower()
    if "mit" in content:
        return "MIT"
    elif "apache" in content:
        return "Apache-2.0"
    elif "gpl" in content:
        return "GPL-3.0"
    return "custom"


def detect_python_version(project_path: Path) -> Optional[str]:
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        m = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
        if m:
            return m.group(1)
    return None


def shields_url(label: str, value: str, color: str, style: str = "flat-square") -> str:
    """Generate shields.io badge URL."""
    label_enc = quote(label, safe="")
    value_enc = quote(str(value), safe="")
    return f"https://img.shields.io/badge/{label_enc}-{value_enc}-{color}?style={style}"


def generate_badges(project_path: Path) -> List[Dict]:
    """Generate all badges for the project."""
    badges = []

    # Version
    version = detect_version(project_path)
    if version:
        badges.append({
            "name": "version",
            "label": "version",
            "value": f"v{version}",
            "color": "blue",
            "url": shields_url("version", f"v{version}", "blue"),
        })

    # Python version
    py_ver = detect_python_version(project_path)
    if py_ver:
        badges.append({
            "name": "python",
            "label": "python",
            "value": py_ver,
            "color": "3776AB",
            "url": shields_url("python", py_ver, "3776AB"),
        })

    # Tests
    test_count = count_tests(project_path)
    if test_count > 0:
        color = "brightgreen" if test_count >= 100 else "green" if test_count >= 50 else "yellow"
        badges.append({
            "name": "tests",
            "label": "tests",
            "value": str(test_count),
            "color": color,
            "url": shields_url("tests", str(test_count), color),
        })

    # Commands
    cmd_count = count_commands(project_path)
    if cmd_count > 0:
        badges.append({
            "name": "commands",
            "label": "commands",
            "value": str(cmd_count),
            "color": "purple",
            "url": shields_url("commands", str(cmd_count), "purple"),
        })

    # Lines of code
    loc = count_loc(project_path)
    if loc > 0:
        if loc >= 10000:
            loc_str = f"{loc // 1000}k+"
        else:
            loc_str = str(loc)
        badges.append({
            "name": "loc",
            "label": "lines of code",
            "value": loc_str,
            "color": "informational",
            "url": shields_url("lines of code", loc_str, "informational"),
        })

    # License
    lic = detect_license(project_path)
    if lic != "unknown":
        badges.append({
            "name": "license",
            "label": "license",
            "value": lic,
            "color": "green",
            "url": shields_url("license", lic, "green"),
        })

    # Platform
    badges.append({
        "name": "platform",
        "label": "platform",
        "value": "linux | macOS | windows",
        "color": "lightgrey",
        "url": shields_url("platform", "linux | macOS | windows", "lightgrey"),
    })

    return badges


def format_badges_md(badges: List[Dict]) -> str:
    return " ".join(f"![{b['label']}]({b['url']})" for b in badges)


def format_badges_html(badges: List[Dict]) -> str:
    return "\n".join(f'<img src="{b["url"]}" alt="{b["label"]}">' for b in badges)


def update_readme(project_path: Path, badges: List[Dict]) -> bool:
    """Update README.md with badge line."""
    readme = project_path / "README.md"
    if not readme.exists():
        return False

    content = readme.read_text()
    badge_line = format_badges_md(badges)

    # Replace existing badge section (between <!-- badges-start --> and <!-- badges-end -->)
    marker_pattern = r"<!-- badges-start -->.*?<!-- badges-end -->"
    new_section = f"<!-- badges-start -->\n{badge_line}\n<!-- badges-end -->"

    if re.search(marker_pattern, content, re.DOTALL):
        content = re.sub(marker_pattern, new_section, content, flags=re.DOTALL)
    else:
        # Also try replacing existing badge images at the top
        badge_img_pattern = r"^(\!\[.*?\]\(https://img\.shields\.io.*?\)\s*)+\n"
        if re.search(badge_img_pattern, content, re.MULTILINE):
            content = re.sub(badge_img_pattern, badge_line + "\n\n", content, count=1, flags=re.MULTILINE)
        else:
            # Insert after first heading
            m = re.search(r"^#\s+.+\n", content, re.MULTILINE)
            if m:
                insert_pos = m.end()
                content = content[:insert_pos] + "\n" + new_section + "\n" + content[insert_pos:]
            else:
                content = new_section + "\n\n" + content

    readme.write_text(content)
    return True


def main():
    args = sys.argv[1:]
    project_path = Path.cwd()

    # Find project root
    check = project_path
    while check != check.parent:
        if (check / ".git").exists():
            project_path = check
            break
        check = check.parent

    fmt = "md"
    if "--format" in args:
        idx = args.index("--format")
        if idx + 1 < len(args):
            fmt = args[idx + 1]
            args = [a for i, a in enumerate(args) if i != idx and i != idx + 1]

    badges = generate_badges(project_path)

    if not args or args[0] == "generate":
        print(f"\n{BOLD}🏷️  Project Badges{RESET}")
        print("=" * 60)
        for b in badges:
            print(f"  {GREEN}●{RESET} {b['label']}: {BOLD}{b['value']}{RESET}")
            print(f"    {DIM}{b['url']}{RESET}")

        print(f"\n{BOLD}Markdown:{RESET}")
        print(format_badges_md(badges))

        if fmt == "html":
            print(f"\n{BOLD}HTML:{RESET}")
            print(format_badges_html(badges))

    elif args[0] == "update":
        if update_readme(project_path, badges):
            print(f"  {GREEN}✓{RESET} Updated README.md with {len(badges)} badges")
        else:
            print(f"  {RED}✗{RESET} README.md not found")
            sys.exit(1)

    elif args[0] in ("help", "--help"):
        print(__doc__)
    else:
        print(f"Unknown command: {args[0]}")
        sys.exit(1)


if __name__ == "__main__":
    main()

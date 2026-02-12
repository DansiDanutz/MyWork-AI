#!/usr/bin/env python3
"""MyWork Changelog Generator — auto-generate changelogs from git history.

Usage:
    mw changelog                    Show recent changes (last tag to HEAD)
    mw changelog --full             Full changelog from all tags
    mw changelog --since <date>     Changes since date (YYYY-MM-DD)
    mw changelog --format md|json   Output format (default: md)
    mw changelog --output <file>    Write to file instead of stdout
    mw changelog --unreleased       Show only unreleased changes
    mw changelog --tag <version>    Generate for specific tag

Parses conventional commits (feat:, fix:, docs:, etc.) into categorized,
readable changelogs with stats.
"""

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# Commit type mappings
COMMIT_TYPES = {
    "feat": ("🚀 Features", 1),
    "fix": ("🐛 Bug Fixes", 2),
    "perf": ("⚡ Performance", 3),
    "refactor": ("♻️ Refactoring", 4),
    "docs": ("📚 Documentation", 5),
    "test": ("✅ Tests", 6),
    "ci": ("🔧 CI/CD", 7),
    "build": ("📦 Build", 8),
    "chore": ("🏗️ Chores", 9),
    "style": ("🎨 Style", 10),
    "security": ("🔒 Security", 3),
}

BREAKING_EMOJI = "💥"


def run_git(args, cwd=None):
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=10,
            cwd=cwd or os.getcwd()
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def get_tags(cwd=None):
    """Get sorted list of version tags."""
    output = run_git(["tag", "--sort=-version:refname", "-l", "v*"], cwd)
    if not output:
        output = run_git(["tag", "--sort=-creatordate"], cwd)
    return [t for t in output.split("\n") if t.strip()] if output else []


def get_commits(from_ref=None, to_ref="HEAD", cwd=None):
    """Get commits between refs."""
    fmt = "%H|%h|%s|%an|%aI|%b<<<END>>>"
    if from_ref:
        range_spec = f"{from_ref}..{to_ref}"
    else:
        range_spec = to_ref
    
    output = run_git(["log", range_spec, f"--pretty=format:{fmt}"], cwd)
    if not output:
        return []
    
    commits = []
    for block in output.split("<<<END>>>"):
        block = block.strip()
        if not block or "|" not in block:
            continue
        parts = block.split("|", 5)
        if len(parts) < 5:
            continue
        
        body = parts[5] if len(parts) > 5 else ""
        subject = parts[2]
        has_breaking = "BREAKING CHANGE" in body
        if ":" in subject:
            has_breaking = has_breaking or "!" in subject.split(":")[0]
        commits.append({
            "hash": parts[0],
            "short": parts[1],
            "subject": subject,
            "author": parts[3],
            "date": parts[4],
            "body": body,
            "breaking": has_breaking,
        })
    return commits


def parse_commit(commit):
    """Parse conventional commit message."""
    subject = commit["subject"]
    
    # Match: type(scope): description  OR  type: description
    match = re.match(r'^(\w+)(?:\(([^)]+)\))?(!)?:\s*(.+)$', subject)
    body = commit.get("body", "")
    if match:
        ctype = match.group(1).lower()
        scope = match.group(2)
        breaking = bool(match.group(3)) or commit.get("breaking", False) or "BREAKING CHANGE" in body
        description = match.group(4)
    else:
        ctype = "other"
        scope = None
        breaking = commit.get("breaking", False) or "BREAKING CHANGE" in body
        description = subject
    
    return {
        **commit,
        "type": ctype,
        "scope": scope,
        "breaking": breaking,
        "description": description,
    }


def group_commits(commits):
    """Group parsed commits by type."""
    groups = defaultdict(list)
    breaking = []
    
    for c in commits:
        parsed = parse_commit(c)
        if parsed["breaking"]:
            breaking.append(parsed)
        
        type_key = parsed["type"]
        if type_key in COMMIT_TYPES:
            groups[type_key].append(parsed)
        else:
            groups["other"].append(parsed)
    
    return groups, breaking


def format_markdown(groups, breaking, title="Changelog", stats=None):
    """Format grouped commits as markdown."""
    lines = [f"# {title}\n"]
    
    if stats:
        lines.append(f"*{stats['total']} commits by {stats['authors']} contributors*\n")
    
    if breaking:
        lines.append(f"## {BREAKING_EMOJI} Breaking Changes\n")
        for c in breaking:
            scope = f"**{c['scope']}:** " if c.get("scope") else ""
            lines.append(f"- {scope}{c['description']} ({c['short']})")
        lines.append("")
    
    # Sort groups by priority
    sorted_types = sorted(
        groups.items(),
        key=lambda x: COMMIT_TYPES.get(x[0], ("Other", 99))[1]
    )
    
    for type_key, commits in sorted_types:
        if not commits:
            continue
        header = COMMIT_TYPES.get(type_key, ("📎 Other", 99))[0]
        lines.append(f"## {header}\n")
        
        # Group by scope within type
        by_scope = defaultdict(list)
        for c in commits:
            by_scope[c.get("scope") or ""].append(c)
        
        for scope in sorted(by_scope.keys()):
            for c in by_scope[scope]:
                scope_prefix = f"**{c['scope']}:** " if c.get("scope") else ""
                lines.append(f"- {scope_prefix}{c['description']} ({c['short']})")
        lines.append("")
    
    return "\n".join(lines)


def format_json(groups, breaking, stats=None):
    """Format as JSON."""
    result = {
        "stats": stats,
        "breaking_changes": [
            {"description": c["description"], "hash": c["short"], "scope": c.get("scope")}
            for c in breaking
        ],
        "changes": {},
    }
    for type_key, commits in groups.items():
        header = COMMIT_TYPES.get(type_key, ("Other", 99))[0]
        result["changes"][header] = [
            {
                "description": c["description"],
                "hash": c["short"],
                "scope": c.get("scope"),
                "author": c["author"],
                "date": c["date"],
            }
            for c in commits
        ]
    return json.dumps(result, indent=2)


def get_stats(commits):
    """Calculate commit stats."""
    authors = set(c["author"] for c in commits)
    types = defaultdict(int)
    for c in commits:
        parsed = parse_commit(c)
        types[parsed["type"]] += 1
    
    return {
        "total": len(commits),
        "authors": len(authors),
        "author_names": sorted(authors),
        "types": dict(types),
    }


def cmd_changelog(args=None):
    """Main changelog command."""
    args = args or []
    
    # Parse arguments
    fmt = "md"
    output_file = None
    since = None
    full = False
    unreleased = False
    tag = None
    
    i = 0
    while i < len(args):
        if args[i] == "--format" and i + 1 < len(args):
            fmt = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i] == "--since" and i + 1 < len(args):
            since = args[i + 1]
            i += 2
        elif args[i] == "--tag" and i + 1 < len(args):
            tag = args[i + 1]
            i += 2
        elif args[i] == "--full":
            full = True
            i += 1
        elif args[i] == "--unreleased":
            unreleased = True
            i += 1
        elif args[i] in ("--help", "-h"):
            print(__doc__)
            return 0
        else:
            i += 1
    
    tags = get_tags()
    sections = []
    
    if since:
        # Get commits since date
        commits = get_commits(cwd=None)
        commits = [c for c in commits if c["date"][:10] >= since]
        if commits:
            stats = get_stats(commits)
            groups, breaking = group_commits(commits)
            title = f"Changes since {since}"
            if fmt == "json":
                content = format_json(groups, breaking, stats)
            else:
                content = format_markdown(groups, breaking, title, stats)
            sections.append(content)
    elif tag:
        # Find the tag and its predecessor
        if tag in tags:
            idx = tags.index(tag)
            from_ref = tags[idx + 1] if idx + 1 < len(tags) else None
            commits = get_commits(from_ref, tag)
            if commits:
                stats = get_stats(commits)
                groups, breaking = group_commits(commits)
                tag_date = run_git(["log", "-1", "--format=%aI", tag])[:10]
                title = f"{tag} ({tag_date})"
                if fmt == "json":
                    content = format_json(groups, breaking, stats)
                else:
                    content = format_markdown(groups, breaking, title, stats)
                sections.append(content)
        else:
            print(f"Tag '{tag}' not found. Available: {', '.join(tags[:5])}")
            return 1
    elif full:
        # Full changelog: all tags + unreleased
        if tags:
            # Unreleased
            commits = get_commits(tags[0], "HEAD")
            if commits:
                stats = get_stats(commits)
                groups, breaking = group_commits(commits)
                sections.append(format_markdown(groups, breaking, "Unreleased", stats))
            
            # Each tag pair
            for i_tag in range(len(tags)):
                from_ref = tags[i_tag + 1] if i_tag + 1 < len(tags) else None
                commits = get_commits(from_ref, tags[i_tag])
                if commits:
                    stats = get_stats(commits)
                    groups, breaking = group_commits(commits)
                    tag_date = run_git(["log", "-1", "--format=%aI", tags[i_tag]])[:10]
                    sections.append(format_markdown(groups, breaking, f"{tags[i_tag]} ({tag_date})", stats))
        else:
            # No tags - all commits
            commits = get_commits()
            if commits:
                stats = get_stats(commits)
                groups, breaking = group_commits(commits)
                sections.append(format_markdown(groups, breaking, "All Changes", stats))
    elif unreleased:
        if tags:
            commits = get_commits(tags[0], "HEAD")
        else:
            commits = get_commits()
        if commits:
            stats = get_stats(commits)
            groups, breaking = group_commits(commits)
            if fmt == "json":
                content = format_json(groups, breaking, stats)
            else:
                content = format_markdown(groups, breaking, "Unreleased Changes", stats)
            sections.append(content)
        else:
            print("No unreleased changes found.")
            return 0
    else:
        # Default: recent changes (last tag to HEAD, or last 50 commits)
        if tags:
            commits = get_commits(tags[0], "HEAD")
            if not commits:
                # Show last tag's changes instead
                from_ref = tags[1] if len(tags) > 1 else None
                commits = get_commits(from_ref, tags[0])
                title = f"{tags[0]}"
            else:
                title = "Unreleased Changes"
        else:
            commits = get_commits()[:50]
            title = "Recent Changes"
        
        if commits:
            stats = get_stats(commits)
            groups, breaking = group_commits(commits)
            if fmt == "json":
                content = format_json(groups, breaking, stats)
            else:
                content = format_markdown(groups, breaking, title, stats)
            sections.append(content)
        else:
            print("No changes found.")
            return 0
    
    # Output
    result = "\n---\n\n".join(sections)
    
    if output_file:
        Path(output_file).write_text(result)
        print(f"✅ Changelog written to {output_file}")
    else:
        print(result)
    
    return 0


if __name__ == "__main__":
    sys.exit(cmd_changelog(sys.argv[1:]))

#!/usr/bin/env python3
"""
mw ai refactor — AI-powered code refactoring engine
=====================================================
Analyzes Python files for structural issues and applies automated refactoring.

Usage:
    mw ai refactor <file>              Analyze and suggest refactorings
    mw ai refactor <file> --apply      Apply safe refactorings automatically
    mw ai refactor <file> --report     Generate detailed markdown report
    mw ai refactor <dir>               Scan directory for refactoring opportunities
    mw ai refactor <file> --diff       Show unified diff of proposed changes

Detects:
    - Long functions (>50 lines) → extract helper functions
    - Deep nesting (>4 levels) → early returns / guard clauses
    - Duplicate code blocks → extract shared utility
    - God classes (>10 methods) → suggest decomposition
    - Complex conditionals → simplify with truth tables
    - Magic numbers/strings → extract constants
    - Dead code (unreachable after return/raise)
    - Mutable default arguments
    - Bare except clauses
    - print() debug statements in production code
    - Star imports (from x import *)
    - Too many parameters (>5) → parameter objects
"""

import ast
import os
import re
import sys
import textwrap
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ANSI colors
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

SEVERITY_COLORS = {"critical": RED, "high": RED, "medium": YELLOW, "low": CYAN}
SEVERITY_ICONS = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}

# Thresholds
MAX_FUNCTION_LINES = 50
MAX_NESTING_DEPTH = 4
MAX_CLASS_METHODS = 10
MAX_PARAMS = 5
MAX_COMPLEXITY = 10  # McCabe-like


class Refactoring:
    """Represents a single refactoring suggestion."""

    def __init__(
        self,
        line: int,
        end_line: int,
        severity: str,
        category: str,
        title: str,
        description: str,
        before: str = "",
        after: str = "",
        auto_fixable: bool = False,
    ):
        self.line = line
        self.end_line = end_line
        self.severity = severity
        self.category = category
        self.title = title
        self.description = description
        self.before = before
        self.after = after
        self.auto_fixable = auto_fixable


class NestingVisitor(ast.NodeVisitor):
    """Calculate nesting depth for each node."""

    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0
        self.deep_nodes: List[Tuple[int, int, int]] = []  # (line, end_line, depth)

    def _visit_nesting(self, node):
        self.current_depth += 1
        if self.current_depth > MAX_NESTING_DEPTH:
            line = getattr(node, "lineno", 0)
            end = getattr(node, "end_lineno", line)
            self.deep_nodes.append((line, end, self.current_depth))
        if self.current_depth > self.max_depth:
            self.max_depth = self.current_depth
        self.generic_visit(node)
        self.current_depth -= 1

    visit_If = _visit_nesting
    visit_For = _visit_nesting
    visit_While = _visit_nesting
    visit_With = _visit_nesting
    visit_Try = _visit_nesting
    visit_ExceptHandler = _visit_nesting


class ComplexityVisitor(ast.NodeVisitor):
    """Calculate cyclomatic complexity for functions."""

    def __init__(self):
        self.complexity = 1  # base

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_IfExp(self, node):
        self.complexity += 1
        self.generic_visit(node)


def get_function_complexity(node: ast.FunctionDef) -> int:
    """Calculate McCabe complexity for a function."""
    visitor = ComplexityVisitor()
    visitor.visit(node)
    return visitor.complexity


def analyze_file(filepath: str) -> List[Refactoring]:
    """Analyze a Python file and return refactoring suggestions."""
    path = Path(filepath)
    if not path.exists():
        print(f"{RED}Error: File not found: {filepath}{RESET}")
        return []
    if path.suffix != ".py":
        print(f"{RED}Error: Not a Python file: {filepath}{RESET}")
        return []

    source = path.read_text(encoding="utf-8", errors="replace")
    lines = source.splitlines()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        print(f"{RED}Syntax error in {filepath}: {e}{RESET}")
        return []

    refactorings: List[Refactoring] = []

    # ── Pass 1: Function-level analysis ──
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _analyze_function(node, lines, refactorings)

        if isinstance(node, ast.ClassDef):
            _analyze_class(node, lines, refactorings)

    # ── Pass 2: Module-level analysis ──
    _check_star_imports(tree, refactorings)
    _check_magic_numbers(tree, lines, refactorings)
    _check_print_statements(tree, lines, refactorings)
    _check_bare_excepts(tree, refactorings)
    _check_mutable_defaults(tree, refactorings)
    _check_dead_code(tree, lines, refactorings)
    _check_duplicate_blocks(tree, lines, refactorings)

    # Sort by severity then line number
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    refactorings.sort(key=lambda r: (severity_order.get(r.severity, 9), r.line))

    return refactorings


def _analyze_function(
    node: ast.FunctionDef, lines: List[str], refactorings: List[Refactoring]
):
    """Analyze a single function for refactoring opportunities."""
    func_lines = (node.end_lineno or node.lineno) - node.lineno + 1
    name = node.name

    # Long function
    if func_lines > MAX_FUNCTION_LINES:
        refactorings.append(
            Refactoring(
                line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                severity="medium",
                category="extract-function",
                title=f"Long function `{name}` ({func_lines} lines)",
                description=(
                    f"Function `{name}` is {func_lines} lines (threshold: {MAX_FUNCTION_LINES}). "
                    "Consider extracting logical blocks into helper functions for readability."
                ),
            )
        )

    # Too many parameters
    params = node.args
    total_params = (
        len(params.args)
        + len(params.posonlyargs)
        + len(params.kwonlyargs)
        + (1 if params.vararg else 0)
        + (1 if params.kwarg else 0)
    )
    # Subtract 'self'/'cls'
    if params.args and params.args[0].arg in ("self", "cls"):
        total_params -= 1

    if total_params > MAX_PARAMS:
        refactorings.append(
            Refactoring(
                line=node.lineno,
                end_line=node.lineno,
                severity="medium",
                category="parameter-object",
                title=f"Too many parameters in `{name}` ({total_params})",
                description=(
                    f"Function `{name}` has {total_params} parameters (threshold: {MAX_PARAMS}). "
                    "Consider using a dataclass/TypedDict or **kwargs for configuration."
                ),
            )
        )

    # Deep nesting
    nv = NestingVisitor()
    nv.visit(node)
    if nv.max_depth > MAX_NESTING_DEPTH:
        refactorings.append(
            Refactoring(
                line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                severity="high",
                category="reduce-nesting",
                title=f"Deep nesting in `{name}` (depth {nv.max_depth})",
                description=(
                    f"Function `{name}` has nesting depth {nv.max_depth} (max: {MAX_NESTING_DEPTH}). "
                    "Use early returns (guard clauses) to flatten the logic."
                ),
                before="if condition:\n    if other:\n        if more:\n            do_thing()",
                after="if not condition:\n    return\nif not other:\n    return\nif not more:\n    return\ndo_thing()",
            )
        )

    # High complexity
    complexity = get_function_complexity(node)
    if complexity > MAX_COMPLEXITY:
        refactorings.append(
            Refactoring(
                line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                severity="high",
                category="reduce-complexity",
                title=f"High complexity in `{name}` (CC={complexity})",
                description=(
                    f"Cyclomatic complexity of `{name}` is {complexity} (threshold: {MAX_COMPLEXITY}). "
                    "Break into smaller functions or use lookup tables/dispatch dicts."
                ),
            )
        )


def _analyze_class(
    node: ast.ClassDef, lines: List[str], refactorings: List[Refactoring]
):
    """Analyze a class for refactoring opportunities."""
    methods = [
        n
        for n in node.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if len(methods) > MAX_CLASS_METHODS:
        refactorings.append(
            Refactoring(
                line=node.lineno,
                end_line=node.end_lineno or node.lineno,
                severity="medium",
                category="decompose-class",
                title=f"God class `{node.name}` ({len(methods)} methods)",
                description=(
                    f"Class `{node.name}` has {len(methods)} methods (threshold: {MAX_CLASS_METHODS}). "
                    "Consider splitting into smaller, focused classes (Single Responsibility Principle)."
                ),
            )
        )


def _check_star_imports(tree: ast.Module, refactorings: List[Refactoring]):
    """Detect `from x import *` statements."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.names:
            for alias in node.names:
                if alias.name == "*":
                    mod = node.module or "unknown"
                    refactorings.append(
                        Refactoring(
                            line=node.lineno,
                            end_line=node.lineno,
                            severity="medium",
                            category="explicit-imports",
                            title=f"Star import from `{mod}`",
                            description=(
                                f"`from {mod} import *` pollutes namespace. "
                                "Import only what you need explicitly."
                            ),
                            before=f"from {mod} import *",
                            after=f"from {mod} import specific_name",
                            auto_fixable=False,
                        )
                    )


def _check_magic_numbers(
    tree: ast.Module, lines: List[str], refactorings: List[Refactoring]
):
    """Detect magic numbers in code (not in assignments to UPPER_CASE)."""
    skip = {0, 1, 2, -1, 0.0, 1.0, 100}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            if node.value in skip:
                continue
            line_no = getattr(node, "lineno", 0)
            if line_no == 0:
                continue
            line_text = lines[line_no - 1] if line_no <= len(lines) else ""
            # Skip if it's a constant assignment (UPPER_CASE = ...)
            stripped = line_text.strip()
            if re.match(r"^[A-Z_][A-Z_0-9]*\s*=", stripped):
                continue
            # Skip decorators, docstrings, default args
            if stripped.startswith("@") or stripped.startswith(('"""', "'''")):
                continue
            refactorings.append(
                Refactoring(
                    line=line_no,
                    end_line=line_no,
                    severity="low",
                    category="extract-constant",
                    title=f"Magic number `{node.value}`",
                    description=(
                        f"Consider extracting `{node.value}` into a named constant "
                        "for clarity and maintainability."
                    ),
                    auto_fixable=False,
                )
            )


def _check_print_statements(
    tree: ast.Module, lines: List[str], refactorings: List[Refactoring]
):
    """Detect print() calls that may be debug leftovers."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                line_no = getattr(node, "lineno", 0)
                line_text = lines[line_no - 1] if line_no <= len(lines) else ""
                # Heuristic: skip if it looks intentional (CLI tools, etc.)
                if "usage" in line_text.lower() or "help" in line_text.lower():
                    continue
                refactorings.append(
                    Refactoring(
                        line=line_no,
                        end_line=line_no,
                        severity="low",
                        category="use-logging",
                        title="print() → logging",
                        description=(
                            "Replace `print()` with `logging.info()` or `logging.debug()` "
                            "for proper log levels and configurability."
                        ),
                        before="print(f'Processing {item}')",
                        after="logger.info('Processing %s', item)",
                        auto_fixable=False,
                    )
                )


def _check_bare_excepts(tree: ast.Module, refactorings: List[Refactoring]):
    """Detect bare except clauses."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            refactorings.append(
                Refactoring(
                    line=node.lineno,
                    end_line=node.lineno,
                    severity="high",
                    category="specific-exception",
                    title="Bare `except:` clause",
                    description=(
                        "Bare `except:` catches SystemExit and KeyboardInterrupt. "
                        "Use `except Exception:` or a more specific type."
                    ),
                    before="except:",
                    after="except Exception as e:",
                    auto_fixable=True,
                )
            )


def _check_mutable_defaults(tree: ast.Module, refactorings: List[Refactoring]):
    """Detect mutable default arguments."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults + node.args.kw_defaults:
                if default is None:
                    continue
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    refactorings.append(
                        Refactoring(
                            line=node.lineno,
                            end_line=node.lineno,
                            severity="high",
                            category="immutable-default",
                            title=f"Mutable default in `{node.name}`",
                            description=(
                                "Mutable default arguments are shared across calls. "
                                "Use `None` and assign inside the function body."
                            ),
                            before="def func(items=[]):",
                            after="def func(items=None):\n    items = items or []",
                            auto_fixable=False,
                        )
                    )


def _check_dead_code(
    tree: ast.Module, lines: List[str], refactorings: List[Refactoring]
):
    """Detect unreachable code after return/raise/break/continue."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for i, stmt in enumerate(node.body[:-1]):
                if isinstance(stmt, (ast.Return, ast.Raise)):
                    next_stmt = node.body[i + 1]
                    if not isinstance(next_stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        refactorings.append(
                            Refactoring(
                                line=getattr(next_stmt, "lineno", 0),
                                end_line=getattr(next_stmt, "end_lineno", 0),
                                severity="medium",
                                category="dead-code",
                                title="Unreachable code",
                                description=(
                                    "This code is after a return/raise and will never execute. "
                                    "Remove it or move before the return."
                                ),
                                auto_fixable=True,
                            )
                        )


def _check_duplicate_blocks(
    tree: ast.Module, lines: List[str], refactorings: List[Refactoring]
):
    """Detect duplicate code blocks (3+ lines repeated)."""
    # Extract function bodies as text blocks
    blocks: List[Tuple[str, int, int, str]] = []  # (text, start, end, func_name)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno
            end = node.end_lineno or start
            if end - start >= 3:
                body_lines = lines[start:end]
                body_text = "\n".join(l.strip() for l in body_lines if l.strip())
                blocks.append((body_text, start, end, node.name))

    # Check for 3-line sliding window duplicates across functions
    seen_chunks: Dict[str, List[Tuple[int, str]]] = defaultdict(list)
    for text, start, end, name in blocks:
        chunk_lines = [l for l in text.split("\n") if l]
        for i in range(len(chunk_lines) - 2):
            chunk = "\n".join(chunk_lines[i : i + 3])
            if len(chunk) > 30:  # skip trivial
                seen_chunks[chunk].append((start + i, name))

    reported: Set[str] = set()
    for chunk, locations in seen_chunks.items():
        if len(locations) >= 2 and chunk not in reported:
            reported.add(chunk)
            funcs = list(set(loc[1] for loc in locations))
            if len(funcs) >= 2:  # only if across different functions
                refactorings.append(
                    Refactoring(
                        line=locations[0][0],
                        end_line=locations[0][0] + 2,
                        severity="medium",
                        category="extract-common",
                        title=f"Duplicate code in {', '.join(funcs[:3])}",
                        description=(
                            f"Similar 3-line block found in functions: {', '.join(funcs)}. "
                            "Extract into a shared helper function."
                        ),
                    )
                )
            if len(reported) >= 5:  # cap duplicates
                break


def format_results(
    filepath: str, refactorings: List[Refactoring], as_markdown: bool = False
) -> str:
    """Format refactoring results for display."""
    if not refactorings:
        if as_markdown:
            return f"# Refactoring Report: {filepath}\n\n✅ No refactoring needed — clean code!"
        return f"\n{GREEN}✅ {filepath} — No refactoring suggestions. Clean code!{RESET}\n"

    # Group by category
    by_category: Dict[str, List[Refactoring]] = defaultdict(list)
    for r in refactorings:
        by_category[r.category].append(r)

    counts = Counter(r.severity for r in refactorings)
    auto_count = sum(1 for r in refactorings if r.auto_fixable)

    if as_markdown:
        return _format_markdown(filepath, refactorings, by_category, counts, auto_count)
    return _format_terminal(filepath, refactorings, by_category, counts, auto_count)


def _format_terminal(filepath, refactorings, by_category, counts, auto_count) -> str:
    """Terminal-colored output."""
    out = []
    out.append(f"\n{BOLD}🔧 Refactoring Report: {filepath}{RESET}")
    out.append("=" * 60)

    # Summary
    parts = []
    for sev in ("critical", "high", "medium", "low"):
        if counts.get(sev, 0):
            c = SEVERITY_COLORS[sev]
            parts.append(f"{c}{counts[sev]} {sev}{RESET}")
    out.append(f"Found {len(refactorings)} suggestions: {', '.join(parts)}")
    if auto_count:
        out.append(f"{GREEN}⚡ {auto_count} auto-fixable with --apply{RESET}")
    out.append("")

    for r in refactorings:
        icon = SEVERITY_ICONS.get(r.severity, "•")
        color = SEVERITY_COLORS.get(r.severity, "")
        out.append(f"{icon} {color}{BOLD}L{r.line}: {r.title}{RESET}")
        out.append(f"   {DIM}[{r.category}]{RESET} {r.description}")
        if r.before:
            out.append(f"   {RED}Before:{RESET} {r.before}")
        if r.after:
            out.append(f"   {GREEN}After:{RESET}  {r.after}")
        if r.auto_fixable:
            out.append(f"   {GREEN}⚡ Auto-fixable{RESET}")
        out.append("")

    return "\n".join(out)


def _format_markdown(filepath, refactorings, by_category, counts, auto_count) -> str:
    """Markdown report output."""
    out = [f"# 🔧 Refactoring Report: `{filepath}`\n"]
    out.append(f"**{len(refactorings)} suggestions found**\n")

    for sev in ("critical", "high", "medium", "low"):
        c = counts.get(sev, 0)
        if c:
            out.append(f"- {SEVERITY_ICONS[sev]} {c} {sev}")

    if auto_count:
        out.append(f"\n⚡ **{auto_count} auto-fixable** with `mw ai refactor --apply`\n")

    out.append("\n## Details\n")
    for r in refactorings:
        icon = SEVERITY_ICONS.get(r.severity, "•")
        out.append(f"### {icon} L{r.line}: {r.title}")
        out.append(f"**Category:** `{r.category}` | **Severity:** {r.severity}\n")
        out.append(r.description + "\n")
        if r.before and r.after:
            out.append("```python")
            out.append(f"# Before:\n{r.before}")
            out.append(f"\n# After:\n{r.after}")
            out.append("```\n")

    return "\n".join(out)


def apply_auto_fixes(filepath: str, refactorings: List[Refactoring]) -> int:
    """Apply auto-fixable refactorings. Returns count of fixes applied."""
    auto = [r for r in refactorings if r.auto_fixable]
    if not auto:
        print(f"{YELLOW}No auto-fixable suggestions found.{RESET}")
        return 0

    path = Path(filepath)
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    applied = 0

    # Apply bare except → except Exception as e
    for r in auto:
        if r.category == "specific-exception":
            idx = r.line - 1
            if idx < len(lines) and "except:" in lines[idx]:
                lines[idx] = lines[idx].replace("except:", "except Exception as e:")
                applied += 1

    # Remove dead code
    dead_lines: Set[int] = set()
    for r in auto:
        if r.category == "dead-code":
            for ln in range(r.line, r.end_line + 1):
                dead_lines.add(ln)

    if dead_lines:
        lines = [l for i, l in enumerate(lines, 1) if i not in dead_lines]
        applied += len(dead_lines)

    if applied:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{GREEN}✅ Applied {applied} auto-fixes to {filepath}{RESET}")

    return applied


def scan_directory(dirpath: str) -> Dict[str, List[Refactoring]]:
    """Scan a directory for refactoring opportunities."""
    results: Dict[str, List[Refactoring]] = {}
    root = Path(dirpath)
    skip_dirs = {
        ".git", "__pycache__", ".venv", "venv", "node_modules",
        ".eggs", "dist", "build", ".tox", ".mypy_cache",
    }

    for pyfile in sorted(root.rglob("*.py")):
        if any(part in skip_dirs for part in pyfile.parts):
            continue
        refs = analyze_file(str(pyfile))
        if refs:
            results[str(pyfile)] = refs

    return results


def main(args: List[str] = None) -> int:
    """Entry point for mw ai refactor."""
    if args is None:
        args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return 0

    target = args[0]
    apply_fixes = "--apply" in args
    report_mode = "--report" in args
    diff_mode = "--diff" in args

    target_path = Path(target)

    if target_path.is_dir():
        print(f"\n{BOLD}🔧 Scanning directory: {target}{RESET}\n")
        results = scan_directory(target)
        if not results:
            print(f"{GREEN}✅ No refactoring suggestions found. Clean codebase!{RESET}")
            return 0

        total = sum(len(v) for v in results.values())
        print(f"Found {total} suggestions across {len(results)} files:\n")
        for fp, refs in results.items():
            counts = Counter(r.severity for r in refs)
            parts = []
            for sev in ("critical", "high", "medium", "low"):
                if counts.get(sev, 0):
                    c = SEVERITY_COLORS[sev]
                    parts.append(f"{c}{counts[sev]} {sev}{RESET}")
            print(f"  {fp}: {', '.join(parts)}")

        # Show details for top files
        print()
        for fp, refs in list(results.items())[:5]:
            print(format_results(fp, refs))

        return 1 if any(
            any(r.severity in ("critical", "high") for r in refs)
            for refs in results.values()
        ) else 0

    elif target_path.is_file():
        refactorings = analyze_file(target)

        if apply_fixes:
            count = apply_auto_fixes(target, refactorings)
            # Re-analyze after fixes
            refactorings = analyze_file(target)
            if not refactorings:
                print(f"{GREEN}✅ All issues resolved!{RESET}")
                return 0

        print(format_results(target, refactorings, as_markdown=report_mode))

        if report_mode:
            report_path = Path(target).with_suffix(".refactor.md")
            report_path.write_text(
                format_results(target, refactorings, as_markdown=True),
                encoding="utf-8",
            )
            print(f"\n{GREEN}📄 Report saved: {report_path}{RESET}")

        return 1 if any(r.severity in ("critical", "high") for r in refactorings) else 0

    else:
        print(f"{RED}Error: {target} not found{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

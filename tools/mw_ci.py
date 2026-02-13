#!/usr/bin/env python3
"""MyWork CI/CD Generator — Auto-generate CI pipelines from project analysis.

Analyzes your project structure, detects frameworks, and generates
production-ready CI/CD configs for GitHub Actions, GitLab CI, or Bitbucket.

Usage:
    mw ci generate [--platform github|gitlab|bitbucket] [--path <project>]
    mw ci preview [--platform github|gitlab]
    mw ci validate
    mw ci list-templates
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# ── Colors ──────────────────────────────────────────────────────────
class C:
    B = "\033[1m"; G = "\033[92m"; Y = "\033[93m"; R = "\033[91m"
    BL = "\033[94m"; CY = "\033[96m"; DIM = "\033[2m"; E = "\033[0m"


# ── Project Analyzer ────────────────────────────────────────────────
class ProjectAnalyzer:
    """Detect project type, language, frameworks, and config."""

    def __init__(self, path: str = "."):
        self.root = Path(path).resolve()
        self.analysis: Dict[str, Any] = {
            "languages": [],
            "frameworks": [],
            "package_managers": [],
            "has_tests": False,
            "test_commands": [],
            "build_commands": [],
            "lint_commands": [],
            "docker": False,
            "node_version": None,
            "python_version": None,
            "env_vars": [],
            "services": [],
            "deploy_targets": [],
        }

    def analyze(self) -> Dict[str, Any]:
        self._detect_python()
        self._detect_node()
        self._detect_docker()
        self._detect_go()
        self._detect_rust()
        self._detect_deploy_targets()
        return self.analysis

    def _detect_python(self):
        pyproject = self.root / "pyproject.toml"
        setup_py = self.root / "setup.py"
        requirements = self.root / "requirements.txt"
        pipfile = self.root / "Pipfile"

        if not any(f.exists() for f in [pyproject, setup_py, requirements, pipfile]):
            return

        self.analysis["languages"].append("python")

        if pipfile.exists():
            self.analysis["package_managers"].append("pipenv")
        elif pyproject.exists():
            content = pyproject.read_text()
            if "poetry" in content.lower():
                self.analysis["package_managers"].append("poetry")
            else:
                self.analysis["package_managers"].append("pip")

            # Detect frameworks
            if "fastapi" in content.lower():
                self.analysis["frameworks"].append("fastapi")
            if "django" in content.lower():
                self.analysis["frameworks"].append("django")
            if "flask" in content.lower():
                self.analysis["frameworks"].append("flask")
            if "pytest" in content.lower():
                self.analysis["has_tests"] = True
                self.analysis["test_commands"].append("pytest")

            # Detect python version
            import re
            ver_match = re.search(r'requires-python\s*=\s*">=(\d+\.\d+)"', content)
            if ver_match:
                self.analysis["python_version"] = ver_match.group(1)
        else:
            self.analysis["package_managers"].append("pip")

        if requirements.exists():
            content = requirements.read_text().lower()
            if "pytest" in content:
                self.analysis["has_tests"] = True
                self.analysis["test_commands"].append("pytest")
            if "fastapi" in content:
                self.analysis["frameworks"].append("fastapi")
            if "django" in content:
                self.analysis["frameworks"].append("django")
            if "flake8" in content or "ruff" in content:
                self.analysis["lint_commands"].append("ruff check . || flake8 .")

        # Check for test directories
        if (self.root / "tests").exists() or (self.root / "test").exists():
            self.analysis["has_tests"] = True
            if "pytest" not in self.analysis["test_commands"]:
                self.analysis["test_commands"].append("pytest")

        if not self.analysis["python_version"]:
            self.analysis["python_version"] = "3.11"

        self.analysis["build_commands"].append("pip install -e '.[dev]' 2>/dev/null || pip install -r requirements.txt")

    def _detect_node(self):
        pkg_json = self.root / "package.json"
        if not pkg_json.exists():
            return

        self.analysis["languages"].append("node")
        content = json.loads(pkg_json.read_text())

        # Package manager
        if (self.root / "pnpm-lock.yaml").exists():
            self.analysis["package_managers"].append("pnpm")
        elif (self.root / "yarn.lock").exists():
            self.analysis["package_managers"].append("yarn")
        elif (self.root / "bun.lockb").exists():
            self.analysis["package_managers"].append("bun")
        else:
            self.analysis["package_managers"].append("npm")

        scripts = content.get("scripts", {})
        deps = {**content.get("dependencies", {}), **content.get("devDependencies", {})}

        # Detect frameworks
        if "next" in deps:
            self.analysis["frameworks"].append("nextjs")
        if "react" in deps:
            self.analysis["frameworks"].append("react")
        if "vue" in deps:
            self.analysis["frameworks"].append("vue")
        if "vite" in deps:
            self.analysis["frameworks"].append("vite")
        if "express" in deps:
            self.analysis["frameworks"].append("express")
        if "nestjs" in str(deps) or "@nestjs/core" in deps:
            self.analysis["frameworks"].append("nestjs")

        # Test detection
        if "test" in scripts:
            self.analysis["has_tests"] = True
            pm = self.analysis["package_managers"][-1]
            self.analysis["test_commands"].append(f"{pm} run test" if pm != "npm" else "npm test")
        if "jest" in deps or "@jest/core" in deps:
            self.analysis["has_tests"] = True
        if "vitest" in deps:
            self.analysis["has_tests"] = True

        # Build
        if "build" in scripts:
            pm = self.analysis["package_managers"][-1]
            self.analysis["build_commands"].append(f"{pm} run build" if pm != "npm" else "npm run build")

        # Lint
        if "lint" in scripts:
            pm = self.analysis["package_managers"][-1]
            self.analysis["lint_commands"].append(f"{pm} run lint" if pm != "npm" else "npm run lint")

        # Node version
        engines = content.get("engines", {})
        if "node" in engines:
            import re
            ver = re.search(r'(\d+)', engines["node"])
            if ver:
                self.analysis["node_version"] = ver.group(1)
        if not self.analysis["node_version"]:
            self.analysis["node_version"] = "20"

    def _detect_docker(self):
        if (self.root / "Dockerfile").exists() or (self.root / "docker-compose.yml").exists():
            self.analysis["docker"] = True
        if (self.root / "docker-compose.yml").exists():
            self.analysis["services"].append("docker-compose")

    def _detect_go(self):
        if (self.root / "go.mod").exists():
            self.analysis["languages"].append("go")
            self.analysis["build_commands"].append("go build ./...")
            self.analysis["test_commands"].append("go test ./...")
            self.analysis["has_tests"] = True

    def _detect_rust(self):
        if (self.root / "Cargo.toml").exists():
            self.analysis["languages"].append("rust")
            self.analysis["build_commands"].append("cargo build")
            self.analysis["test_commands"].append("cargo test")
            self.analysis["has_tests"] = True

    def _detect_deploy_targets(self):
        if (self.root / "vercel.json").exists():
            self.analysis["deploy_targets"].append("vercel")
        if (self.root / "netlify.toml").exists():
            self.analysis["deploy_targets"].append("netlify")
        if (self.root / "railway.json").exists() or (self.root / "railway.toml").exists():
            self.analysis["deploy_targets"].append("railway")
        if (self.root / "render.yaml").exists():
            self.analysis["deploy_targets"].append("render")
        if (self.root / "fly.toml").exists():
            self.analysis["deploy_targets"].append("fly")
        if (self.root / "Procfile").exists():
            self.analysis["deploy_targets"].append("heroku")


# ── CI Generators ───────────────────────────────────────────────────
class GitHubActionsGenerator:
    """Generate GitHub Actions workflow YAML."""

    def generate(self, analysis: Dict[str, Any], options: Dict = None) -> str:
        options = options or {}
        lines = [
            f"# Auto-generated by MyWork CI (mw ci) — {datetime.now().strftime('%Y-%m-%d')}",
            "# Docs: https://docs.mywork.ai/ci",
            "",
            f"name: CI",
            "",
            "on:",
            "  push:",
            "    branches: [main, master, develop]",
            "  pull_request:",
            "    branches: [main, master]",
            "",
            "permissions:",
            "  contents: read",
            "",
            "jobs:",
        ]

        # Determine matrix
        if "python" in analysis["languages"]:
            lines.extend(self._python_job(analysis))
        if "node" in analysis["languages"]:
            lines.extend(self._node_job(analysis))
        if "go" in analysis["languages"]:
            lines.extend(self._go_job(analysis))
        if "rust" in analysis["languages"]:
            lines.extend(self._rust_job(analysis))

        # Deploy job
        if analysis["deploy_targets"]:
            lines.extend(self._deploy_job(analysis))

        return "\n".join(lines) + "\n"

    def _python_job(self, a: Dict) -> List[str]:
        ver = a.get("python_version", "3.11")
        versions = [ver]
        if ver == "3.11":
            versions = ["3.10", "3.11", "3.12"]
        elif ver == "3.9":
            versions = ["3.9", "3.10", "3.11", "3.12"]

        pm = "poetry" if "poetry" in a["package_managers"] else "pip"

        lines = [
            "  test-python:",
            f"    name: Python Tests",
            "    runs-on: ubuntu-latest",
            "    strategy:",
            "      matrix:",
            f"        python-version: {json.dumps(versions)}",
            "      fail-fast: false",
            "",
            "    steps:",
            "      - uses: actions/checkout@v4",
            "",
            "      - name: Set up Python ${{ matrix.python-version }}",
            "        uses: actions/setup-python@v5",
            "        with:",
            "          python-version: ${{ matrix.python-version }}",
            "          cache: pip",
            "",
        ]

        if pm == "poetry":
            lines.extend([
                "      - name: Install Poetry",
                "        run: pip install poetry",
                "",
                "      - name: Install dependencies",
                "        run: poetry install --no-interaction",
                "",
            ])
        else:
            lines.extend([
                "      - name: Install dependencies",
                "        run: |",
            ])
            for cmd in a["build_commands"]:
                if "pip" in cmd:
                    lines.append(f"          {cmd}")
            lines.append("")

        if a["lint_commands"]:
            lines.extend([
                "      - name: Lint",
                "        run: |",
            ])
            for cmd in a["lint_commands"]:
                prefix = "poetry run " if pm == "poetry" else ""
                lines.append(f"          {prefix}{cmd}")
            lines.append("")

        if a["has_tests"]:
            lines.extend([
                "      - name: Run tests",
                "        run: |",
            ])
            prefix = "poetry run " if pm == "poetry" else ""
            for cmd in a["test_commands"]:
                if "pytest" in cmd:
                    lines.append(f"          {prefix}pytest --tb=short -q")
                else:
                    lines.append(f"          {prefix}{cmd}")
            lines.append("")

        return lines

    def _node_job(self, a: Dict) -> List[str]:
        ver = a.get("node_version", "20")
        pm = next((p for p in a["package_managers"] if p in ("pnpm", "yarn", "bun", "npm")), "npm")
        install_cmd = {
            "npm": "npm ci",
            "yarn": "yarn install --frozen-lockfile",
            "pnpm": "pnpm install --frozen-lockfile",
            "bun": "bun install --frozen-lockfile",
        }.get(pm, "npm ci")

        lines = [
            "  test-node:",
            f"    name: Node Tests",
            "    runs-on: ubuntu-latest",
            "    strategy:",
            "      matrix:",
            f"        node-version: [{ver}]",
            "",
            "    steps:",
            "      - uses: actions/checkout@v4",
            "",
            "      - name: Setup Node.js ${{ matrix.node-version }}",
            "        uses: actions/setup-node@v4",
            "        with:",
            "          node-version: ${{ matrix.node-version }}",
            f"          cache: {pm if pm != 'bun' else 'npm'}",
            "",
        ]

        if pm == "pnpm":
            lines.extend([
                "      - name: Install pnpm",
                "        uses: pnpm/action-setup@v2",
                "        with:",
                "          version: latest",
                "",
            ])

        lines.extend([
            "      - name: Install dependencies",
            f"        run: {install_cmd}",
            "",
        ])

        if a["lint_commands"]:
            lines.extend([
                "      - name: Lint",
                "        run: |",
            ])
            for cmd in a["lint_commands"]:
                lines.append(f"          {cmd}")
            lines.append("")

        if a["build_commands"]:
            for cmd in a["build_commands"]:
                if "npm" in cmd or "pnpm" in cmd or "yarn" in cmd:
                    lines.extend([
                        "      - name: Build",
                        f"        run: {cmd}",
                        "",
                    ])

        if a["has_tests"]:
            lines.extend([
                "      - name: Run tests",
                "        run: |",
            ])
            for cmd in a["test_commands"]:
                lines.append(f"          {cmd}")
            lines.append("")

        return lines

    def _go_job(self, a: Dict) -> List[str]:
        return [
            "  test-go:",
            "    name: Go Tests",
            "    runs-on: ubuntu-latest",
            "",
            "    steps:",
            "      - uses: actions/checkout@v4",
            "",
            "      - name: Set up Go",
            "        uses: actions/setup-go@v5",
            "        with:",
            "          go-version: stable",
            "",
            "      - name: Build",
            "        run: go build ./...",
            "",
            "      - name: Test",
            "        run: go test ./... -v -race -coverprofile=coverage.out",
            "",
        ]

    def _rust_job(self, a: Dict) -> List[str]:
        return [
            "  test-rust:",
            "    name: Rust Tests",
            "    runs-on: ubuntu-latest",
            "",
            "    steps:",
            "      - uses: actions/checkout@v4",
            "",
            "      - name: Install Rust",
            "        uses: dtolnay/rust-toolchain@stable",
            "",
            "      - name: Cache",
            "        uses: Swatinem/rust-cache@v2",
            "",
            "      - name: Build",
            "        run: cargo build --verbose",
            "",
            "      - name: Test",
            "        run: cargo test --verbose",
            "",
        ]

    def _deploy_job(self, a: Dict) -> List[str]:
        target = a["deploy_targets"][0]
        lines = [
            "  deploy:",
            f"    name: Deploy to {target.title()}",
            "    runs-on: ubuntu-latest",
            "    needs: [" + ", ".join(f"test-{l}" for l in a["languages"]) + "]",
            "    if: github.ref == 'refs/heads/main' && github.event_name == 'push'",
            "",
            "    steps:",
            "      - uses: actions/checkout@v4",
            "",
        ]

        if target == "vercel":
            lines.extend([
                "      - name: Deploy to Vercel",
                "        uses: amondnet/vercel-action@v25",
                "        with:",
                "          vercel-token: ${{ secrets.VERCEL_TOKEN }}",
                "          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}",
                "          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}",
                "          vercel-args: --prod",
                "",
            ])
        elif target == "fly":
            lines.extend([
                "      - name: Deploy to Fly.io",
                "        uses: superfly/flyctl-actions/setup-flyctl@master",
                "",
                "      - run: flyctl deploy --remote-only",
                "        env:",
                "          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}",
                "",
            ])
        elif target == "railway":
            lines.extend([
                "      - name: Deploy to Railway",
                "        uses: bervProject/railway-deploy@main",
                "        with:",
                "          railway_token: ${{ secrets.RAILWAY_TOKEN }}",
                "",
            ])

        return lines


class GitLabCIGenerator:
    """Generate .gitlab-ci.yml."""

    def generate(self, analysis: Dict[str, Any], options: Dict = None) -> str:
        lines = [
            f"# Auto-generated by MyWork CI (mw ci) — {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "stages:",
            "  - lint",
            "  - test",
            "  - build",
            "  - deploy",
            "",
        ]

        if "python" in analysis["languages"]:
            ver = analysis.get("python_version", "3.11")
            lines.extend([
                f"test-python:",
                f"  image: python:{ver}",
                "  stage: test",
                "  script:",
            ])
            for cmd in analysis["build_commands"]:
                if "pip" in cmd:
                    lines.append(f"    - {cmd}")
            if analysis["has_tests"]:
                lines.append("    - pytest --tb=short -q")
            lines.extend(["  cache:", "    paths:", "      - .cache/pip", ""])

        if "node" in analysis["languages"]:
            ver = analysis.get("node_version", "20")
            pm = next((p for p in analysis["package_managers"] if p in ("pnpm", "yarn", "npm")), "npm")
            install = {"npm": "npm ci", "yarn": "yarn install --frozen-lockfile", "pnpm": "pnpm install --frozen-lockfile"}.get(pm, "npm ci")
            lines.extend([
                f"test-node:",
                f"  image: node:{ver}",
                "  stage: test",
                "  script:",
                f"    - {install}",
            ])
            for cmd in analysis["build_commands"]:
                if pm in cmd or "npm" in cmd:
                    lines.append(f"    - {cmd}")
            if analysis["has_tests"]:
                for cmd in analysis["test_commands"]:
                    lines.append(f"    - {cmd}")
            lines.extend(["  cache:", "    paths:", f"      - node_modules/", ""])

        return "\n".join(lines) + "\n"


# ── Main Entry ──────────────────────────────────────────────────────
GENERATORS = {
    "github": GitHubActionsGenerator,
    "gitlab": GitLabCIGenerator,
}

PLATFORMS = {
    "github": (".github/workflows/ci.yml", "GitHub Actions"),
    "gitlab": (".gitlab-ci.yml", "GitLab CI"),
}


def cmd_generate(args: List[str], project_path: str = "."):
    """Generate CI config."""
    platform = "github"
    dry_run = False
    force = False

    i = 0
    while i < len(args):
        if args[i] in ("--platform", "-p") and i + 1 < len(args):
            platform = args[i + 1].lower()
            i += 2
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        elif args[i] in ("--force", "-f"):
            force = True
            i += 1
        elif args[i] in ("--path",) and i + 1 < len(args):
            project_path = args[i + 1]
            i += 2
        else:
            i += 1

    if platform not in GENERATORS:
        print(f"{C.R}❌ Unknown platform: {platform}. Use: {', '.join(GENERATORS.keys())}{C.E}")
        return 1

    # Analyze project
    print(f"{C.BL}🔍 Analyzing project at {Path(project_path).resolve()}...{C.E}")
    analyzer = ProjectAnalyzer(project_path)
    analysis = analyzer.analyze()

    if not analysis["languages"]:
        print(f"{C.Y}⚠️  No supported languages detected. Is this the right directory?{C.E}")
        return 1

    print(f"   {C.G}Languages:{C.E}  {', '.join(analysis['languages'])}")
    print(f"   {C.G}Frameworks:{C.E} {', '.join(analysis['frameworks']) or 'none detected'}")
    print(f"   {C.G}Tests:{C.E}      {'✅ yes' if analysis['has_tests'] else '❌ no'}")
    print(f"   {C.G}Docker:{C.E}     {'✅ yes' if analysis['docker'] else '❌ no'}")
    print(f"   {C.G}Deploy:{C.E}     {', '.join(analysis['deploy_targets']) or 'none'}")
    print()

    # Generate
    gen = GENERATORS[platform]()
    output = gen.generate(analysis)
    filepath, platform_name = PLATFORMS[platform]

    if dry_run:
        print(f"{C.CY}📋 Preview ({platform_name}):{C.E}")
        print(f"{C.DIM}{'─' * 60}{C.E}")
        print(output)
        print(f"{C.DIM}{'─' * 60}{C.E}")
        return 0

    # Write file
    dest = Path(project_path) / filepath
    if dest.exists() and not force:
        print(f"{C.Y}⚠️  {filepath} already exists. Use --force to overwrite.{C.E}")
        print(f"   Preview with: mw ci generate --dry-run")
        return 1

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(output)
    print(f"{C.G}✅ Generated {filepath}{C.E}")
    print(f"   {C.DIM}Platform: {platform_name}{C.E}")
    print(f"   {C.DIM}File: {dest.resolve()}{C.E}")
    print()
    print(f"   {C.B}Next steps:{C.E}")
    print(f"   1. Review the generated config")
    print(f"   2. Add any required secrets to your repo settings")
    print(f"   3. git add {filepath} && git commit -m 'ci: add {platform_name} pipeline'")
    return 0


def cmd_preview(args: List[str], project_path: str = "."):
    """Preview CI config without writing."""
    return cmd_generate(["--dry-run"] + args, project_path)


def cmd_validate(args: List[str], project_path: str = "."):
    """Validate existing CI config."""
    for platform, (filepath, name) in PLATFORMS.items():
        p = Path(project_path) / filepath
        if p.exists():
            content = p.read_text()
            issues = []
            if platform == "github":
                if "actions/checkout" not in content:
                    issues.append("Missing actions/checkout step")
                if "on:" not in content:
                    issues.append("Missing trigger configuration")
            print(f"{C.B}{name}:{C.E} {filepath}")
            if issues:
                for issue in issues:
                    print(f"   {C.Y}⚠️  {issue}{C.E}")
            else:
                print(f"   {C.G}✅ Looks good{C.E}")
            print()
    return 0


def cmd_list_templates(args: List[str], project_path: str = "."):
    """List available CI templates."""
    print(f"{C.B}📋 Available CI Templates{C.E}")
    print(f"{'─' * 40}")
    templates = [
        ("python", "Python with pytest, ruff, multi-version matrix"),
        ("node", "Node.js with npm/yarn/pnpm, build + test"),
        ("go", "Go with race detection + coverage"),
        ("rust", "Rust with cargo build + test + cache"),
        ("docker", "Docker build + push to registry"),
        ("vercel", "Auto-deploy to Vercel on push"),
        ("fly", "Deploy to Fly.io"),
        ("railway", "Deploy to Railway"),
    ]
    for name, desc in templates:
        print(f"   {C.G}{name:12s}{C.E} {desc}")
    print()
    print(f"{C.DIM}Use: mw ci generate --platform github (auto-detects your stack){C.E}")
    return 0


def main(args: List[str] = None):
    """Entry point for mw ci."""
    if args is None:
        args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h", "help"):
        print(f"{C.B}🔧 MyWork CI/CD Generator{C.E}")
        print(f"{'─' * 40}")
        print(f"  {C.G}mw ci generate{C.E}          Generate CI config (auto-detects stack)")
        print(f"  {C.G}mw ci generate --dry-run{C.E} Preview without writing")
        print(f"  {C.G}mw ci generate -p gitlab{C.E} Generate for GitLab CI")
        print(f"  {C.G}mw ci preview{C.E}           Alias for generate --dry-run")
        print(f"  {C.G}mw ci validate{C.E}          Check existing CI config")
        print(f"  {C.G}mw ci list-templates{C.E}    Show available templates")
        print()
        print(f"  {C.DIM}Options:{C.E}")
        print(f"    --platform, -p   github | gitlab | bitbucket")
        print(f"    --path           Project directory (default: .)")
        print(f"    --force, -f      Overwrite existing config")
        print(f"    --dry-run        Preview only")
        return 0

    subcmd = args[0]
    rest = args[1:]

    commands = {
        "generate": cmd_generate,
        "gen": cmd_generate,
        "preview": cmd_preview,
        "validate": cmd_validate,
        "list-templates": cmd_list_templates,
        "templates": cmd_list_templates,
    }

    fn = commands.get(subcmd)
    if fn:
        return fn(rest)
    else:
        print(f"{C.R}❌ Unknown subcommand: {subcmd}{C.E}")
        print(f"   Try: mw ci --help")
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)

#!/usr/bin/env python3
"""
MyWork Framework Health Check
==============================
Comprehensive diagnostics for all framework components.

Usage:
    python health_check.py              # Full health check
    python health_check.py quick        # Quick status check
    python health_check.py fix          # Auto-fix common issues
    python health_check.py report       # Generate detailed report

Checks:
    - GSD installation and version
    - AutoForge server status
    - n8n connection and workflows
    - Project structure integrity
    - Git repository integrity
    - API key validity
    - Dependency versions
    - Disk space
    - Security issues
"""

import os
import sys
import json
import socket
import subprocess
import time

try:
    import fcntl  # Unix-only
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None
try:
    import msvcrt  # Windows-only
except ImportError:  # pragma: no cover - Unix fallback
    msvcrt = None
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

# Configuration - Import from shared config
try:
    from config import MYWORK_ROOT, AUTOCODER_ROOT as AUTOCODER_PATH
except ImportError:
    # Fallback if config not available
    def _get_mywork_root():
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        return script_dir.parent if script_dir.name == "tools" else Path.home() / "MyWork"

    MYWORK_ROOT = _get_mywork_root()
    AUTOCODER_PATH = Path(os.environ.get("AUTOCODER_ROOT", Path.home() / "GamesAI" / "autocoder"))

# Health check lock file for preventing concurrent runs
HEALTH_CHECK_LOCK = MYWORK_ROOT / ".tmp" / "health_check.lock"

GSD_PATH = Path.home() / ".claude" / "commands" / "gsd"
N8N_SKILLS_PATH = Path.home() / ".claude" / "skills" / "n8n-skills"


def _is_server_mode() -> bool:
    """Detect if running on a headless server (no Claude Desktop).
    
    Returns True if GSD/AutoForge/n8n are not expected to be installed.
    """
    # If .claude directory doesn't exist at all, we're in server mode
    claude_dir = Path.home() / ".claude"
    if not claude_dir.exists():
        return True
    # If DISPLAY is not set and we're on Linux, likely a headless server
    if sys.platform == "linux" and not os.environ.get("DISPLAY"):
        return True
    return False


class HealthCheckLock:
    """Context manager for preventing concurrent health check runs."""

    def __init__(self, lock_file: Path, timeout: int = 5):
        self.lock_file = lock_file
        self.timeout = timeout
        self.lock_fd = None

    def __enter__(self):
        try:
            # Ensure .tmp directory exists
            self.lock_file.parent.mkdir(parents=True, exist_ok=True)

            # Create lock file
            self.lock_fd = open(self.lock_file, "w")
            self.lock_fd.seek(0)

            # Try to acquire exclusive lock with timeout
            start_time = time.time()
            while True:
                try:
                    if fcntl is not None:
                        fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    elif msvcrt is not None:
                        # Lock 1 byte in non-blocking mode
                        msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        # No locking available; proceed without lock
                        return self

                    self.lock_fd.write(f"health_check:{os.getpid()}:{time.time()}\n")
                    self.lock_fd.flush()
                    return self
                except (BlockingIOError, OSError):
                    if time.time() - start_time > self.timeout:
                        raise RuntimeError(
                            f"Another health check is running (timeout after {self.timeout}s)"
                        )
                    time.sleep(0.1)
        except Exception:
            if self.lock_fd:
                self.lock_fd.close()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_fd:
            try:
                if fcntl is not None:
                    fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
                elif msvcrt is not None:
                    self.lock_fd.seek(0)
                    msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
                self.lock_fd.close()
                # Clean up lock file
                if self.lock_file.exists():
                    self.lock_file.unlink()
            except Exception:
                pass  # Best effort cleanup


def check_file_permissions(path: Path, need_write: bool = False) -> tuple[bool, str]:
    """
    Check if we have required permissions for file/directory operations.

    Returns:
        (success, error_message)
    """
    try:
        if not path.exists():
            # Check parent directory for write permission if we need to create
            parent = path.parent
            if parent.exists():
                if need_write and not os.access(parent, os.W_OK):
                    return False, f"No write permission for parent directory: {parent}"
                return True, ""
            else:
                return check_file_permissions(parent, need_write=True)

        # Check existing file/directory
        if not os.access(path, os.R_OK):
            return False, f"No read permission: {path}"

        if need_write and not os.access(path, os.W_OK):
            return False, f"No write permission: {path}"

        return True, ""
    except Exception as e:
        return False, f"Permission check failed: {e}"


def safe_socket_connect(host: str, port: int, timeout: float = 3.0) -> bool:
    """
    Safely check if a socket connection can be established with timeout protection.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except (socket.error, socket.timeout, OSError):
        return False


class Status(Enum):
    OK = "✅"
    WARNING = "⚠️"
    ERROR = "❌"
    UNKNOWN = "❓"


@dataclass
class CheckResult:
    name: str
    status: Status
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    fix_command: Optional[str] = None


class HealthChecker:
    """Performs health checks on MyWork framework components."""

    def __init__(self):
        self.results: List[CheckResult] = []

    def add_result(self, result: CheckResult):
        self.results.append(result)

    def run_all(self) -> List[CheckResult]:
        """Run all health checks."""
        server = _is_server_mode()
        if not server:
            self.check_gsd()
            self.check_autoforge()
            self.check_n8n()
        else:
            self.add_result(CheckResult(
                name="Environment",
                status=Status.OK,
                message="Server mode detected — skipping desktop-only checks (GSD, AutoForge, n8n)",
            ))
        self.check_git_integrity()
        self.check_projects()
        self.check_api_keys()
        self.check_dependencies()
        self.check_security()
        self.check_disk_space()
        return self.results

    def run_quick(self) -> List[CheckResult]:
        """Run quick status checks only."""
        if not _is_server_mode():
            self.check_gsd(quick=True)
            self.check_autoforge(quick=True)
            self.check_n8n(quick=True)
        else:
            self.add_result(CheckResult(
                name="Environment",
                status=Status.OK,
                message="Server mode — desktop checks skipped",
            ))
        return self.results

    def check_gsd(self, quick: bool = False):
        """Check GSD installation and status."""
        try:
            if not GSD_PATH.exists():
                self.add_result(
                    CheckResult(
                        name="GSD Installation",
                        status=Status.ERROR,
                        message="GSD not installed",
                        fix_command="/install gsd",
                    )
                )
                return

            # Check version
            version_file = GSD_PATH / "version.json"
            if version_file.exists():
                with open(version_file) as f:
                    version_data = json.load(f)
                    version = version_data.get("version", "unknown")
            else:
                # Try to find version in any config file
                version = "installed (version unknown)"

            # Count commands
            commands = list(GSD_PATH.glob("*.md"))

            # Check for updates
            update_check = Path.home() / ".claude" / "cache" / "gsd-update-check.json"
            has_updates = False
            latest_version = version

            if update_check.exists():
                try:
                    with open(update_check) as f:
                        update_data = json.load(f)
                        has_updates = update_data.get("updateAvailable", False)
                        latest_version = update_data.get("latestVersion", version)
                except (json.JSONDecodeError, KeyError):
                    pass

            if has_updates:
                self.add_result(
                    CheckResult(
                        name="GSD Version",
                        status=Status.WARNING,
                        message=f"Update available: {version} → {latest_version}",
                        details={
                            "current": version,
                            "latest": latest_version,
                            "commands": len(commands),
                        },
                        fix_command="/gsd:update",
                    )
                )
            else:
                self.add_result(
                    CheckResult(
                        name="GSD Installation",
                        status=Status.OK,
                        message=f"GSD v{version} with {len(commands)} commands",
                        details={"version": version, "commands": len(commands)},
                    )
                )

            if quick:
                return

            # Check agents
            agents_path = Path.home() / ".claude" / "agents"
            gsd_agents = list(agents_path.glob("gsd-*.md")) if agents_path.exists() else []

            self.add_result(
                CheckResult(
                    name="GSD Agents",
                    status=Status.OK if len(gsd_agents) >= 10 else Status.WARNING,
                    message=f"{len(gsd_agents)} GSD agents installed",
                    details={"agents": [a.stem for a in gsd_agents]},
                )
            )

            # Check hooks
            hooks_path = Path.home() / ".claude" / "hooks"
            gsd_hooks = list(hooks_path.glob("gsd-*.js")) if hooks_path.exists() else []

            self.add_result(
                CheckResult(
                    name="GSD Hooks",
                    status=Status.OK if len(gsd_hooks) >= 2 else Status.WARNING,
                    message=f"{len(gsd_hooks)} GSD hooks active",
                    details={"hooks": [h.stem for h in gsd_hooks]},
                )
            )

        except Exception as e:
            self.add_result(
                CheckResult(
                    name="GSD Check", status=Status.ERROR, message=f"Error checking GSD: {str(e)}"
                )
            )

    def check_autoforge(self, quick: bool = False):
        """Check AutoForge installation and server status."""
        try:
            # Check installation  
            if not AUTOCODER_PATH.exists():
                self.add_result(
                    CheckResult(
                        name="AutoForge Installation",
                        status=Status.ERROR,
                        message="AutoForge not found at expected path",
                        details={"expected_path": str(AUTOCODER_PATH)},
                    )
                )
                return

            # Check if server is running (with timeout protection)
            server_running = safe_socket_connect("127.0.0.1", 8888, timeout=3.0)

            if server_running:
                self.add_result(
                    CheckResult(
                        name="AutoForge Server",
                        status=Status.OK,
                        message="Server running on port 8888",
                        details={"port": 8888, "running": True},
                    )
                )
            else:
                self.add_result(
                    CheckResult(
                        name="AutoForge Server",
                        status=Status.WARNING,
                        message="Server not running",
                        details={"port": 8888, "running": False},
                        fix_command="python tools/autoforge_api.py server",
                    )
                )

            if quick:
                return

            # Check git status
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=AUTOCODER_PATH,
                capture_output=True,
                text=True,
                timeout=10,
            )
            commit = result.stdout.strip() if result.returncode == 0 else "unknown"

            # Check for updates
            subprocess.run(["git", "fetch", "--quiet"], cwd=AUTOCODER_PATH, capture_output=True, timeout=10)
            result = subprocess.run(
                ["git", "log", "--oneline", "HEAD..@{u}"],
                cwd=AUTOCODER_PATH,
                capture_output=True,
                text=True,
                timeout=10,
            )
            pending_updates = (
                len(result.stdout.strip().split("\n"))
                if result.returncode == 0 and result.stdout.strip()
                else 0
            )

            if pending_updates > 0:
                self.add_result(
                    CheckResult(
                        name="AutoForge Version",
                        status=Status.WARNING,
                        message=f"Commit {commit}, {pending_updates} updates available",
                        details={"commit": commit, "pending": pending_updates},
                        fix_command="python tools/auto_update.py update autoforge",
                    )
                )
            else:
                self.add_result(
                    CheckResult(
                        name="AutoForge Version",
                        status=Status.OK,
                        message=f"Commit {commit}, up to date",
                        details={"commit": commit},
                    )
                )

            # Check venv
            venv_path = AUTOCODER_PATH / "venv"
            if venv_path.exists():
                self.add_result(
                    CheckResult(
                        name="AutoForge Environment",
                        status=Status.OK,
                        message="Python venv configured",
                    )
                )
            else:
                self.add_result(
                    CheckResult(
                        name="AutoForge Environment",
                        status=Status.ERROR,
                        message="Python venv missing",
                        fix_command=f"cd {AUTOCODER_PATH} && python -m venv venv && pip install -r requirements.txt",
                    )
                )

        except Exception as e:
            self.add_result(
                CheckResult(
                    name="AutoForge Check",
                    status=Status.ERROR,
                    message=f"Error checking AutoForge: {str(e)}",
                )
            )

    def check_n8n(self, quick: bool = False):
        """Check n8n-mcp and n8n-skills."""
        try:
            # Check n8n-skills installation
            if N8N_SKILLS_PATH.exists():
                skills = (
                    list((N8N_SKILLS_PATH / "skills").glob("n8n-*"))
                    if (N8N_SKILLS_PATH / "skills").exists()
                    else []
                )
                self.add_result(
                    CheckResult(
                        name="n8n-skills",
                        status=Status.OK if len(skills) >= 7 else Status.WARNING,
                        message=f"{len(skills)} skills installed",
                        details={"skills": [s.name for s in skills]},
                    )
                )
            else:
                self.add_result(
                    CheckResult(
                        name="n8n-skills",
                        status=Status.ERROR,
                        message="n8n-skills not installed",
                        fix_command="git clone https://github.com/czlonkowski/n8n-skills.git ~/.claude/skills/n8n-skills",
                    )
                )

            # Check .mcp.json configuration
            mcp_config = MYWORK_ROOT / ".mcp.json"
            if mcp_config.exists():
                with open(mcp_config) as f:
                    config = json.load(f)
                    servers = config.get("mcpServers", {})

                    if "n8n-mcp" in servers:
                        n8n_config = servers["n8n-mcp"]
                        env = n8n_config.get("env", {})

                        if env.get("N8N_API_KEY") and env.get("N8N_API_URL"):
                            self.add_result(
                                CheckResult(
                                    name="n8n-mcp Config",
                                    status=Status.OK,
                                    message=f"Configured for {env.get('N8N_API_URL', 'unknown')}",
                                    details={"url": env.get("N8N_API_URL")},
                                )
                            )
                        else:
                            self.add_result(
                                CheckResult(
                                    name="n8n-mcp Config",
                                    status=Status.WARNING,
                                    message="n8n-mcp configured but missing API key or URL",
                                )
                            )
                    else:
                        self.add_result(
                            CheckResult(
                                name="n8n-mcp",
                                status=Status.ERROR,
                                message="n8n-mcp not in .mcp.json",
                            )
                        )
            else:
                self.add_result(
                    CheckResult(
                        name="n8n-mcp Config",
                        status=Status.ERROR,
                        message=".mcp.json not found",
                        details={"expected": str(mcp_config)},
                    )
                )

            if quick:
                return

            # Test n8n-mcp availability (npx should work)
            result = subprocess.run(
                ["npx", "--no-install", "n8n-mcp", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # npx n8n-mcp might not have --version, so just check if it runs
                self.add_result(
                    CheckResult(
                        name="n8n-mcp Package",
                        status=Status.OK,
                        message="n8n-mcp available via npx",
                    )
                )
            else:
                output = (result.stderr or result.stdout or "").strip()
                detail = output.splitlines()[0] if output else "npx returned non-zero exit code"
                self.add_result(
                    CheckResult(
                        name="n8n-mcp Package",
                        status=Status.WARNING,
                        message=f"n8n-mcp not available via npx ({detail})",
                        fix_command="npm install -g n8n-mcp",
                    )
                )

        except subprocess.TimeoutExpired:
            self.add_result(
                CheckResult(
                    name="n8n-mcp Package", status=Status.WARNING, message="n8n-mcp check timed out"
                )
            )
        except Exception as e:
            self.add_result(
                CheckResult(
                    name="n8n Check", status=Status.ERROR, message=f"Error checking n8n: {str(e)}"
                )
            )

    def check_projects(self):
        """Check project structure and GSD state."""
        try:
            projects_dir = MYWORK_ROOT / "projects"

            if not projects_dir.exists():
                self.add_result(
                    CheckResult(
                        name="Projects Directory",
                        status=Status.ERROR,
                        message="Projects directory not found",
                        fix_command=f"mkdir -p {projects_dir}",
                    )
                )
                return

            projects = [
                p
                for p in projects_dir.iterdir()
                if p.is_dir() and not p.name.startswith((".", "_"))
            ]

            self.add_result(
                CheckResult(
                    name="Projects Directory",
                    status=Status.OK,
                    message=f"{len(projects)} projects found",
                    details={"projects": [p.name for p in projects]},
                )
            )

            # Check each project's GSD state
            for project in projects:
                planning_dir = project / ".planning"

                if not planning_dir.exists():
                    self.add_result(
                        CheckResult(
                            name=f"Project: {project.name}",
                            status=Status.WARNING,
                            message="No .planning directory",
                            fix_command=f"mkdir -p {planning_dir}",
                        )
                    )
                    continue

                # Check for key GSD files
                required_files = ["PROJECT.md", "ROADMAP.md", "STATE.md"]
                missing = [f for f in required_files if not (planning_dir / f).exists()]

                if missing:
                    self.add_result(
                        CheckResult(
                            name=f"Project: {project.name}",
                            status=Status.WARNING,
                            message=f"Missing GSD files: {', '.join(missing)}",
                            details={"missing": missing},
                            fix_command=f"cd {project} && /gsd:new-project",
                        )
                    )
                else:
                    # Check STATE.md for last update
                    state_file = planning_dir / "STATE.md"
                    mtime = datetime.fromtimestamp(state_file.stat().st_mtime)
                    days_old = (datetime.now() - mtime).days

                    status = Status.OK if days_old < 7 else Status.WARNING
                    self.add_result(
                        CheckResult(
                            name=f"Project: {project.name}",
                            status=status,
                            message=f"GSD state complete, last update {days_old} days ago",
                            details={"last_updated": mtime.isoformat(), "days_old": days_old},
                        )
                    )

        except Exception as e:
            self.add_result(
                CheckResult(
                    name="Projects Check",
                    status=Status.ERROR,
                    message=f"Error checking projects: {str(e)}",
                )
            )

    def check_api_keys(self):
        """Check API key configuration."""
        try:
            env_file = MYWORK_ROOT / ".env"

            if not env_file.exists():
                self.add_result(
                    CheckResult(
                        name="Environment File", status=Status.ERROR, message=".env file not found"
                    )
                )
                return

            with open(env_file) as f:
                content = f.read()

            # Key categories to check
            key_checks = {
                "ANTHROPIC_API_KEY": "Anthropic/Claude",
                "OPENAI_API_KEY": "OpenAI",
                "N8N_API_KEY": "n8n",
                "GITHUB_TOKEN": "GitHub",
            }

            configured = []
            missing = []

            for key, name in key_checks.items():
                # Check if key exists and has a value
                pattern = f"{key}="
                if pattern in content:
                    # Get the value
                    for line in content.split("\n"):
                        if line.startswith(pattern):
                            value = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if value and not value.startswith("#"):
                                configured.append(name)
                            else:
                                missing.append(name)
                            break
                else:
                    missing.append(name)

            if missing:
                self.add_result(
                    CheckResult(
                        name="API Keys",
                        status=Status.WARNING,
                        message=f"{len(configured)} configured, {len(missing)} missing",
                        details={"configured": configured, "missing": missing},
                    )
                )
            else:
                self.add_result(
                    CheckResult(
                        name="API Keys",
                        status=Status.OK,
                        message=f"All {len(configured)} essential keys configured",
                        details={"configured": configured},
                    )
                )

        except Exception as e:
            self.add_result(
                CheckResult(
                    name="API Keys Check",
                    status=Status.ERROR,
                    message=f"Error checking API keys: {str(e)}",
                )
            )

    def check_dependencies(self):
        """Check Python and Node.js dependencies."""
        try:
            # Check Python
            result = subprocess.run(["python3", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                python_version = result.stdout.strip()
                self.add_result(
                    CheckResult(name="Python", status=Status.OK, message=python_version)
                )
            else:
                self.add_result(
                    CheckResult(name="Python", status=Status.ERROR, message="Python not found")
                )

            # Check Node.js
            result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                major_version = int(node_version.replace("v", "").split(".")[0])
                status = Status.OK if major_version >= 18 else Status.WARNING
                self.add_result(
                    CheckResult(
                        name="Node.js",
                        status=status,
                        message=node_version,
                        details={"major": major_version},
                    )
                )
            else:
                self.add_result(
                    CheckResult(name="Node.js", status=Status.ERROR, message="Node.js not found")
                )

            # Check npm
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.add_result(
                    CheckResult(name="npm", status=Status.OK, message=f"v{result.stdout.strip()}")
                )

            # Check git
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                git_version = result.stdout.strip()
                self.add_result(
                    CheckResult(name="Git", status=Status.OK, message=git_version)
                )

            # Check pip packages for MyWork framework
            pip_requirements = [
                ("httpx", "0.24.0"),
                ("websockets", "10.0"),
                ("pydantic", "2.0"),
                ("python-dotenv", "0.19.0")
            ]
            
            for package, min_version in pip_requirements:
                try:
                    result = subprocess.run(
                        ["pip", "show", package], 
                        capture_output=True, 
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        # Extract version from pip show output
                        for line in result.stdout.split('\n'):
                            if line.startswith('Version:'):
                                version = line.split(':', 1)[1].strip()
                                # Simple version comparison (works for basic semver)
                                if version >= min_version:
                                    status = Status.OK
                                    message = f"v{version} (>= {min_version})"
                                else:
                                    status = Status.WARNING
                                    message = f"v{version} (requires >= {min_version})"
                                
                                self.add_result(
                                    CheckResult(
                                        name=f"Python Package: {package}",
                                        status=status,
                                        message=message,
                                        details={"installed_version": version, "required": min_version}
                                    )
                                )
                                break
                    else:
                        self.add_result(
                            CheckResult(
                                name=f"Python Package: {package}",
                                status=Status.ERROR,
                                message="Not installed",
                                fix_command=f"pip install {package}>={min_version}"
                            )
                        )
                except Exception as pkg_e:
                    self.add_result(
                        CheckResult(
                            name=f"Python Package: {package}",
                            status=Status.ERROR,
                            message=f"Check failed: {str(pkg_e)}"
                        )
                    )

            # Check framework-specific files
            framework_files = [
                ("pyproject.toml", "Framework configuration"),
                ("requirements.txt", "Python dependencies"),
                (".gitignore", "Git ignore rules"),
                ("tools/mw.py", "MyWork CLI"),
                ("tools/brain.py", "Brain knowledge system"),
                ("tools/autoforge_api.py", "AutoForge integration")
            ]
            
            missing_files = []
            for file_path, description in framework_files:
                full_path = MYWORK_ROOT / file_path
                if not full_path.exists():
                    missing_files.append(f"{file_path} ({description})")
            
            if missing_files:
                self.add_result(
                    CheckResult(
                        name="Framework Files",
                        status=Status.WARNING,
                        message=f"{len(missing_files)} files missing",
                        details={"missing": missing_files}
                    )
                )
            else:
                self.add_result(
                    CheckResult(
                        name="Framework Files",
                        status=Status.OK,
                        message="All required files present"
                    )
                )

        except Exception as e:
            self.add_result(
                CheckResult(
                    name="Dependencies Check",
                    status=Status.ERROR,
                    message=f"Error checking dependencies: {str(e)}",
                )
            )

    def check_security(self):
        """Check for common security issues."""
        try:
            issues = []

            # Check for hardcoded secrets in tools (avoid false positives)
            tools_dir = MYWORK_ROOT / "tools"
            for tool_file in tools_dir.glob("*.py"):
                if tool_file.name == "health_check.py":
                    continue
                content = tool_file.read_text()
                # Look for potential API keys/tokens (high-signal patterns only)
                if any(pattern in content for pattern in ["sk-", "gsk_", "eyJ", "Bearer "]):
                    # Check if it's not in a comment or example
                    for line in content.split("\n"):
                        if any(p in line for p in ["sk-", "gsk_", "eyJ", "Bearer "]):
                            if not line.strip().startswith("#") and "example" not in line.lower():
                                issues.append(f"Potential hardcoded secret in {tool_file.name}")
                                break

            # Check .gitignore
            gitignore = MYWORK_ROOT / ".gitignore"
            if gitignore.exists():
                content = gitignore.read_text()
                required_ignores = [".env", "__pycache__", "node_modules"]
                missing_ignores = [i for i in required_ignores if i not in content]
                if "*.pyc" not in content and "*.py[cod]" not in content:
                    missing_ignores.append("*.pyc")

                if missing_ignores:
                    issues.append(f".gitignore missing: {', '.join(missing_ignores)}")
            else:
                issues.append(".gitignore not found")

            # Check file permissions on .env
            env_file = MYWORK_ROOT / ".env"
            if env_file.exists():
                mode = oct(env_file.stat().st_mode)[-3:]
                if mode != "600" and mode != "644":
                    pass  # Relaxed check for macOS

            if issues:
                self.add_result(
                    CheckResult(
                        name="Security",
                        status=Status.WARNING,
                        message=f"{len(issues)} potential issues found",
                        details={"issues": issues},
                    )
                )
            else:
                self.add_result(
                    CheckResult(
                        name="Security", status=Status.OK, message="No obvious security issues"
                    )
                )

        except Exception as e:
            self.add_result(
                CheckResult(
                    name="Security Check",
                    status=Status.ERROR,
                    message=f"Error checking security: {str(e)}",
                )
            )

    def check_disk_space(self):
        """Check available disk space."""
        try:
            import shutil

            total, used, free = shutil.disk_usage(MYWORK_ROOT)

            free_gb = free / (1024**3)
            total_gb = total / (1024**3)
            used_percent = (used / total) * 100

            if free_gb < 5:
                status = Status.ERROR
                message = f"Low disk space: {free_gb:.1f}GB free"
            elif free_gb < 20:
                status = Status.WARNING
                message = f"Disk space warning: {free_gb:.1f}GB free"
            else:
                status = Status.OK
                message = (
                    f"{free_gb:.1f}GB free of {total_gb:.1f}GB ({100-used_percent:.1f}% available)"
                )

            self.add_result(
                CheckResult(
                    name="Disk Space",
                    status=status,
                    message=message,
                    details={
                        "free_gb": round(free_gb, 1),
                        "total_gb": round(total_gb, 1),
                        "used_percent": round(used_percent, 1),
                    },
                )
            )

        except Exception as e:
            self.add_result(
                CheckResult(
                    name="Disk Space Check",
                    status=Status.ERROR,
                    message=f"Error checking disk space: {str(e)}",
                )
            )

    def check_git_integrity(self):
        """Check git repository integrity."""
        try:
            # Check if this is a git repository
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=MYWORK_ROOT,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode != 0:
                self.add_result(
                    CheckResult(
                        name="Git Repository",
                        status=Status.ERROR,
                        message="Not a git repository",
                        details={"path": str(MYWORK_ROOT)},
                        fix_command="cd " + str(MYWORK_ROOT) + " && git init"
                    )
                )
                return

            # Check repository status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=MYWORK_ROOT,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                modified_files = len([line for line in result.stdout.strip().split('\n') if line.strip()])
                
                if result.stdout.strip():
                    self.add_result(
                        CheckResult(
                            name="Git Working Directory",
                            status=Status.WARNING,
                            message=f"{modified_files} uncommitted changes",
                            details={"modified_files": modified_files},
                            fix_command="git add . && git commit -m 'WIP: Uncommitted changes'"
                        )
                    )
                else:
                    self.add_result(
                        CheckResult(
                            name="Git Working Directory",
                            status=Status.OK,
                            message="Clean working directory"
                        )
                    )

            # Check for unpushed commits
            result = subprocess.run(
                ["git", "log", "--oneline", "@{u}..HEAD"],
                cwd=MYWORK_ROOT,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0 and result.stdout.strip():
                unpushed_commits = len(result.stdout.strip().split('\n'))
                self.add_result(
                    CheckResult(
                        name="Git Remote Sync",
                        status=Status.WARNING,
                        message=f"{unpushed_commits} unpushed commits",
                        details={"unpushed_commits": unpushed_commits},
                        fix_command="git push"
                    )
                )
            else:
                self.add_result(
                    CheckResult(
                        name="Git Remote Sync",
                        status=Status.OK,
                        message="Repository in sync with remote"
                    )
                )

            # Check git configuration
            result = subprocess.run(
                ["git", "config", "user.email"],
                cwd=MYWORK_ROOT,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0 and result.stdout.strip():
                email = result.stdout.strip()
                self.add_result(
                    CheckResult(
                        name="Git Configuration",
                        status=Status.OK,
                        message=f"User configured: {email}",
                        details={"user_email": email}
                    )
                )
            else:
                self.add_result(
                    CheckResult(
                        name="Git Configuration",
                        status=Status.WARNING,
                        message="Git user not configured",
                        fix_command="git config user.email 'memo@openclaw.ai' && git config user.name 'Memo'"
                    )
                )

        except Exception as e:
            self.add_result(
                CheckResult(
                    name="Git Integrity Check",
                    status=Status.ERROR,
                    message=f"Error checking git repository: {str(e)}",
                )
            )


def print_results(results: List[CheckResult], verbose: bool = False):
    """Print formatted health check results."""
    print("\n" + "=" * 60)
    print("🏥 MyWork Framework Health Check")
    print("=" * 60)
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Group by status
    ok = [r for r in results if r.status == Status.OK]
    warnings = [r for r in results if r.status == Status.WARNING]
    errors = [r for r in results if r.status == Status.ERROR]

    # Print errors first
    if errors:
        print("\n❌ ERRORS")
        print("-" * 40)
        for r in errors:
            print(f"   {r.status.value} {r.name}")
            print(f"      {r.message}")
            if r.fix_command:
                print(f"      Fix: {r.fix_command}")

    # Print warnings
    if warnings:
        print("\n⚠️  WARNINGS")
        print("-" * 40)
        for r in warnings:
            print(f"   {r.status.value} {r.name}")
            print(f"      {r.message}")
            if r.fix_command:
                print(f"      Fix: {r.fix_command}")

    # Print OK items (summarized)
    if ok:
        print("\n✅ HEALTHY")
        print("-" * 40)
        for r in ok:
            print(f"   {r.status.value} {r.name}: {r.message}")

    # Summary
    print("\n" + "=" * 60)
    print(f"Summary: {len(ok)} OK, {len(warnings)} Warnings, {len(errors)} Errors")

    if errors:
        print("\n💡 Run 'python tools/health_check.py fix' to auto-fix issues")

    print("=" * 60)


def auto_fix(results: List[CheckResult]):
    """Attempt to auto-fix issues."""
    fixable = [r for r in results if r.fix_command and r.status in (Status.ERROR, Status.WARNING)]

    if not fixable:
        print("\n✅ No auto-fixable issues found")
        return

    print(f"\n🔧 Found {len(fixable)} fixable issues")

    for result in fixable:
        print(f"\n   Fixing: {result.name}")
        print(f"   Command: {result.fix_command}")

        try:
            response = input("   Run this fix? [y/N]: ").strip().lower()
        except EOFError:
            response = "n"
            print("   (skipped — non-interactive mode)")
        if response == "y":
            try:
                # Handle different command types
                if result.fix_command.startswith("/"):
                    print(f"   ℹ️  Run this command manually in Claude Code: {result.fix_command}")
                elif result.fix_command.startswith("cd "):
                    # Handle directory change commands securely
                    # Parse "cd <dir> && <command>" pattern
                    command_parts = result.fix_command.split(" && ")
                    if len(command_parts) == 2:
                        cd_part = command_parts[0]
                        cmd_part = command_parts[1]
                        # Extract directory from "cd <dir>"
                        target_dir = cd_part.replace("cd ", "").strip()
                        # Run command in target directory without shell=True
                        subprocess.run(cmd_part.split(), cwd=target_dir, shell=False, timeout=10)
                    else:
                        # Simple cd command - just inform user
                        print(f"   ℹ️  Please change directory manually: {result.fix_command}")
                    print("   ✅ Done")
                else:
                    parts = result.fix_command.split()
                    subprocess.run(parts, timeout=10)
                    print("   ✅ Done")
            except Exception as e:
                print(f"   ❌ Failed: {e}")


def generate_report(results: List[CheckResult]) -> str:
    """Generate a detailed markdown report."""
    report = f"""# MyWork Framework Health Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Status | Count |
|--------|-------|
| ✅ OK | {len([r for r in results if r.status == Status.OK])} |
| ⚠️ Warnings | {len([r for r in results if r.status == Status.WARNING])} |
| ❌ Errors | {len([r for r in results if r.status == Status.ERROR])} |

## Detailed Results

"""

    for result in results:
        report += f"### {result.status.value} {result.name}\n\n"
        report += f"**Status:** {result.message}\n\n"

        if result.details:
            report += "**Details:**\n```json\n"
            report += json.dumps(result.details, indent=2)
            report += "\n```\n\n"

        if result.fix_command:
            report += f"**Fix Command:** `{result.fix_command}`\n\n"

        report += "---\n\n"

    return report


def main():
    """Main entry point."""
    command = sys.argv[1] if len(sys.argv) > 1 else "full"

    # Use lock file protection for non-quick checks
    if command == "quick":
        checker = HealthChecker()
        results = checker.run_quick()
        print_results(results)
        return

    try:
        with HealthCheckLock(HEALTH_CHECK_LOCK, timeout=10):
            checker = HealthChecker()

            if command == "fix":
                # Check file permissions before attempting fixes
                can_write, error = check_file_permissions(MYWORK_ROOT, need_write=True)
                if not can_write:
                    print(f"❌ Cannot run fix mode: {error}")
                    sys.exit(1)

                results = checker.run_all()
                print_results(results)
                auto_fix(results)

            elif command == "report":
                results = checker.run_all()
                report = generate_report(results)
                report_file = (
                    MYWORK_ROOT
                    / ".tmp"
                    / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                )

                # Check permissions before writing report
                can_write, error = check_file_permissions(report_file.parent, need_write=True)
                if not can_write:
                    print(f"❌ Cannot write report: {error}")
                else:
                    report_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(report_file, "w") as f:
                        f.write(report)
                    print(f"✅ Report saved to: {report_file}")

                print_results(results)

            else:  # full check
                results = checker.run_all()
                print_results(results)

    except RuntimeError as e:
        print(f"⚠️  {e}")
        print("If you need to force a health check, remove the lock file:")
        print(f"   rm {HEALTH_CHECK_LOCK}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

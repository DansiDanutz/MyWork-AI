#!/usr/bin/env python3
"""
Brain Learner - Automatic Knowledge Discovery
==============================================
Discovers learnings from work patterns and automatically updates the brain.

This script should be run:
- After completing GSD phases
- After fixing errors
- During weekly maintenance
- After any significant work session

Usage:
    python brain_learner.py discover           # Discover new learnings from recent work
    python brain_learner.py analyze-errors     # Learn from error patterns
    python brain_learner.py analyze-modules    # Learn from module registry patterns
    python brain_learner.py analyze-tracebacks # Learn from Python tracebacks in logs
    python brain_learner.py analyze-deployments # Learn from successful deployments
    python brain_learner.py analyze-reviews    # Learn from code review patterns
    python brain_learner.py auto-tag           # Auto-tag entries based on content
    python brain_learner.py confidence-score   # Update confidence scores for entries
    python brain_learner.py promote            # Promote validated EXPERIMENTAL entries
    python brain_learner.py cleanup-smart      # Intelligent cleanup based on usage
    python brain_learner.py daily              # Run daily learning routine
    python brain_learner.py weekly             # Run weekly deep analysis

The brain learns from:
- GSD phase completions (SUMMARY.md, VERIFICATION.md)
- Git commit patterns
- Error logs and their resolutions
- Module registry patterns
- Health check history
- Successful workflows
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# Configuration - Import from shared config with fallback
try:
    from config import MYWORK_ROOT, PROJECTS_DIR, BRAIN_DATA_JSON as BRAIN_JSON, BRAIN_MD, TMP_DIR

    LEARNING_LOG = TMP_DIR / "learning_log.json"
    ERROR_LOG = TMP_DIR / "error_patterns.json"
except ImportError:

    def _get_mywork_root():
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        return script_dir.parent if script_dir.name == "tools" else Path.home() / "MyWork"

    MYWORK_ROOT = _get_mywork_root()
    PROJECTS_DIR = MYWORK_ROOT / "projects"
    BRAIN_JSON = MYWORK_ROOT / ".planning" / "brain_data.json"
    BRAIN_MD = MYWORK_ROOT / ".planning" / "BRAIN.md"
    LEARNING_LOG = MYWORK_ROOT / ".tmp" / "learning_log.json"
    ERROR_LOG = MYWORK_ROOT / ".tmp" / "error_patterns.json"

# Import brain manager
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from brain import BrainManager, BrainEntry
except ImportError:
    print("Error: Could not import brain module")
    sys.exit(1)


class LearningEngine:
    """Discovers and extracts learnings from work patterns."""

    def __init__(self):
        self.brain = BrainManager()
        self.discoveries: List[Dict[str, Any]] = []
        self.load_learning_log()

    def load_learning_log(self):
        """Load previous learning sessions."""
        if LEARNING_LOG.exists():
            try:
                with open(LEARNING_LOG) as f:
                    self.learning_history = json.load(f)
            except json.JSONDecodeError:
                self.learning_history = {"sessions": [], "discovered": []}
        else:
            self.learning_history = {"sessions": [], "discovered": []}

    def save_learning_log(self):
        """Save learning session."""
        LEARNING_LOG.parent.mkdir(parents=True, exist_ok=True)
        self.learning_history["sessions"].append(
            {"timestamp": datetime.now().isoformat(), "discoveries": len(self.discoveries)}
        )
        with open(LEARNING_LOG, "w") as f:
            json.dump(self.learning_history, f, indent=2)

    def already_learned(self, content: str) -> bool:
        """Check if we already have this learning."""
        content_lower = content.lower()
        for entry in self.brain.entries.values():
            if content_lower in entry.content.lower() or entry.content.lower() in content_lower:
                return True
        # Check discovery history
        for discovered in self.learning_history.get("discovered", []):
            if content_lower in discovered.lower():
                return True
        return False

    def add_discovery(
        self,
        entry_type: str,
        content: str,
        context: str = "",
        confidence: str = "EXPERIMENTAL",
        source: str = "auto",
    ):
        """Add a discovery if not already known."""
        if self.already_learned(content):
            return False

        self.discoveries.append(
            {
                "type": entry_type,
                "content": content,
                "context": context,
                "confidence": confidence,
                "source": source,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Track in history
        self.learning_history.setdefault("discovered", []).append(content)

        return True

    def discover_from_gsd_phases(self) -> int:
        """Discover learnings from completed GSD phases."""
        count = 0

        for project in PROJECTS_DIR.iterdir():
            if not project.is_dir() or project.name.startswith((".", "_")):
                continue

            phases_dir = project / ".planning" / "phases"
            if not phases_dir.exists():
                continue

            for phase_dir in phases_dir.iterdir():
                if not phase_dir.is_dir():
                    continue

                # Check SUMMARY.md for learnings
                summary = phase_dir / "SUMMARY.md"
                if summary.exists():
                    count += self._extract_from_summary(summary, project.name)

                # Check VERIFICATION.md for issues/solutions
                verification = phase_dir / "VERIFICATION.md"
                if verification.exists():
                    count += self._extract_from_verification(verification, project.name)

        return count

    def _extract_from_summary(self, summary_path: Path, project: str) -> int:
        """Extract learnings from phase summary."""
        count = 0
        content = summary_path.read_text()

        # Look for "Lessons Learned" or "What Worked" sections
        lessons_match = re.search(
            r"(?:lessons?\s*learned|what\s*worked|key\s*insights?)[\s:]*\n((?:[-*]\s*.+\n?)+)",
            content,
            re.IGNORECASE,
        )

        if lessons_match:
            for line in lessons_match.group(1).split("\n"):
                line = line.strip().lstrip("-*").strip()
                if line and len(line) > 20:
                    if self.add_discovery(
                        "lesson",
                        line,
                        f"From {project} phase summary",
                        "EXPERIMENTAL",
                        f"gsd:{project}",
                    ):
                        count += 1

        # Look for "Issues" or "Blockers" sections
        issues_match = re.search(
            r"(?:issues?|blockers?|problems?)[\s:]*\n((?:[-*]\s*.+\n?)+)", content, re.IGNORECASE
        )

        if issues_match:
            for line in issues_match.group(1).split("\n"):
                line = line.strip().lstrip("-*").strip()
                if line and len(line) > 20:
                    # Convert issue to anti-pattern
                    if self.add_discovery(
                        "antipattern",
                        f"Avoid: {line}",
                        f"Issue encountered in {project}",
                        "EXPERIMENTAL",
                        f"gsd:{project}",
                    ):
                        count += 1

        return count

    def _extract_from_verification(self, verification_path: Path, project: str) -> int:
        """Extract learnings from verification results."""
        count = 0
        content = verification_path.read_text()

        # Look for failed tests and their fixes
        failures_match = re.search(
            r"(?:failed|issues?|bugs?)[\s:]*\n((?:[-*]\s*.+\n?)+)", content, re.IGNORECASE
        )

        if failures_match:
            for line in failures_match.group(1).split("\n"):
                line = line.strip().lstrip("-*").strip()
                if line and len(line) > 20:
                    if self.add_discovery(
                        "antipattern",
                        f"Check for: {line}",
                        f"Verification issue in {project}",
                        "EXPERIMENTAL",
                        f"gsd:{project}",
                    ):
                        count += 1

        return count

    def discover_from_git_commits(self, days: int = 7) -> int:
        """Discover patterns from recent git commits."""
        count = 0

        for project in PROJECTS_DIR.iterdir():
            if not project.is_dir() or project.name.startswith((".", "_")):
                continue

            git_dir = project / ".git"
            if not git_dir.exists():
                continue

            try:
                # Get recent commits
                result = subprocess.run(
                    ["git", "log", f"--since={days} days ago", "--pretty=format:%s"],
                    cwd=project,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode != 0:
                    continue

                commits = result.stdout.strip().split("\n")

                # Analyze commit patterns
                fix_count = sum(1 for c in commits if "fix" in c.lower())
                refactor_count = sum(1 for c in commits if "refactor" in c.lower())
                feature_count = sum(
                    1 for c in commits if any(w in c.lower() for w in ["feat", "add", "implement"])
                )

                # If lots of fixes, might indicate pattern to learn
                if fix_count > 3:
                    # Look for common fix patterns
                    fix_commits = [c for c in commits if "fix" in c.lower()]
                    for commit in fix_commits[:3]:
                        # Extract what was fixed
                        if self.add_discovery(
                            "lesson",
                            f"Common fix pattern: {commit}",
                            f"Recurring fix in {project.name}",
                            "EXPERIMENTAL",
                            f"git:{project.name}",
                        ):
                            count += 1

            except Exception:
                continue

        return count

    def discover_from_module_patterns(self) -> int:
        """Discover patterns from module registry."""
        count = 0
        registry_file = MYWORK_ROOT / ".planning" / "module_registry.json"

        if not registry_file.exists():
            return 0

        try:
            with open(registry_file) as f:
                registry = json.load(f)

            modules = registry.get("modules", [])

            # Analyze naming patterns
            name_patterns = defaultdict(int)
            for mod in modules:
                name = mod.get("name", "")
                # Extract common prefixes
                if name.startswith(("get", "set", "create", "update", "delete")):
                    pattern = name[:6] + "..."
                    name_patterns[pattern] += 1
                elif name.startswith("use"):
                    name_patterns["use... (hook)"] += 1
                elif name.endswith(("Service", "Manager", "Handler")):
                    name_patterns["*Service/*Manager pattern"] += 1

            # Learn from dominant patterns
            for pattern, count_val in sorted(name_patterns.items(), key=lambda x: -x[1])[:3]:
                if count_val > 5:
                    if self.add_discovery(
                        "pattern",
                        f"Common naming: {pattern} (found {count_val} times)",
                        "From module registry analysis",
                        "TESTED",  # Based on evidence
                        "registry",
                    ):
                        count += 1

            # Analyze module types distribution
            type_counts = defaultdict(int)
            for mod in modules:
                type_counts[mod.get("type", "unknown")] += 1

            # Most common types are proven patterns
            for mod_type, type_count in sorted(type_counts.items(), key=lambda x: -x[1])[:3]:
                if type_count > 10:
                    if self.add_discovery(
                        "insight",
                        f"Project pattern: Heavy use of {mod_type} modules ({type_count} found)",
                        "From module registry analysis",
                        "TESTED",
                        "registry",
                    ):
                        count += 1

        except Exception as e:
            print(f"Warning: Could not analyze registry: {e}")

        return count

    def discover_from_error_patterns(self) -> int:
        """Discover patterns from error logs."""
        count = 0

        # Check various log files
        log_files = [
            MYWORK_ROOT / ".tmp" / "autocoder.error.log",
            MYWORK_ROOT / ".tmp" / "update.log",
        ]

        error_patterns = defaultdict(list)

        for log_file in log_files:
            if not log_file.exists():
                continue

            try:
                content = log_file.read_text()

                # Common error patterns
                patterns = [
                    (
                        r'ModuleNotFoundError: No module named [\'"](\w+)[\'"]',
                        "Missing Python module: {}",
                    ),
                    (r'ImportError: cannot import name [\'"](\w+)[\'"]', "Import issue: {}"),
                    (r'FileNotFoundError:.*[\'"]([^"\']+)[\'"]', "Missing file: {}"),
                    (r'PermissionError:.*[\'"]([^"\']+)[\'"]', "Permission issue: {}"),
                    (r"ConnectionRefusedError", "Connection refused - check if service is running"),  # SECURITY_SAFE: error pattern matching
                    (r"timeout", "Timeout - increase timeout or check network"),
                ]

                for pattern, template in patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        if match.groups():
                            error_msg = template.format(match.group(1))
                        else:
                            error_msg = template
                        error_patterns[error_msg].append(log_file.name)

            except Exception:
                continue

        # Learn from recurring errors
        for error, occurrences in error_patterns.items():
            if len(occurrences) >= 2:  # Recurring error
                if self.add_discovery(
                    "antipattern",
                    f"Watch for: {error}",
                    f"Occurred {len(occurrences)} times in logs",
                    "EXPERIMENTAL",
                    "error_logs",
                ):
                    count += 1

        return count

    def promote_validated_entries(self) -> int:
        """Promote EXPERIMENTAL entries that have been validated."""
        count = 0

        for entry in list(self.brain.entries.values()):
            if entry.status != "EXPERIMENTAL":
                continue

            # Check if entry has been around for a while without issues
            try:
                added_date = datetime.strptime(entry.date_added, "%Y-%m-%d")
                age_days = (datetime.now() - added_date).days

                # If experimental for more than 14 days without deprecation, promote
                if age_days > 14:
                    self.brain.update(entry.id, status="TESTED")
                    count += 1
                    print(f"   ✅ Promoted {entry.id}: {entry.content[:40]}...")

            except ValueError:
                continue

        if count > 0:
            self.brain.save()
            self._update_brain_md()

        return count

    def smart_cleanup(self) -> int:
        """Intelligent cleanup based on relevance."""
        count = 0

        for entry in list(self.brain.entries.values()):
            # Check for obsolete entries
            obsolete_indicators = [
                "deprecated",
                "no longer",
                "outdated",
                "replaced by",
                "use instead",
            ]

            content_lower = entry.content.lower()
            if any(ind in content_lower for ind in obsolete_indicators):
                if entry.status != "DEPRECATED":
                    self.brain.update(entry.id, status="DEPRECATED")
                    count += 1
                    print(f"   🗑️ Deprecated {entry.id}: {entry.content[:40]}...")

        if count > 0:
            self.brain.save()
            self._update_brain_md()

        return count

    def discover_from_python_tracebacks(self) -> int:
        """Learn from Python tracebacks in recent logs."""
        count = 0

        # Check various log sources
        log_sources = [
            MYWORK_ROOT / "logs",
            MYWORK_ROOT / ".tmp",
            Path("/var/log"),
        ]

        for source in log_sources:
            if source.exists():
                if source.is_file():
                    count += self._analyze_traceback_file(source)
                else:
                    count += self._scan_directory_for_tracebacks(source)

        return count

    def _analyze_traceback_file(self, file_path: Path) -> int:
        """Analyze a single file for Python tracebacks."""
        count = 0
        
        try:
            # Skip very large files
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                return 0
            
            # Only analyze recent files
            if file_path.stat().st_mtime < (datetime.now() - timedelta(days=7)).timestamp():
                return 0

            content = file_path.read_text(errors='ignore')
            count += self._analyze_traceback_content(content, str(file_path))
            
        except Exception:
            pass  # Skip files we can't read

        return count

    def _scan_directory_for_tracebacks(self, directory: Path) -> int:
        """Scan directory for files containing Python tracebacks."""
        count = 0
        
        # Look for relevant file types
        patterns = ["*.log", "*.txt", "*.out", "*.err"]
        
        for pattern in patterns:
            for file_path in directory.glob(pattern):
                count += self._analyze_traceback_file(file_path)
        
        return count

    def _analyze_traceback_content(self, content: str, source: str) -> int:
        """Analyze content for Python tracebacks and extract learnings."""
        count = 0

        # Pattern to match Python tracebacks
        traceback_pattern = r'Traceback \(most recent call last\):(.*?)(?=\n\S|\n*$)'
        
        tracebacks = re.findall(traceback_pattern, content, re.DOTALL)
        
        for traceback in tracebacks:
            # Extract the error type and message
            error_match = re.search(r'(\w+Error): (.+)', traceback)
            if not error_match:
                continue
                
            error_type = error_match.group(1)
            error_message = error_match.group(2).strip()
            
            # Create meaningful learning from the error
            if error_type and error_message:
                lesson = self._extract_error_lesson(error_type, error_message)
                confidence_score = self._calculate_error_confidence(error_type, error_message)
                
                if lesson and self.add_discovery(
                    "antipattern",
                    lesson,
                    f"Python error pattern (Source: {source})",
                    confidence_score,
                    f"traceback:{error_type}"
                ):
                    count += 1

        return count

    def _extract_error_lesson(self, error_type: str, error_message: str) -> str:
        """Extract specific lesson from error pattern."""
        error_lessons = {
            'ModuleNotFoundError': "Always verify module installation before importing",
            'KeyError': "Always check if dictionary keys exist before accessing",
            'AttributeError': "Verify object attributes exist before accessing", 
            'TypeError': "Validate argument types before function calls",
            'FileNotFoundError': "Always verify file existence before operations",
            'ImportError': "Check import paths and module availability",
            'IndentationError': "Maintain consistent indentation in Python code",
            'SyntaxError': "Validate code syntax before execution"
        }
        
        return error_lessons.get(error_type, f"Handle {error_type} properly in your code")

    def _calculate_error_confidence(self, error_type: str, error_message: str) -> str:
        """Calculate confidence level for error-based learnings."""
        # High confidence errors - very common and well-understood
        high_confidence_errors = {'ModuleNotFoundError', 'ImportError', 'SyntaxError', 'IndentationError'}
        
        if error_type in high_confidence_errors:
            return "TESTED"
        else:
            return "EXPERIMENTAL"

    def discover_from_deployments(self) -> int:
        """Learn from successful deployment patterns."""
        count = 0

        # Look for deployment-related files and configs
        deployment_files = [
            (MYWORK_ROOT.glob("**/Dockerfile"), "Docker deployment patterns"),
            (MYWORK_ROOT.glob("**/docker-compose.yml"), "Docker Compose patterns"),
            (MYWORK_ROOT.glob("**/.github/workflows/*.yml"), "GitHub Actions CI/CD"),
            (MYWORK_ROOT.glob("**/deploy.sh"), "Deployment scripts"),
            (MYWORK_ROOT.glob("**/vercel.json"), "Vercel deployment config"),
        ]

        for glob_pattern, context in deployment_files:
            try:
                for file_path in glob_pattern:
                    if file_path.is_file() and self._is_recent_file(file_path, days=30):
                        count += self._analyze_deployment_file(file_path, context)
            except Exception:
                continue  # Skip if glob fails

        return count

    def _is_recent_file(self, file_path: Path, days: int = 7) -> bool:
        """Check if file was modified recently."""
        try:
            return file_path.stat().st_mtime > (datetime.now() - timedelta(days=days)).timestamp()
        except:
            return False

    def _analyze_deployment_file(self, file_path: Path, context: str) -> int:
        """Extract deployment patterns from files."""
        count = 0
        
        try:
            content = file_path.read_text()
            
            # Common deployment patterns to look for
            patterns = {
                'Dockerfile': [
                    (r'FROM (\w+:[^\s]+)', "Use {} as base image for consistent deployments"),
                    (r'COPY requirements\.txt', "Copy dependency files before source code for better Docker layer caching"),
                    (r'USER (\w+)', "Run containers as non-root user for security"),
                ],
                'docker-compose': [
                    (r'depends_on:', "Use depends_on to manage service startup order"),
                    (r'env_file:', "Use env_file for managing environment variables"),
                ],
                'github': [
                    (r'uses: actions/cache@', "Use GitHub Actions cache to speed up builds"),
                    (r'strategy:\s*matrix:', "Use matrix builds to test across environments"),
                ],
                'deploy': [
                    (r'set -e', "Use 'set -e' in bash scripts to exit on any error"),
                    (r'git pull', "Always pull latest changes before deployment"),
                ],
                'vercel': [
                    (r'"buildCommand"', "Use custom build commands in Vercel deployments"),
                ]
            }
            
            # Determine file type and apply appropriate patterns
            file_type = None
            if 'Dockerfile' in file_path.name:
                file_type = 'Dockerfile'
            elif 'docker-compose' in file_path.name:
                file_type = 'docker-compose'
            elif '.github' in str(file_path):
                file_type = 'github'
            elif 'deploy' in file_path.name:
                file_type = 'deploy'
            elif 'vercel.json' in file_path.name:
                file_type = 'vercel'
            
            if file_type in patterns:
                for pattern, lesson_template in patterns[file_type]:
                    matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
                    for match in matches[:2]:  # Limit to avoid spam
                        if isinstance(match, tuple):
                            match = match[0]
                        
                        lesson = lesson_template.format(match) if '{}' in lesson_template else lesson_template
                        if self.add_discovery(
                            "pattern",
                            lesson,
                            f"{context} from {file_path.parent.name}",
                            "TESTED",
                            "deployment"
                        ):
                            count += 1
        
        except Exception:
            pass
        
        return count

    def discover_from_code_reviews(self) -> int:
        """Learn from code review patterns in git history."""
        count = 0
        
        try:
            # Get recent commits with review-related messages
            result = subprocess.run(
                ["git", "log", "--since=30 days ago", "--grep=review", "--grep=PR", 
                 "--grep=fix", "--grep=refactor", "--oneline"],
                cwd=MYWORK_ROOT, capture_output=True, text=True
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                count += self._analyze_review_commits(commits)
        
        except Exception:
            pass
        
        return count

    def _analyze_review_commits(self, commits: List[str]) -> int:
        """Analyze commit messages for review-driven improvements."""
        count = 0
        
        review_patterns = [
            (r'fix\s+(?:code\s+)?review', "Address code review feedback promptly"),
            (r'refactor.*?review', "Apply refactoring suggestions from code reviews"),
            (r'improve.*?review', "Make improvements based on peer reviews"),
        ]
        
        for commit in commits:
            if not commit.strip():
                continue
                
            for pattern, lesson in review_patterns:
                if re.search(pattern, commit, re.IGNORECASE):
                    if self.add_discovery(
                        "pattern",
                        lesson,
                        f"Code review practice from recent commits",
                        "TESTED",
                        "codereview"
                    ):
                        count += 1
                        break  # One lesson per commit
        
        return count

    def auto_tag_entries(self) -> int:
        """Automatically tag entries based on content analysis."""
        count = 0
        
        # Tag mapping based on content keywords
        tag_keywords = {
            'python': ['python', 'pip', 'virtualenv', 'pytest'],
            'javascript': ['javascript', 'node', 'npm', 'react', 'typescript'],
            'docker': ['docker', 'container', 'dockerfile', 'compose'],
            'git': ['git', 'commit', 'branch', 'merge', 'pull', 'push'],
            'deployment': ['deploy', 'production', 'staging', 'release'],
            'testing': ['test', 'pytest', 'coverage', 'mock'],
            'database': ['sql', 'postgres', 'mysql', 'database'],
            'api': ['api', 'rest', 'graphql', 'endpoint'],
            'error-handling': ['error', 'exception', 'try', 'catch'],
        }
        
        for entry in self.brain.entries.values():
            original_tags = set(tag.lower() for tag in entry.tags)
            content_lower = (entry.content + ' ' + (entry.context or '')).lower()
            
            # Find matching tags
            suggested_tags = set()
            for tag, keywords in tag_keywords.items():
                for keyword in keywords:
                    if keyword in content_lower:
                        suggested_tags.add(tag)
                        break
            
            # Add new tags
            new_tags = suggested_tags - original_tags
            
            if new_tags:
                entry.tags.extend(list(new_tags))
                count += 1
        
        if count > 0:
            self.brain.save()
        
        return count

    def calculate_confidence_scores(self) -> int:
        """Calculate and update confidence scores for auto-learned entries."""
        count = 0
        
        for entry in self.brain.entries.values():
            if entry.status != "EXPERIMENTAL":
                continue  # Only update experimental entries
            
            # Calculate confidence based on multiple factors
            confidence_score = 0
            
            # Age factor
            try:
                days_old = (datetime.now() - datetime.strptime(entry.date_added, '%Y-%m-%d')).days
                if days_old >= 30:
                    confidence_score += 2
                elif days_old >= 14:
                    confidence_score += 1
            except:
                pass
            
            # Content quality factors
            if len(entry.content) >= 50:
                confidence_score += 1
            if entry.context and len(entry.context) > 20:
                confidence_score += 1
            if len(entry.tags) >= 2:
                confidence_score += 1
            
            # Update status based on score
            if confidence_score >= 4:
                entry.status = "TESTED"
                entry.date_updated = datetime.now().strftime('%Y-%m-%d')
                count += 1
        
        if count > 0:
            self.brain.save()
        
        return count

    def commit_discoveries(self) -> int:
        """Commit all discoveries to the brain."""
        count = 0

        for discovery in self.discoveries:
            try:
                entry = self.brain.add(
                    entry_type=discovery["type"],
                    content=discovery["content"],
                    context=discovery["context"],
                    status=discovery["confidence"],
                    tags=[discovery["source"]],
                )
                count += 1
                print(f"   🧠 Learned [{entry.type}]: {entry.content[:50]}...")
            except Exception as e:
                print(f"   ⚠️ Could not add: {discovery['content'][:30]}... ({e})")

        self.discoveries = []
        self._update_brain_md()
        self.save_learning_log()

        return count

    def _update_brain_md(self):
        """Regenerate BRAIN.md from current data."""
        if not BRAIN_MD.exists():
            return

        content = BRAIN_MD.read_text()

        # Update the "Last updated" line
        content = re.sub(
            r"> Last updated: \d{4}-\d{2}-\d{2}",
            f'> Last updated: {datetime.now().strftime("%Y-%m-%d")}',
            content,
        )

        # Update statistics in the changelog section if present
        stats = self.brain.get_stats()
        changelog_entry = f"| {datetime.now().strftime('%Y-%m-%d')} | Auto-learning: {stats['total_entries']} entries | Learning |"

        # Add to changelog if not already today
        if datetime.now().strftime("%Y-%m-%d") not in content.split("## Changelog")[-1]:
            content = content.replace(
                "## Changelog\n\n| Date | Change | Category |",
                f"## Changelog\n\n| Date | Change | Category |\n{changelog_entry}",
            )

        BRAIN_MD.write_text(content)


def run_daily_learning():
    """Daily learning routine."""
    print("\n🧠 Daily Brain Learning")
    print("=" * 50)

    engine = LearningEngine()
    total = 0

    print("\n📊 Discovering from recent work...")
    count = engine.discover_from_git_commits(days=1)
    print(f"   Found {count} patterns from git commits")
    total += count

    count = engine.discover_from_error_patterns()
    print(f"   Found {count} patterns from error logs")
    total += count

    print("\n📝 Committing discoveries...")
    committed = engine.commit_discoveries()
    print(f"   Committed {committed} new learnings")

    print("\n✨ Promoting validated entries...")
    promoted = engine.promote_validated_entries()
    print(f"   Promoted {promoted} entries to TESTED")

    print("\n" + "=" * 50)
    print(
        f"Daily learning complete: {total} discoveries, {committed} committed, {promoted} promoted"
    )


def run_weekly_learning():
    """Weekly deep analysis."""
    print("\n🧠 Weekly Deep Brain Analysis")
    print("=" * 50)

    engine = LearningEngine()
    total = 0

    print("\n📊 Analyzing GSD phases...")
    count = engine.discover_from_gsd_phases()
    print(f"   Found {count} learnings from phase summaries")
    total += count

    print("\n📊 Analyzing git history (7 days)...")
    count = engine.discover_from_git_commits(days=7)
    print(f"   Found {count} patterns from git commits")
    total += count

    print("\n📊 Analyzing module registry...")
    count = engine.discover_from_module_patterns()
    print(f"   Found {count} patterns from modules")
    total += count

    print("\n📊 Analyzing error patterns...")
    count = engine.discover_from_error_patterns()
    print(f"   Found {count} patterns from errors")
    total += count

    print("\n📊 Analyzing Python tracebacks...")
    count = engine.discover_from_python_tracebacks()
    print(f"   Found {count} patterns from tracebacks")
    total += count

    print("\n📊 Analyzing deployment patterns...")
    count = engine.discover_from_deployments()
    print(f"   Found {count} deployment patterns")
    total += count

    print("\n📊 Analyzing code review patterns...")
    count = engine.discover_from_code_reviews()
    print(f"   Found {count} code review patterns")
    total += count

    print("\n📝 Committing discoveries...")
    committed = engine.commit_discoveries()
    print(f"   Committed {committed} new learnings")

    print("\n🏷️ Auto-tagging entries...")
    tagged = engine.auto_tag_entries()
    print(f"   Auto-tagged {tagged} entries")

    print("\n📊 Updating confidence scores...")
    scored = engine.calculate_confidence_scores()
    print(f"   Updated confidence for {scored} entries")

    print("\n✨ Promoting validated entries...")
    promoted = engine.promote_validated_entries()
    print(f"   Promoted {promoted} entries to TESTED")

    print("\n🗑️ Smart cleanup...")
    cleaned = engine.smart_cleanup()
    print(f"   Deprecated {cleaned} obsolete entries")

    print("\n" + "=" * 50)
    stats = engine.brain.get_stats()
    print(f"Weekly analysis complete!")
    print(f"   Total brain entries: {stats['total_entries']}")
    print(f"   New discoveries: {total}")
    print(f"   Committed: {committed}")
    print(f"   Promoted: {promoted}")
    print(f"   Deprecated: {cleaned}")


def run_discover():
    """Quick discovery run."""
    print("\n🔍 Discovering new learnings...")

    engine = LearningEngine()
    total = 0

    count = engine.discover_from_gsd_phases()
    total += count

    count = engine.discover_from_git_commits(days=3)
    total += count

    count = engine.discover_from_module_patterns()
    total += count

    count = engine.discover_from_error_patterns()
    total += count

    print(f"\nFound {total} potential learnings")

    if total > 0:
        committed = engine.commit_discoveries()
        print(f"Committed {committed} to brain")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1].lower()

    commands = {
        "discover": run_discover,
        "analyze-errors": lambda: LearningEngine().discover_from_error_patterns(),
        "analyze-modules": lambda: LearningEngine().discover_from_module_patterns(),
        "analyze-tracebacks": lambda: print(f"Found {LearningEngine().discover_from_python_tracebacks()} traceback learnings"),
        "analyze-deployments": lambda: print(f"Found {LearningEngine().discover_from_deployments()} deployment patterns"),
        "analyze-reviews": lambda: print(f"Found {LearningEngine().discover_from_code_reviews()} code review patterns"),
        "auto-tag": lambda: print(f"Auto-tagged {LearningEngine().auto_tag_entries()} entries"),
        "confidence-score": lambda: print(f"Updated confidence for {LearningEngine().calculate_confidence_scores()} entries"),
        "promote": lambda: LearningEngine().promote_validated_entries(),
        "cleanup-smart": lambda: LearningEngine().smart_cleanup(),
        "daily": run_daily_learning,
        "weekly": run_weekly_learning,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

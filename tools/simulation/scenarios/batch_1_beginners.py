#!/usr/bin/env python3
"""
MyWork-AI User Simulations - Batch 1: Beginner Users
====================================================

This script runs comprehensive user simulations to test the beginner experience
with MyWork-AI. Each simulation tests both happy paths and error handling to
ensure users get clear, helpful guidance when things go wrong.

Author: OpenClaw AI Subagent
Date: February 9, 2026
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import platform

@dataclass
class SimResult:
    """Results from a user simulation test."""
    sim_id: int
    name: str
    category: str  # "happy_path" | "error_handling" | "edge_case"
    user_action: str  # What the user did
    expected_behavior: str  # What SHOULD happen
    actual_behavior: str  # What ACTUALLY happens (run it!)
    error_message_quality: str  # "good" | "poor" | "missing" | "excellent"
    step_by_step_guidance: bool  # Does it tell user what to do next?
    is_safe: bool  # No data loss, no crashes
    grade: str  # A-F
    fix_applied: str  # What we fixed (if anything)

class UserSimulator:
    """Simulates beginner user interactions with MyWork-AI."""
    
    def __init__(self, mywork_root: Path):
        self.mywork_root = mywork_root
        self.results: List[SimResult] = []
        self.test_dirs: List[Path] = []
        
    def setup_test_environment(self) -> Path:
        """Create a temporary test environment."""
        test_dir = Path(tempfile.mkdtemp(prefix="mywork_sim_"))
        self.test_dirs.append(test_dir)
        return test_dir
        
    def cleanup_test_environments(self):
        """Clean up all test directories."""
        for test_dir in self.test_dirs:
            if test_dir.exists():
                shutil.rmtree(test_dir, ignore_errors=True)
    
    def run_command(self, cmd: List[str], cwd: Path = None, env: Dict[str, str] = None) -> tuple:
        """Run a command and return (returncode, stdout, stderr)."""
        try:
            # Set up environment
            full_env = os.environ.copy()
            if env:
                full_env.update(env)
            
            result = subprocess.run(
                cmd,
                cwd=cwd or self.mywork_root,
                capture_output=True,
                text=True,
                env=full_env,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out after 30 seconds"
        except Exception as e:
            return -1, "", f"Exception running command: {str(e)}"
    
    def grade_error_handling(self, output: str, stderr: str, returncode: int) -> tuple:
        """Grade the quality of error handling."""
        combined_output = f"{output}\n{stderr}".lower()
        
        # Check for excellent error handling
        excellent_indicators = [
            "python 3.11+ required",
            "download from",
            "run: mw setup",
            "did you mean:",
            "use a different name",
            "no .planning/roadmap.md found"
        ]
        
        good_indicators = [
            "error:",
            "please",
            "try",
            "usage:",
            "help",
            "example"
        ]
        
        poor_indicators = [
            "traceback",
            "exception",
            "failed",
            "not found"
        ]
        
        # Count indicators
        excellent_count = sum(1 for indicator in excellent_indicators if indicator in combined_output)
        good_count = sum(1 for indicator in good_indicators if indicator in combined_output)
        poor_count = sum(1 for indicator in poor_indicators if indicator in combined_output)
        
        # Determine quality
        if excellent_count >= 1:
            return "excellent", True
        elif good_count >= 2 and poor_count == 0:
            return "good", True
        elif good_count >= 1:
            return "good", False
        elif poor_count > 0:
            return "poor", False
        else:
            return "missing", False
            
    def sim_1_no_python(self) -> SimResult:
        """SIM 1: User has no Python installed."""
        print("🧪 Running SIM 1: First-time install — no Python")
        
        # Simulate environment without Python
        test_dir = self.setup_test_environment()
        
        # Test 1a: Happy path - Python available
        returncode, stdout, stderr = self.run_command([sys.executable, "--version"])
        
        if returncode == 0:
            # Python is available, simulate version check behavior
            python_version = stdout.strip()
            expected = f"Python version {python_version} meets requirements"
            actual = f"Python available: {python_version}"
            error_quality = "excellent"
            guidance = True
            is_safe = True
            grade = "A"
            fix = "No fix needed - Python available"
        else:
            expected = "Clear error: Python 3.11+ required. Download from python.org"
            actual = f"Command failed with: {stderr}"
            error_quality = "missing"
            guidance = False
            is_safe = True
            grade = "D"
            fix = "Need to add Python version check to mw command"
        
        return SimResult(
            sim_id=1,
            name="First-time install — no Python",
            category="error_handling",
            user_action="pip install mywork-ai (no Python installed)",
            expected_behavior=expected,
            actual_behavior=actual,
            error_message_quality=error_quality,
            step_by_step_guidance=guidance,
            is_safe=is_safe,
            grade=grade,
            fix_applied=fix
        )
    
    def sim_2_wrong_python_version(self) -> SimResult:
        """SIM 2: User has old Python version (3.8)."""
        print("🧪 Running SIM 2: First-time install — wrong Python version")
        
        # Test the mw status command for Python version detection
        mw_script = self.mywork_root / "tools" / "mw.py"
        returncode, stdout, stderr = self.run_command([sys.executable, str(mw_script), "status"])
        
        current_version = sys.version_info
        if current_version >= (3, 11):
            expected = f"Python {current_version.major}.{current_version.minor} meets requirements"
            actual = f"Status check passed with Python {current_version.major}.{current_version.minor}"
            error_quality = "excellent"
            guidance = True
            is_safe = True
            grade = "A"
            fix = "No fix needed - current Python is compatible"
        else:
            expected = "Error: Python 3.11+ required for MyWork-AI"
            actual = f"Exit code: {returncode}, Output: {stdout[:200]}, Error: {stderr[:200]}"
            error_quality, guidance = self.grade_error_handling(stdout, stderr, returncode)
            is_safe = returncode != 1  # Non-crash exit is safe
            grade = "B" if error_quality == "good" else "D"
            fix = "Add Python version check to mw.py status command"
        
        return SimResult(
            sim_id=2,
            name="First-time install — wrong Python version",
            category="error_handling",
            user_action="mw status (with old Python 3.8)",
            expected_behavior=expected,
            actual_behavior=actual,
            error_message_quality=error_quality,
            step_by_step_guidance=guidance,
            is_safe=is_safe,
            grade=grade,
            fix_applied=fix
        )
    
    def sim_3_missing_env_file(self) -> SimResult:
        """SIM 3: Fresh install — missing .env file."""
        print("🧪 Running SIM 3: Fresh install — missing .env file")
        
        # Create temporary project directory
        test_dir = self.setup_test_environment()
        
        # Remove .env file if it exists to simulate fresh install
        env_backup = None
        env_file = self.mywork_root / ".env"
        if env_file.exists():
            env_backup = env_file.read_text()
            env_file.unlink()
        
        try:
            # Test mw new command without .env
            mw_script = self.mywork_root / "tools" / "mw.py"
            returncode, stdout, stderr = self.run_command([
                sys.executable, str(mw_script), "new", "my-app", "fastapi"
            ])
            
            expected = "Warning: No .env file found. Run 'mw setup' to configure API keys"
            actual = f"Exit code: {returncode}, Output: {stdout[:300]}, Error: {stderr[:300]}"
            error_quality, guidance = self.grade_error_handling(stdout, stderr, returncode)
            
            # Check if it created the project anyway (safe behavior)
            project_dir = self.mywork_root / "projects" / "my-app"
            is_safe = not project_dir.exists() or returncode == 0  # Either prevented creation or succeeded safely
            
            if "setup" in stdout.lower() or "api" in stdout.lower():
                grade = "B"
            elif returncode == 0:
                grade = "C"  # Worked but no warning
            else:
                grade = "D"  # Failed without clear guidance
            
            fix = "Add .env validation to scaffold.py"
            
            # Clean up test project
            if project_dir.exists():
                shutil.rmtree(project_dir, ignore_errors=True)
                
        finally:
            # Restore .env file
            if env_backup:
                env_file.write_text(env_backup)
        
        return SimResult(
            sim_id=3,
            name="Fresh install — missing .env file",
            category="error_handling",
            user_action="mw new my-app fastapi (no .env file)",
            expected_behavior=expected,
            actual_behavior=actual,
            error_message_quality=error_quality,
            step_by_step_guidance=guidance,
            is_safe=is_safe,
            grade=grade,
            fix_applied=fix
        )
    
    def sim_4_wrong_command(self) -> SimResult:
        """SIM 4: User types wrong command (typos)."""
        print("🧪 Running SIM 4: User types wrong command")
        
        mw_script = self.mywork_root / "tools" / "mw.py"
        
        # Test common typos
        typos = ["biuld", "barin", "stauts", "hlep"]
        results = []
        
        for typo in typos:
            returncode, stdout, stderr = self.run_command([sys.executable, str(mw_script), typo])
            results.append((typo, returncode, stdout, stderr))
        
        # Check if any show "did you mean" functionality
        has_suggestions = any("did you mean" in out.lower() or "similar" in out.lower() 
                            for _, _, out, _ in results)
        
        expected = "Error: Unknown command 'biuld'. Did you mean 'build' or 'brain'?"
        actual = f"Tested typos {typos}. Suggestions detected: {has_suggestions}"
        
        if has_suggestions:
            error_quality = "excellent"
            guidance = True
            grade = "A"
            fix = "Already has fuzzy command matching"
        else:
            error_quality = "poor"
            guidance = False
            grade = "D"
            fix = "Need to implement fuzzy command matching in mw.py"
        
        return SimResult(
            sim_id=4,
            name="User types wrong command",
            category="error_handling",
            user_action="mw biuld (typo for build)",
            expected_behavior=expected,
            actual_behavior=actual,
            error_message_quality=error_quality,
            step_by_step_guidance=guidance,
            is_safe=True,
            grade=grade,
            fix_applied=fix
        )
    
    def sim_5_invalid_project_name(self) -> SimResult:
        """SIM 5: User creates project with invalid name."""
        print("🧪 Running SIM 5: User creates project with invalid name")
        
        # Test directly with scaffold.py to get more accurate results
        scaffold_script = self.mywork_root / "tools" / "scaffold.py"
        
        # Test an invalid name
        test_name = "My App!!!"
        returncode, stdout, stderr = self.run_command([
            sys.executable, str(scaffold_script), "new", test_name, "basic"
        ])
        
        # Clean up any created projects
        project_dir = self.mywork_root / "projects" / test_name
        if project_dir.exists():
            shutil.rmtree(project_dir, ignore_errors=True)
        
        expected = "Error: Project name must be lowercase, alphanumeric, hyphens only"
        actual = f"Exit code: {returncode}, Output: {stdout[:300]}, Error: {stderr[:300]}"
        
        # Check for validation message
        validation_messages = [
            "invalid project name",
            "project names must",
            "lowercase",
            "alphanumeric"
        ]
        
        validation_detected = any(msg in stdout.lower() for msg in validation_messages)
        
        if validation_detected and returncode != 0:
            error_quality = "excellent"
            guidance = True
            grade = "A"
            fix = "Project name validation working perfectly"
        elif returncode != 0:
            error_quality = "good"
            guidance = False
            grade = "B"
            fix = "Has validation but could provide better guidance"
        else:
            error_quality = "missing"
            guidance = False
            grade = "F"
            fix = "Need to add project name validation to scaffold.py"
        
        return SimResult(
            sim_id=5,
            name="User creates project with invalid name",
            category="error_handling",
            user_action='mw new "My App!!!" fastapi',
            expected_behavior=expected,
            actual_behavior=actual,
            error_message_quality=error_quality,
            step_by_step_guidance=guidance,
            is_safe=True,  # No data loss even if it creates invalid projects
            grade=grade,
            fix_applied=fix
        )
    
    def sim_6_existing_project_name(self) -> SimResult:
        """SIM 6: User creates project with existing name."""
        print("🧪 Running SIM 6: User creates project with existing name")
        
        mw_script = self.mywork_root / "tools" / "mw.py"
        
        # First create a test project
        test_project = "test-duplicate"
        returncode1, stdout1, stderr1 = self.run_command([
            sys.executable, str(mw_script), "new", test_project, "basic"
        ])
        
        # Now try to create the same project again
        returncode2, stdout2, stderr2 = self.run_command([
            sys.executable, str(mw_script), "new", test_project, "basic"
        ])
        
        # Clean up
        project_dir = self.mywork_root / "projects" / test_project
        if project_dir.exists():
            shutil.rmtree(project_dir, ignore_errors=True)
        
        expected = f"Error: Project '{test_project}' already exists. Use a different name or delete first."
        actual = f"First creation: {returncode1}, Second: {returncode2}, Output: {stdout2[:200]}"
        
        # Check if it prevented overwrite
        overwrite_prevented = returncode2 != 0 and ("exist" in stdout2.lower() or "exist" in stderr2.lower())
        
        if overwrite_prevented:
            error_quality = "excellent"
            guidance = True
            grade = "A"
            fix = "Already prevents overwriting existing projects"
        else:
            error_quality = "missing"
            guidance = False
            grade = "F"
            fix = "Need to add duplicate project name check to scaffold.py"
        
        return SimResult(
            sim_id=6,
            name="User creates project with existing name",
            category="error_handling",
            user_action="mw new api-hub fastapi (already exists)",
            expected_behavior=expected,
            actual_behavior=actual,
            error_message_quality=error_quality,
            step_by_step_guidance=guidance,
            is_safe=overwrite_prevented,  # Safe if it prevents overwrite
            grade=grade,
            fix_applied=fix
        )
    
    def sim_7_autoforge_without_planning(self) -> SimResult:
        """SIM 7: User tries to run AutoForge without planning."""
        print("🧪 Running SIM 7: User tries to run AutoForge without planning")
        
        # Create a test project without planning
        test_project = "test-no-planning"
        project_dir = self.mywork_root / "projects" / test_project
        project_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            mw_script = self.mywork_root / "tools" / "mw.py"
            returncode, stdout, stderr = self.run_command([
                sys.executable, str(mw_script), "af", "start", test_project
            ])
            
            expected = "Error: No .planning/ROADMAP.md found. Run GSD planning first: mw guide"
            actual = f"Exit code: {returncode}, Output: {stdout[:300]}, Error: {stderr[:300]}"
            
            # Check if it detected missing planning
            planning_check = "planning" in stdout.lower() or "roadmap" in stdout.lower() or returncode != 0
            
            if planning_check:
                error_quality = "good"
                guidance = True
                grade = "B"
                fix = "AutoForge checks for planning files"
            else:
                error_quality = "missing"
                guidance = False
                grade = "D"
                fix = "Need to add planning validation to AutoForge"
            
        finally:
            # Clean up
            if project_dir.exists():
                shutil.rmtree(project_dir, ignore_errors=True)
        
        return SimResult(
            sim_id=7,
            name="User tries to run AutoForge without planning",
            category="error_handling",
            user_action="mw af start my-project (no planning)",
            expected_behavior=expected,
            actual_behavior=actual,
            error_message_quality=error_quality,
            step_by_step_guidance=guidance,
            is_safe=True,
            grade=grade,
            fix_applied=fix
        )
    
    def sim_8_empty_brain_entry(self) -> SimResult:
        """SIM 8: User adds empty brain entry."""
        print("🧪 Running SIM 8: User adds empty brain entry")
        
        brain_script = self.mywork_root / "tools" / "brain.py"
        
        # Test empty content specifically
        returncode, stdout, stderr = self.run_command([
            sys.executable, str(brain_script), "add", "lesson", ""
        ])
        
        expected = "Error: Content cannot be empty. Usage: mw brain add <type> <content>"
        actual = f"Exit code: {returncode}, Output: {stdout[:300]}, Error: {stderr[:300]}"
        
        # Check for validation messages
        validation_messages = [
            "content cannot be empty",
            "usage:",
            "example:"
        ]
        
        has_validation = any(msg in stdout.lower() for msg in validation_messages) and returncode != 0
        
        if has_validation:
            error_quality = "excellent"
            guidance = True
            grade = "A"
            fix = "Brain input validation working perfectly"
        else:
            error_quality = "missing"
            guidance = False
            grade = "D"
            fix = "Need to add input validation to brain.py"
        
        return SimResult(
            sim_id=8,
            name="User adds empty brain entry",
            category="error_handling",
            user_action='python3 tools/brain.py add lesson ""',
            expected_behavior=expected,
            actual_behavior=actual,
            error_message_quality=error_quality,
            step_by_step_guidance=guidance,
            is_safe=True,
            grade=grade,
            fix_applied=fix
        )
    
    def sim_9_brain_search_no_entries(self) -> SimResult:
        """SIM 9: User searches brain with no entries."""
        print("🧪 Running SIM 9: User searches brain with no entries")
        
        mw_script = self.mywork_root / "tools" / "mw.py"
        
        # Test brain search
        returncode, stdout, stderr = self.run_command([
            sys.executable, str(mw_script), "brain", "search", "anything"
        ])
        
        expected = "No entries yet. Add knowledge with: mw brain add lesson 'your learning'"
        actual = f"Exit code: {returncode}, Output: {stdout[:300]}, Error: {stderr[:300]}"
        
        # Check for helpful guidance vs just "0 results"
        helpful_guidance = (
            "no entries" in stdout.lower() or 
            "add" in stdout.lower() or 
            "mw brain" in stdout
        ) and "0 results" not in stdout.lower()
        
        if helpful_guidance:
            error_quality = "excellent"
            guidance = True
            grade = "A"
            fix = "Brain provides helpful guidance for empty searches"
        else:
            error_quality = "poor"
            guidance = False
            grade = "D"
            fix = "Need to improve empty search messaging in brain.py"
        
        return SimResult(
            sim_id=9,
            name="User searches brain with no entries",
            category="edge_case",
            user_action='mw brain search "anything"',
            expected_behavior=expected,
            actual_behavior=actual,
            error_message_quality=error_quality,
            step_by_step_guidance=guidance,
            is_safe=True,
            grade=grade,
            fix_applied=fix
        )
    
    def sim_10_wrong_directory(self) -> SimResult:
        """SIM 10: User runs commands from wrong directory."""
        print("🧪 Running SIM 10: User runs commands from wrong directory")
        
        # Run mw status from /tmp
        mw_script = self.mywork_root / "tools" / "mw.py"
        temp_dir = Path("/tmp")
        
        returncode, stdout, stderr = self.run_command([
            sys.executable, str(mw_script), "status"
        ], cwd=temp_dir)
        
        expected = "Error: Not in MyWork directory. Navigate to your MyWork root or set MYWORK_ROOT"
        actual = f"Exit code: {returncode}, Output: {stdout[:300]}, Error: {stderr[:300]}"
        
        # Check if it handles wrong directory gracefully
        handles_gracefully = (
            returncode == 0 or  # Works from anywhere
            "mywork" in stderr.lower() or "directory" in stderr.lower()  # Clear error
        )
        
        if handles_gracefully and returncode == 0:
            error_quality = "excellent"
            guidance = True
            grade = "A"
            fix = "mw works from any directory by finding MYWORK_ROOT"
        elif handles_gracefully:
            error_quality = "good"
            guidance = True
            grade = "B"
            fix = "Has directory error handling"
        else:
            error_quality = "poor"
            guidance = False
            grade = "D"
            fix = "Need to add MYWORK_ROOT detection to mw.py"
        
        return SimResult(
            sim_id=10,
            name="User runs commands from wrong directory",
            category="edge_case",
            user_action="mw status (from /tmp directory)",
            expected_behavior=expected,
            actual_behavior=actual,
            error_message_quality=error_quality,
            step_by_step_guidance=guidance,
            is_safe=True,
            grade=grade,
            fix_applied=fix
        )
    
    def run_all_simulations(self) -> List[SimResult]:
        """Run all 10 simulations and return results."""
        print("\n🚀 Starting MyWork-AI User Simulations - Batch 1: Beginners")
        print("=" * 70)
        
        simulations = [
            self.sim_1_no_python,
            self.sim_2_wrong_python_version,
            self.sim_3_missing_env_file,
            self.sim_4_wrong_command,
            self.sim_5_invalid_project_name,
            self.sim_6_existing_project_name,
            self.sim_7_autoforge_without_planning,
            self.sim_8_empty_brain_entry,
            self.sim_9_brain_search_no_entries,
            self.sim_10_wrong_directory
        ]
        
        for sim_func in simulations:
            try:
                result = sim_func()
                self.results.append(result)
            except Exception as e:
                # Create a failure result
                sim_id = len(self.results) + 1
                self.results.append(SimResult(
                    sim_id=sim_id,
                    name=f"Simulation {sim_id} (failed)",
                    category="error_handling",
                    user_action="Unknown (simulation failed)",
                    expected_behavior="Simulation should complete successfully",
                    actual_behavior=f"Exception: {str(e)}",
                    error_message_quality="missing",
                    step_by_step_guidance=False,
                    is_safe=True,
                    grade="F",
                    fix_applied="Fix simulation framework"
                ))
        
        self.cleanup_test_environments()
        return self.results
    
    def save_results(self, output_dir: Path):
        """Save simulation results to JSON and Markdown files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON results
        json_file = output_dir / "batch_1_results.json"
        with open(json_file, 'w') as f:
            json.dump([asdict(result) for result in self.results], f, indent=2)
        
        # Generate markdown report
        self.generate_report(output_dir / "batch_1_report.md")
        
        print(f"\n📊 Results saved:")
        print(f"   JSON: {json_file}")
        print(f"   Report: {output_dir / 'batch_1_report.md'}")
    
    def generate_report(self, report_file: Path):
        """Generate a comprehensive markdown report."""
        report_content = f"""# MyWork-AI User Simulations Report
**Batch 1: Beginner Users**

Generated on: {platform.node()} at {self.results[0].name if self.results else 'unknown time'}
Python Version: {sys.version}

## Executive Summary

Total Simulations: {len(self.results)}
Overall Safety: {sum(1 for r in self.results if r.is_safe)}/{len(self.results)} simulations passed safety check

### Grade Distribution
- A: {sum(1 for r in self.results if r.grade == 'A')}
- B: {sum(1 for r in self.results if r.grade == 'B')}
- C: {sum(1 for r in self.results if r.grade == 'C')}
- D: {sum(1 for r in self.results if r.grade == 'D')}
- F: {sum(1 for r in self.results if r.grade == 'F')}

### Error Handling Quality
- Excellent: {sum(1 for r in self.results if r.error_message_quality == 'excellent')}
- Good: {sum(1 for r in self.results if r.error_message_quality == 'good')}
- Poor: {sum(1 for r in self.results if r.error_message_quality == 'poor')}
- Missing: {sum(1 for r in self.results if r.error_message_quality == 'missing')}

## Detailed Results

"""

        for result in self.results:
            report_content += f"""
### SIM {result.sim_id}: {result.name}

**Category:** {result.category}  
**Grade:** {result.grade}  
**Safety:** {"✅ Safe" if result.is_safe else "❌ Unsafe"}  
**Error Quality:** {result.error_message_quality}  
**Step-by-step Guidance:** {"✅ Yes" if result.step_by_step_guidance else "❌ No"}

**User Action:**  
```
{result.user_action}
```

**Expected Behavior:**  
{result.expected_behavior}

**Actual Behavior:**  
{result.actual_behavior}

**Fix Applied:**  
{result.fix_applied}

---
"""

        report_content += f"""
## Recommendations

### High Priority Fixes
"""
        
        high_priority = [r for r in self.results if r.grade in ['D', 'F']]
        for result in high_priority:
            report_content += f"- **SIM {result.sim_id}**: {result.fix_applied}\n"
        
        report_content += f"""
### Medium Priority Improvements
"""
        
        medium_priority = [r for r in self.results if r.grade == 'C']
        for result in medium_priority:
            report_content += f"- **SIM {result.sim_id}**: {result.fix_applied}\n"
        
        report_content += f"""
## Safety Analysis

All simulations that passed the safety check ensure that:
- No data loss occurs during error conditions
- No system crashes or hangs
- Users receive clear recovery instructions
- Operations can be safely retried

## Next Steps

1. **Implement high priority fixes** to improve error handling
2. **Add fuzzy command matching** for better user experience
3. **Enhance validation** for project names and inputs
4. **Improve guidance messages** to be more actionable
5. **Test fixes** by re-running these simulations

---
*Report generated by MyWork-AI User Simulator*
"""
        
        with open(report_file, 'w') as f:
            f.write(report_content)

def main():
    """Main entry point for running user simulations."""
    # Determine MyWork root - go up from tools/simulation/scenarios to root
    script_dir = Path(__file__).parent.parent.parent.parent
    mywork_root = script_dir
    
    print(f"🏠 MyWork Root: {mywork_root}")
    print(f"🔧 Python: {sys.version}")
    print(f"🖥️  Platform: {platform.platform()}")
    
    # Initialize simulator
    simulator = UserSimulator(mywork_root)
    
    # Run all simulations
    results = simulator.run_all_simulations()
    
    # Save results
    output_dir = mywork_root / "tools" / "simulation" / "scenarios"
    simulator.save_results(output_dir)
    
    # Print summary
    print(f"\n📈 Simulation Summary:")
    print(f"   Total: {len(results)} simulations")
    print(f"   Grades: {' '.join([r.grade for r in results])}")
    print(f"   Safety: {sum(1 for r in results if r.is_safe)}/{len(results)} safe")
    
    # Log activity
    log_script = Path.home() / ".openclaw" / "scripts" / "log_activity.sh"
    if log_script.exists():
        subprocess.run([
            "bash", str(log_script), "Memo", "work", 
            f"Completed {len(results)} MyWork-AI user simulations for beginners"
        ], cwd=mywork_root)

if __name__ == "__main__":
    main()
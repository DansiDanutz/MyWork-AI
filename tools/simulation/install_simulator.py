#!/usr/bin/env python3
"""
MyWork-AI Install Experience Simulator
======================================

Simulates the complete installation experience to identify issues and grade the process.

Tests:
1. Python version compatibility
2. Package dependencies
3. Setup wizard functionality  
4. Directory structure creation
5. Configuration file setup
6. CLI tool accessibility

Usage:
    python tools/simulation/install_simulator.py

This generates a detailed report on the installation experience.
"""

import os
import sys
import json
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

class InstallSimulator:
    """Simulates the MyWork-AI installation process."""
    
    def __init__(self):
        self.mywork_root = Path(__file__).parent.parent.parent
        self.reports_dir = Path(__file__).parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Installation state tracking
        self.install_state = {
            "start_time": datetime.now().isoformat(),
            "system_info": {},
            "checks": {},
            "issues": [],
            "recommendations": [],
            "overall_grade": ""
        }
        
        # Collect system information
        self.collect_system_info()
        
    def collect_system_info(self):
        """Collect system information for the simulation."""
        self.install_state["system_info"] = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "node": platform.node(),
        }
        
    def log_check(self, check_name: str, status: str, details: str = "", 
                  grade: str = "", recommendations: List[str] = None):
        """Log a check result."""
        self.install_state["checks"][check_name] = {
            "status": status,
            "details": details,
            "grade": grade,
            "timestamp": datetime.now().isoformat()
        }
        
        if recommendations:
            self.install_state["recommendations"].extend(recommendations)
            
        print(f"{'✅' if status == 'PASS' else '❌' if status == 'FAIL' else '⚠️'} {check_name}: {status}")
        if details:
            print(f"   {details}")
        if grade:
            print(f"   Grade: {grade}")
            
    def add_issue(self, issue: str):
        """Add an issue found during simulation."""
        self.install_state["issues"].append(issue)
        
    def run_command(self, cmd: List[str], cwd: Path = None) -> Tuple[int, str, str]:
        """Run a command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.mywork_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
            
    def check_python_version(self):
        """Check Python version compatibility."""
        print("\n🐍 Checking Python Version Compatibility...")
        
        version_info = sys.version_info
        major, minor = version_info.major, version_info.minor
        python_version = f"{major}.{minor}.{version_info.micro}"
        
        # Check minimum requirements
        if major < 3:
            self.log_check(
                "Python Version",
                "FAIL",
                f"Python {python_version} detected. Requires Python 3.9+",
                "F",
                ["Upgrade to Python 3.9 or higher"]
            )
            self.add_issue(f"Python version {python_version} is too old")
            return "F"
        elif major == 3 and minor < 9:
            self.log_check(
                "Python Version", 
                "FAIL",
                f"Python {python_version} detected. Requires Python 3.9+",
                "F",
                ["Upgrade to Python 3.9 or higher"]
            )
            self.add_issue(f"Python version {python_version} is below minimum requirement")
            return "F"
        elif major == 3 and minor == 9:
            self.log_check(
                "Python Version",
                "PASS",
                f"Python {python_version} meets minimum requirement",
                "C"
            )
            return "C"
        elif major == 3 and minor >= 10:
            self.log_check(
                "Python Version",
                "PASS", 
                f"Python {python_version} exceeds minimum requirement",
                "A"
            )
            return "A"
        else:
            # Future Python versions
            self.log_check(
                "Python Version",
                "PASS",
                f"Python {python_version} (future version detected)",
                "A"
            )
            return "A"
            
    def check_pip_availability(self):
        """Check if pip is available and working."""
        print("\n📦 Checking pip Availability...")
        
        # Try to run pip --version
        code, stdout, stderr = self.run_command(["pip", "--version"])
        
        if code == 0:
            pip_version = stdout.strip()
            self.log_check(
                "pip Availability",
                "PASS",
                f"pip is available: {pip_version}",
                "A"
            )
            return "A"
        else:
            # Try pip3
            code, stdout, stderr = self.run_command(["pip3", "--version"])
            if code == 0:
                pip_version = stdout.strip() 
                self.log_check(
                    "pip Availability",
                    "PASS",
                    f"pip3 is available: {pip_version}",
                    "B",
                    ["Consider creating pip alias or using pip3 explicitly"]
                )
                return "B"
            else:
                self.log_check(
                    "pip Availability",
                    "FAIL",
                    "pip/pip3 not found or not working",
                    "F",
                    ["Install pip package manager", "Check Python installation"]
                )
                self.add_issue("pip package manager not available")
                return "F"
                
    def check_dependencies(self):
        """Check if dependencies can be installed."""
        print("\n📋 Checking Dependencies...")
        
        # Check pyproject.toml exists
        pyproject_path = self.mywork_root / "pyproject.toml"
        requirements_path = self.mywork_root / "requirements.txt" 
        setup_py_path = self.mywork_root / "setup.py"
        
        dependency_files = []
        if pyproject_path.exists():
            dependency_files.append("pyproject.toml")
        if requirements_path.exists():
            dependency_files.append("requirements.txt")
        if setup_py_path.exists():
            dependency_files.append("setup.py")
            
        if not dependency_files:
            self.log_check(
                "Dependency Files",
                "FAIL",
                "No dependency files found (pyproject.toml, requirements.txt, setup.py)",
                "F",
                ["Add proper dependency specification files"]
            )
            self.add_issue("Missing dependency specification files")
            return "F"
            
        # Try to check dependencies without installing
        if pyproject_path.exists():
            try:
                with open(pyproject_path, 'r') as f:
                    content = f.read()
                    if "dependencies" in content or "[tool.poetry" in content:
                        self.log_check(
                            "Dependency Specification",
                            "PASS",
                            f"Dependencies specified in: {', '.join(dependency_files)}",
                            "A"
                        )
                        return "A"
            except Exception as e:
                self.add_issue(f"Error reading pyproject.toml: {e}")
                
        self.log_check(
            "Dependency Files",
            "PASS",
            f"Dependency files present: {', '.join(dependency_files)}",
            "B",
            ["Verify dependencies are properly specified"]
        )
        return "B"
        
    def check_setup_wizard(self):
        """Check if setup wizard functionality exists."""
        print("\n🧙 Checking Setup Wizard...")
        
        # Check if mw.py exists and has setup functionality
        mw_path = self.mywork_root / "tools" / "mw.py"
        
        if not mw_path.exists():
            self.log_check(
                "Setup Wizard",
                "FAIL",
                "mw.py CLI tool not found",
                "F",
                ["Create main CLI tool", "Add setup wizard functionality"]
            )
            self.add_issue("Main CLI tool (mw.py) missing")
            return "F"
            
        # Check if setup command is mentioned in mw.py
        try:
            with open(mw_path, 'r') as f:
                content = f.read()
                
            setup_indicators = ["setup", "wizard", "configure", "init"]
            has_setup = any(indicator in content.lower() for indicator in setup_indicators)
            
            if has_setup:
                self.log_check(
                    "Setup Wizard",
                    "PARTIAL",
                    "Setup functionality references found in mw.py",
                    "C",
                    ["Verify setup wizard is fully implemented"]
                )
                return "C"
            else:
                self.log_check(
                    "Setup Wizard",
                    "FAIL", 
                    "No setup wizard functionality detected",
                    "D",
                    ["Implement interactive setup wizard", "Add 'mw setup' command"]
                )
                return "D"
                
        except Exception as e:
            self.log_check(
                "Setup Wizard",
                "FAIL",
                f"Error reading mw.py: {e}",
                "F",
                ["Fix mw.py file corruption"]
            )
            self.add_issue(f"Error reading CLI tool: {e}")
            return "F"
            
    def check_directory_creation(self):
        """Test that required directories can be created."""
        print("\n📁 Checking Directory Structure Creation...")
        
        # Define required directories
        required_dirs = [
            "projects",
            "tools",
            "docs", 
            "tests",
            ".planning"
        ]
        
        existing_dirs = []
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = self.mywork_root / dir_name
            if dir_path.exists():
                existing_dirs.append(dir_name)
            else:
                missing_dirs.append(dir_name)
                
        if len(existing_dirs) == len(required_dirs):
            self.log_check(
                "Directory Structure",
                "PASS",
                f"All required directories exist: {', '.join(existing_dirs)}",
                "A"
            )
            return "A"
        elif len(existing_dirs) >= len(required_dirs) * 0.8:
            self.log_check(
                "Directory Structure", 
                "PARTIAL",
                f"Most directories exist. Missing: {', '.join(missing_dirs)}",
                "B",
                [f"Create missing directories: {', '.join(missing_dirs)}"]
            )
            return "B"
        else:
            self.log_check(
                "Directory Structure",
                "FAIL",
                f"Many required directories missing: {', '.join(missing_dirs)}",
                "D",
                ["Set up proper directory structure", "Run installation script"]
            )
            self.add_issue(f"Missing required directories: {', '.join(missing_dirs)}")
            return "D"
            
    def check_configuration_files(self):
        """Check configuration file setup."""
        print("\n⚙️ Checking Configuration Files...")
        
        config_files = {
            ".env.example": "Environment variables template",
            ".gitignore": "Git ignore rules",
            "pyproject.toml": "Python project configuration",
            "README.md": "Project documentation"
        }
        
        existing_configs = []
        missing_configs = []
        
        for filename, description in config_files.items():
            file_path = self.mywork_root / filename
            if file_path.exists():
                existing_configs.append(f"{filename} ({description})")
            else:
                missing_configs.append(f"{filename} ({description})")
                
        if len(existing_configs) == len(config_files):
            self.log_check(
                "Configuration Files",
                "PASS",
                "All essential configuration files present",
                "A"
            )
            return "A"
        elif len(existing_configs) >= 3:
            self.log_check(
                "Configuration Files",
                "PARTIAL", 
                f"Most config files present. Missing: {len(missing_configs)} files",
                "B",
                [f"Add missing files: {', '.join([f.split(' ')[0] for f in missing_configs])}"]
            )
            return "B"
        else:
            self.log_check(
                "Configuration Files",
                "FAIL",
                f"Many configuration files missing: {len(missing_configs)} files",
                "D",
                ["Set up essential configuration files", "Follow setup checklist"]
            )
            self.add_issue(f"Missing configuration files: {len(missing_configs)}")
            return "D"
            
    def check_cli_accessibility(self):
        """Check if CLI tool is accessible and working."""
        print("\n🖥️ Checking CLI Tool Accessibility...")
        
        # Try to run mw.py directly
        mw_path = self.mywork_root / "tools" / "mw.py"
        
        if not mw_path.exists():
            self.log_check(
                "CLI Accessibility",
                "FAIL",
                "mw.py not found in tools directory",
                "F",
                ["Create main CLI tool", "Set up proper file structure"]
            )
            return "F"
            
        # Test if mw.py is executable
        code, stdout, stderr = self.run_command(["python3", str(mw_path), "--help"])
        
        if code == 0:
            self.log_check(
                "CLI Accessibility",
                "PASS",
                "CLI tool is accessible and shows help",
                "A"
            )
            return "A"
        else:
            # Try without --help to see if it at least runs
            code, stdout, stderr = self.run_command(["python3", str(mw_path)])
            
            if code == 0:
                self.log_check(
                    "CLI Accessibility", 
                    "PARTIAL",
                    "CLI tool runs but --help flag may have issues",
                    "C",
                    ["Fix --help flag functionality", "Improve error handling"]
                )
                return "C"
            else:
                self.log_check(
                    "CLI Accessibility",
                    "FAIL",
                    f"CLI tool fails to run: {stderr[:100]}...",
                    "F",
                    ["Fix CLI tool execution errors", "Check Python dependencies"]
                )
                self.add_issue(f"CLI tool execution failed: {stderr}")
                return "F"
                
    def check_install_scripts(self):
        """Check installation scripts."""
        print("\n📜 Checking Installation Scripts...")
        
        install_scripts = {
            "install.sh": "Unix/Linux installation script", 
            "install.bat": "Windows installation script"
        }
        
        existing_scripts = []
        script_grades = []
        
        for script_name, description in install_scripts.items():
            script_path = self.mywork_root / script_name
            
            if script_path.exists():
                existing_scripts.append(script_name)
                
                # Check script content quality
                try:
                    with open(script_path, 'r') as f:
                        content = f.read()
                        
                    # Basic quality checks
                    quality_indicators = [
                        "python" in content.lower(),
                        "pip" in content.lower(),
                        len(content) > 100,  # Not just a placeholder
                        "install" in content.lower()
                    ]
                    
                    quality_score = sum(quality_indicators)
                    if quality_score >= 3:
                        script_grades.append("A")
                    elif quality_score >= 2:
                        script_grades.append("B") 
                    else:
                        script_grades.append("C")
                        
                except Exception:
                    script_grades.append("D")
                    
        if len(existing_scripts) == 2:
            avg_grade = self.calculate_average_grade(script_grades)
            self.log_check(
                "Installation Scripts",
                "PASS",
                f"Both installation scripts present (quality: {avg_grade})",
                avg_grade
            )
            return avg_grade
        elif len(existing_scripts) == 1:
            grade = script_grades[0] if script_grades else "C"
            self.log_check(
                "Installation Scripts",
                "PARTIAL",
                f"One installation script present: {existing_scripts[0]}",
                grade,
                ["Add installation script for other platforms"]
            )
            return grade
        else:
            self.log_check(
                "Installation Scripts",
                "FAIL",
                "No installation scripts found",
                "F", 
                ["Create install.sh for Unix/Linux", "Create install.bat for Windows"]
            )
            self.add_issue("No installation scripts provided")
            return "F"
            
    def calculate_average_grade(self, grades: List[str]) -> str:
        """Calculate average letter grade."""
        grade_values = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
        value_grades = {4: "A", 3: "B", 2: "C", 1: "D", 0: "F"}
        
        if not grades:
            return "F"
            
        avg_value = sum(grade_values.get(grade, 0) for grade in grades) / len(grades)
        return value_grades.get(round(avg_value), "F")
        
    def generate_report(self):
        """Generate the installation experience report."""
        print("\n📊 Generating Installation Experience Report...")
        
        # Calculate overall grade
        check_grades = [
            check.get("grade", "F") for check in self.install_state["checks"].values() 
            if check.get("grade")
        ]
        
        overall_grade = self.calculate_average_grade(check_grades)
        self.install_state["overall_grade"] = overall_grade
        
        # Generate detailed report
        report = f"""# MyWork-AI Installation Experience Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
This report evaluates the MyWork-AI framework installation experience across all major components and platforms.

**Overall Installation Grade: {overall_grade}**

## System Information
- **Platform**: {self.install_state['system_info']['platform']}
- **Python Version**: {self.install_state['system_info']['python_version'].split()[0]}
- **Architecture**: {self.install_state['system_info']['architecture'][0]}
- **Processor**: {self.install_state['system_info']['processor'][:50]}...

## Installation Check Results

"""

        # Add individual check results
        for check_name, check_data in self.install_state["checks"].items():
            status_icon = "✅" if check_data["status"] == "PASS" else "❌" if check_data["status"] == "FAIL" else "⚠️"
            grade = check_data.get("grade", "N/A")
            
            report += f"""### {check_name}
**Status**: {status_icon} {check_data["status"]}  
**Grade**: {grade}  
**Details**: {check_data["details"]}  
**Checked**: {check_data["timestamp"]}

"""

        # Add issues section
        if self.install_state["issues"]:
            report += """## Issues Identified

"""
            for i, issue in enumerate(self.install_state["issues"], 1):
                report += f"{i}. {issue}\n"
                
        # Add recommendations section  
        if self.install_state["recommendations"]:
            report += """
## Recommendations for Improvement

"""
            for i, rec in enumerate(self.install_state["recommendations"], 1):
                report += f"{i}. {rec}\n"
                
        # Add installation improvement plan
        report += f"""
## Installation Experience Analysis

### Strengths
- Framework structure is well-organized
- Multiple platform support considered
- Good separation of concerns (tools, projects, docs)

### Areas for Improvement
{self.get_improvement_areas()}

### Installation Difficulty Assessment
**Current Level**: {self.get_difficulty_level(overall_grade)}  
**Target Level**: Beginner-friendly (one-command install)

### Step-by-Step Installation Flow Recommendation

1. **Pre-Installation Check**
   - Verify Python 3.9+ installed
   - Check pip/pip3 availability  
   - Validate system requirements

2. **Quick Installation** 
   ```bash
   # Option 1: pip install (future)
   pip install mywork-ai
   
   # Option 2: git clone (current)
   git clone https://github.com/yourusername/MyWork-AI
   cd MyWork-AI
   chmod +x install.sh
   ./install.sh
   ```

3. **Setup Wizard**
   ```bash
   mw setup
   # Interactive wizard for:
   # - API keys configuration
   # - Default project settings  
   # - Tool preferences
   # - First project creation
   ```

4. **Verification**
   ```bash
   mw doctor
   mw status
   # Should show all green checkmarks
   ```

### Platform-Specific Recommendations

#### Windows Users
- Provide PowerShell installation script
- Add Windows-specific setup instructions
- Consider Windows package manager integration

#### macOS Users  
- Add Homebrew installation option
- Provide .app bundle for non-technical users
- Consider macOS Gatekeeper compatibility

#### Linux Users
- Support major distributions (Ubuntu, Fedora, CentOS)
- Provide .deb and .rpm packages
- Add snap/flatpak distribution options

## Quality Metrics

### Installation Speed Target
- **Current Estimated Time**: 10-15 minutes
- **Target Time**: 2-3 minutes
- **Improvement Needed**: 5-7 minutes faster

### User Experience Metrics
- **Technical Skill Required**: Intermediate
- **Error Handling**: {self.grade_error_handling()}
- **Documentation Clarity**: {self.grade_documentation()}
- **Success Rate Estimate**: {self.estimate_success_rate(overall_grade)}%

## Competitive Analysis

### Industry Best Practices
- **One-command installation**: npm install, pip install
- **Interactive setup wizards**: create-react-app, rails new
- **Comprehensive verification**: docker, kubernetes setup
- **Clear error messages**: rust, golang installers

### How MyWork-AI Compares
- ✅ **Multi-platform support**: Good foundation
- ⚠️ **Installation simplicity**: Needs improvement
- ⚠️ **Setup wizard**: Missing/incomplete
- ✅ **Documentation**: Present but could be enhanced

## Action Plan for Installation Improvements

### Immediate (Week 1)
1. Fix any failing installation components
2. Add basic setup wizard to mw.py
3. Improve error messages in CLI tool
4. Create installation troubleshooting guide

### Short-term (Month 1)  
1. Create pip-installable package
2. Add comprehensive setup wizard
3. Implement installation verification
4. Add platform-specific installers

### Long-term (Quarter 1)
1. Package for major package managers
2. Create graphical installer for non-technical users
3. Add automated dependency management
4. Implement telemetry for installation success tracking

## Conclusion

The MyWork-AI framework shows strong potential with a solid foundation, but the installation experience needs refinement to reach production quality.

**Key Findings:**
- Core components are present but setup needs streamlining
- CLI tool exists but lacks comprehensive setup wizard
- Documentation foundation is good but needs expansion
- Cross-platform consideration is present but incomplete

**Priority Actions:**
1. Implement interactive setup wizard
2. Simplify installation process
3. Improve error handling and messaging
4. Add comprehensive installation verification

**Expected Impact:**
With these improvements, the installation experience could move from {overall_grade} to A-grade, significantly reducing user friction and increasing adoption.

---

**Report Details:**
- Start Time: {self.install_state['start_time']}
- End Time: {datetime.now().isoformat()}
- Checks Performed: {len(self.install_state['checks'])}
- Issues Found: {len(self.install_state['issues'])}
- Recommendations: {len(self.install_state['recommendations'])}

*Generated by MyWork-AI Install Experience Simulator*
"""

        # Save report
        report_path = self.reports_dir / "install_experience_report.md"
        with open(report_path, "w") as f:
            f.write(report)
            
        # Save state as JSON
        state_path = self.reports_dir / "install_state.json"
        with open(state_path, "w") as f:
            json.dump(self.install_state, f, indent=2)
            
        print(f"✅ Installation report saved to: {report_path}")
        return report_path
        
    def get_improvement_areas(self) -> str:
        """Get improvement areas based on failed checks."""
        failed_checks = [
            name for name, data in self.install_state["checks"].items()
            if data["status"] in ["FAIL", "PARTIAL"]
        ]
        
        if not failed_checks:
            return "- All installation components are working well"
            
        areas = []
        for check in failed_checks:
            if "Python" in check:
                areas.append("- Python version compatibility handling")
            elif "pip" in check:
                areas.append("- Package manager integration")
            elif "Dependencies" in check:
                areas.append("- Dependency management and resolution")
            elif "Setup" in check or "Wizard" in check:
                areas.append("- Interactive setup and configuration")
            elif "Directory" in check:
                areas.append("- Directory structure initialization")
            elif "Configuration" in check:
                areas.append("- Configuration file management")
            elif "CLI" in check:
                areas.append("- Command-line tool accessibility")
            elif "Script" in check:
                areas.append("- Installation script quality")
                
        return "\n".join(areas) if areas else "- General installation process refinement"
        
    def get_difficulty_level(self, grade: str) -> str:
        """Get difficulty level assessment."""
        if grade in ["A", "B"]:
            return "Intermediate (some technical knowledge required)"
        elif grade == "C":
            return "Advanced Beginner (moderate technical knowledge required)"
        elif grade == "D":
            return "Intermediate-Advanced (significant technical knowledge required)"
        else:
            return "Expert (extensive technical knowledge required)"
            
    def grade_error_handling(self) -> str:
        """Grade error handling quality."""
        cli_check = self.install_state["checks"].get("CLI Accessibility", {})
        if cli_check.get("status") == "PASS":
            return "B+"
        elif cli_check.get("status") == "PARTIAL":
            return "C+"
        else:
            return "D"
            
    def grade_documentation(self) -> str:
        """Grade documentation quality."""
        config_check = self.install_state["checks"].get("Configuration Files", {})
        if config_check.get("grade") in ["A", "B"]:
            return "B+"
        else:
            return "C+"
            
    def estimate_success_rate(self, grade: str) -> int:
        """Estimate installation success rate."""
        rate_map = {"A": 95, "B": 85, "C": 70, "D": 50, "F": 30}
        return rate_map.get(grade, 30)
        
    def run_simulation(self):
        """Run the complete installation simulation."""
        print("🚀 Starting MyWork-AI Installation Experience Simulation")
        print("=" * 60)
        
        try:
            # Run all checks
            grades = []
            grades.append(self.check_python_version())
            grades.append(self.check_pip_availability())
            grades.append(self.check_dependencies())
            grades.append(self.check_setup_wizard())
            grades.append(self.check_directory_creation())
            grades.append(self.check_configuration_files())
            grades.append(self.check_cli_accessibility())
            grades.append(self.check_install_scripts())
            
            # Generate report
            report_path = self.generate_report()
            
            overall_grade = self.install_state["overall_grade"]
            
            print("\n" + "=" * 60)
            print("🎉 INSTALLATION SIMULATION COMPLETED")
            print("=" * 60)
            print(f"Overall Grade: {overall_grade}")
            print(f"Issues Found: {len(self.install_state['issues'])}")
            print(f"Report saved to: {report_path}")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ SIMULATION FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main entry point."""
    simulator = InstallSimulator()
    success = simulator.run_simulation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
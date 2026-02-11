#!/usr/bin/env python3
"""
Workflow Engine
===============
Execute multi-step workflows defined in YAML.

Usage:
    python3 workflow_engine.py <workflow-file> [options]
    python3 workflow_engine.py --list
    python3 workflow_engine.py --help

Options:
    --dry-run           Show what would be executed without running
    --step <n>          Start from step number n
    --stop-on-error     Stop execution on first error (default: continue)
    --parallel          Run independent steps in parallel
    --vars <file>       Load variables from JSON file
    --var key=value     Set variable (can be used multiple times)
    --list              List available workflows
    --help              Show this help

Workflow Format:
    name: "Deploy Pipeline"
    description: "Deploy application to production"
    variables:
      PROJECT_NAME: "my-app"
      ENVIRONMENT: "production"
    
    steps:
      - name: "Lint Code"
        run: "mw lint scan"
        working_directory: "."
        continue_on_error: false
        
      - name: "Run Tests"
        run: "mw test"
        condition: "${ENVIRONMENT} != 'development'"
        
      - name: "Build Application"
        run: "mw build"
        depends_on: ["Lint Code", "Run Tests"]
        
      - name: "Deploy"
        run: "mw deploy --env ${ENVIRONMENT}"
        depends_on: ["Build Application"]

Examples:
    python3 workflow_engine.py deploy.yaml
    python3 workflow_engine.py ci-pipeline.yaml --dry-run
    python3 workflow_engine.py deploy.yaml --var ENVIRONMENT=staging
    python3 workflow_engine.py build.yaml --step 3 --parallel
"""

import os
import sys
import json
import subprocess
import asyncio
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install PyYAML")
    sys.exit(1)

try:
    from config import MYWORK_ROOT, PROJECTS_DIR
except ImportError:
    def _get_mywork_root() -> Path:
        if env_root := os.environ.get("MYWORK_ROOT"):
            return Path(env_root)
        script_dir = Path(__file__).resolve().parent
        if script_dir.name == "tools":
            potential_root = script_dir.parent
            if (potential_root / "CLAUDE.md").exists():
                return potential_root
        return Path.home() / "MyWork"
    
    MYWORK_ROOT = _get_mywork_root()
    PROJECTS_DIR = MYWORK_ROOT / "projects"

class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"

def color(text: str, color_code: str) -> str:
    """Apply color to text."""
    return f"{color_code}{text}{Colors.ENDC}"

class WorkflowStep:
    """Represents a single workflow step."""
    
    def __init__(self, data: Dict[str, Any], step_index: int):
        self.index = step_index
        self.name = data.get("name", f"Step {step_index}")
        self.command = data.get("run", "")
        self.working_directory = data.get("working_directory", ".")
        self.condition = data.get("condition", "")
        self.continue_on_error = data.get("continue_on_error", False)
        self.depends_on = data.get("depends_on", [])
        self.timeout = data.get("timeout", 300)  # 5 minutes default
        self.environment = data.get("environment", {})
        
        # Status tracking
        self.status = "pending"  # pending, running, success, failed, skipped
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.output: str = ""
        self.error: str = ""
        self.exit_code: Optional[int] = None
    
    def __str__(self) -> str:
        return f"Step {self.index}: {self.name}"
    
    def get_duration(self) -> float:
        """Get step execution duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

class WorkflowEngine:
    """Execute multi-step workflows."""
    
    def __init__(self):
        self.variables: Dict[str, str] = {}
        self.workflows_dir = MYWORK_ROOT / "workflows"
        self.workflows_dir.mkdir(exist_ok=True)
    
    def load_workflow(self, workflow_path: Path) -> Dict[str, Any]:
        """Load workflow from YAML file."""
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow file not found: {workflow_path}")
        
        try:
            with open(workflow_path, 'r') as f:
                workflow = yaml.safe_load(f)
            
            if not isinstance(workflow, dict):
                raise ValueError("Workflow file must contain a dictionary")
            
            # Validate required fields
            if "steps" not in workflow:
                raise ValueError("Workflow must have 'steps' field")
            
            if not isinstance(workflow["steps"], list):
                raise ValueError("'steps' must be a list")
            
            return workflow
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in workflow file: {e}")
    
    def substitute_variables(self, text: str, variables: Dict[str, str]) -> str:
        """Substitute variables in text using ${VAR} syntax."""
        def replace_var(match):
            var_name = match.group(1)
            return variables.get(var_name, match.group(0))
        
        return re.sub(r'\$\{([^}]+)\}', replace_var, text)
    
    def evaluate_condition(self, condition: str, variables: Dict[str, str]) -> bool:
        """Evaluate a simple condition expression."""
        if not condition.strip():
            return True
        
        # Substitute variables
        condition = self.substitute_variables(condition, variables)
        
        # Simple condition evaluation (extend as needed)
        # Supports: ==, !=, contains
        if "==" in condition:
            left, right = [part.strip().strip('"\'') for part in condition.split("==", 1)]
            return left == right
        elif "!=" in condition:
            left, right = [part.strip().strip('"\'') for part in condition.split("!=", 1)]
            return left != right
        elif "contains" in condition:
            parts = condition.split("contains")
            if len(parts) == 2:
                left = parts[0].strip().strip('"\'')
                right = parts[1].strip().strip('"\'')
                return right in left
        
        # If we can't parse it, assume true
        return True
    
    def build_dependency_graph(self, steps: List[WorkflowStep]) -> Dict[int, List[int]]:
        """Build dependency graph for parallel execution."""
        graph = {i: [] for i in range(len(steps))}
        name_to_index = {step.name: step.index for step in steps}
        
        for step in steps:
            if step.depends_on:
                for dep_name in step.depends_on:
                    if dep_name in name_to_index:
                        dep_index = name_to_index[dep_name]
                        graph[step.index].append(dep_index)
        
        return graph
    
    def topological_sort(self, steps: List[WorkflowStep]) -> List[List[int]]:
        """Return steps grouped by execution level for parallel execution."""
        graph = self.build_dependency_graph(steps)
        
        # Calculate in-degree for each step
        in_degree = {i: 0 for i in range(len(steps))}
        for step_idx in graph:
            for dep_idx in graph[step_idx]:
                in_degree[step_idx] += 1
        
        levels = []
        remaining = set(range(len(steps)))
        
        while remaining:
            # Find all steps with no dependencies
            current_level = [idx for idx in remaining if in_degree[idx] == 0]
            
            if not current_level:
                # Circular dependency detected
                raise ValueError("Circular dependency detected in workflow steps")
            
            levels.append(current_level)
            remaining -= set(current_level)
            
            # Remove processed steps from in-degree calculation
            for completed_idx in current_level:
                for step_idx in remaining:
                    if completed_idx in graph[step_idx]:
                        in_degree[step_idx] -= 1
        
        return levels
    
    def execute_step(self, step: WorkflowStep, variables: Dict[str, str], 
                    dry_run: bool = False) -> bool:
        """Execute a single workflow step."""
        print(f"{'🔍' if dry_run else '▶️'} {color(step.name, Colors.BOLD)}")
        
        # Check condition
        if step.condition and not self.evaluate_condition(step.condition, variables):
            step.status = "skipped"
            print(f"   ⏭️  Skipped (condition: {step.condition})")
            return True
        
        # Substitute variables in command
        command = self.substitute_variables(step.command, variables)
        
        if dry_run:
            print(f"   📝 Would run: {color(command, Colors.BLUE)}")
            print(f"   📁 Working directory: {step.working_directory}")
            step.status = "success"  # Assume success for dry run
            return True
        
        step.status = "running"
        step.start_time = datetime.now()
        
        print(f"   📝 Command: {color(command, Colors.BLUE)}")
        print(f"   📁 Working directory: {step.working_directory}")
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(step.environment)
            env.update(variables)
            
            # Execute command
            process = subprocess.run(
                command,
                shell=True,
                cwd=step.working_directory,
                capture_output=True,
                text=True,
                timeout=step.timeout,
                env=env
            )
            
            step.end_time = datetime.now()
            step.exit_code = process.returncode
            step.output = process.stdout
            step.error = process.stderr
            
            if process.returncode == 0:
                step.status = "success"
                duration = step.get_duration()
                print(f"   ✅ Success ({duration:.1f}s)")
                if step.output.strip():
                    # Show first few lines of output
                    output_lines = step.output.strip().split('\n')[:3]
                    for line in output_lines:
                        print(f"      {line}")
                    if len(step.output.strip().split('\n')) > 3:
                        print(f"      ... (output truncated)")
                return True
            else:
                step.status = "failed"
                duration = step.get_duration()
                print(f"   ❌ Failed (exit code: {process.returncode}, {duration:.1f}s)")
                if step.error.strip():
                    error_lines = step.error.strip().split('\n')[:3]
                    for line in error_lines:
                        print(f"      {color(line, Colors.RED)}")
                    if len(step.error.strip().split('\n')) > 3:
                        print(f"      ... (error output truncated)")
                
                if step.continue_on_error:
                    print(f"   ⚠️  Continuing despite error")
                    return True
                return False
        
        except subprocess.TimeoutExpired:
            step.end_time = datetime.now()
            step.status = "failed"
            step.error = f"Command timed out after {step.timeout} seconds"
            print(f"   ⏰ Timeout after {step.timeout}s")
            return not step.continue_on_error
        
        except Exception as e:
            step.end_time = datetime.now()
            step.status = "failed"
            step.error = str(e)
            print(f"   ❌ Error: {e}")
            return not step.continue_on_error
    
    def execute_workflow(self, workflow_path: Path, dry_run: bool = False, 
                        start_step: int = 1, stop_on_error: bool = True,
                        parallel: bool = False, custom_vars: Dict[str, str] = None) -> bool:
        """Execute a complete workflow."""
        
        print(f"{color('🚀 Workflow Engine', Colors.BOLD)}")
        print(f"   Workflow: {workflow_path}")
        
        try:
            # Load workflow
            workflow_data = self.load_workflow(workflow_path)
            
            # Setup variables
            variables = {
                "MYWORK_ROOT": str(MYWORK_ROOT),
                "PROJECTS_DIR": str(PROJECTS_DIR),
                "WORKFLOW_DIR": str(workflow_path.parent),
                "TIMESTAMP": datetime.now().isoformat(),
                **workflow_data.get("variables", {}),
                **(custom_vars or {})
            }
            
            # Create workflow steps
            steps = []
            for i, step_data in enumerate(workflow_data["steps"]):
                if i + 1 >= start_step:  # Skip steps before start_step
                    step = WorkflowStep(step_data, i)
                    steps.append(step)
            
            if not steps:
                print(f"   ⚠️  No steps to execute")
                return True
            
            print(f"   Steps: {len(steps)}")
            print(f"   Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
            if parallel:
                print(f"   Execution: Parallel where possible")
            
            workflow_name = workflow_data.get("name", "Unnamed Workflow")
            workflow_desc = workflow_data.get("description", "")
            
            print(f"\n{color(f'📋 {workflow_name}', Colors.HEADER)}")
            if workflow_desc:
                print(f"   {workflow_desc}")
            
            # Show variables
            if variables:
                print(f"\n{color('🔧 Variables:', Colors.BOLD)}")
                for key, value in list(variables.items())[:5]:  # Show first 5
                    print(f"   {key} = {value}")
                if len(variables) > 5:
                    print(f"   ... and {len(variables) - 5} more")
            
            print(f"\n{color('▶️ Executing Steps:', Colors.BOLD)}")
            
            success = True
            
            if parallel:
                # Execute steps in parallel groups
                execution_levels = self.topological_sort(steps)
                
                for level_idx, step_indices in enumerate(execution_levels):
                    level_steps = [steps[i] for i in step_indices]
                    print(f"\n   🔄 Level {level_idx + 1}: {len(level_steps)} step(s)")
                    
                    if len(level_steps) == 1:
                        # Single step, execute normally
                        step_success = self.execute_step(level_steps[0], variables, dry_run)
                        if not step_success and stop_on_error:
                            success = False
                            break
                    else:
                        # Multiple steps, execute in parallel
                        with ThreadPoolExecutor(max_workers=min(len(level_steps), 4)) as executor:
                            futures = {
                                executor.submit(self.execute_step, step, variables, dry_run): step 
                                for step in level_steps
                            }
                            
                            level_success = True
                            for future in as_completed(futures):
                                step = futures[future]
                                try:
                                    step_success = future.result()
                                    if not step_success:
                                        level_success = False
                                except Exception as e:
                                    print(f"   ❌ Step '{step.name}' failed with exception: {e}")
                                    level_success = False
                            
                            if not level_success and stop_on_error:
                                success = False
                                break
            else:
                # Sequential execution
                for step in steps:
                    step_success = self.execute_step(step, variables, dry_run)
                    
                    if not step_success and stop_on_error:
                        success = False
                        break
                    elif not step_success:
                        success = False  # Mark overall as failed but continue
            
            # Summary
            print(f"\n{color('📊 Workflow Summary:', Colors.BOLD)}")
            
            total_steps = len(steps)
            successful_steps = len([s for s in steps if s.status == "success"])
            failed_steps = len([s for s in steps if s.status == "failed"])
            skipped_steps = len([s for s in steps if s.status == "skipped"])
            
            print(f"   Total steps: {total_steps}")
            print(f"   Successful: {color(str(successful_steps), Colors.GREEN)}")
            if failed_steps > 0:
                print(f"   Failed: {color(str(failed_steps), Colors.RED)}")
            if skipped_steps > 0:
                print(f"   Skipped: {color(str(skipped_steps), Colors.YELLOW)}")
            
            # Calculate total duration
            total_duration = sum(step.get_duration() for step in steps if step.start_time and step.end_time)
            if total_duration > 0:
                print(f"   Duration: {total_duration:.1f}s")
            
            if success:
                print(f"\n{color('🎉 Workflow completed successfully!', Colors.GREEN)}")
            else:
                print(f"\n{color('❌ Workflow failed!', Colors.RED)}")
            
            # Save execution report
            self.save_execution_report(workflow_path, steps, variables, success, dry_run)
            
            return success
            
        except Exception as e:
            print(f"{color('❌ Workflow execution failed:', Colors.RED)} {e}")
            return False
    
    def save_execution_report(self, workflow_path: Path, steps: List[WorkflowStep], 
                             variables: Dict[str, str], success: bool, dry_run: bool) -> None:
        """Save workflow execution report."""
        reports_dir = MYWORK_ROOT / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"workflow_{workflow_path.stem}_{timestamp}.json"
        
        report = {
            "workflow_file": str(workflow_path),
            "execution_time": datetime.now().isoformat(),
            "success": success,
            "dry_run": dry_run,
            "variables": variables,
            "steps": []
        }
        
        for step in steps:
            step_report = {
                "index": step.index,
                "name": step.name,
                "command": step.command,
                "status": step.status,
                "start_time": step.start_time.isoformat() if step.start_time else None,
                "end_time": step.end_time.isoformat() if step.end_time else None,
                "duration_seconds": step.get_duration(),
                "exit_code": step.exit_code,
                "output": step.output,
                "error": step.error
            }
            report["steps"].append(step_report)
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"   📄 Report saved: {report_file}")
        except Exception:
            pass
    
    def list_workflows(self) -> None:
        """List available workflows."""
        print(f"{color('📋 Available Workflows:', Colors.BOLD)}")
        
        # Look in workflows directory
        workflow_files = list(self.workflows_dir.glob("*.yaml")) + list(self.workflows_dir.glob("*.yml"))
        
        if not workflow_files:
            print(f"   No workflows found in {self.workflows_dir}")
            print(f"   Create workflow files with .yaml or .yml extension")
            return
        
        for workflow_file in sorted(workflow_files):
            try:
                workflow_data = self.load_workflow(workflow_file)
                name = workflow_data.get("name", workflow_file.stem)
                description = workflow_data.get("description", "No description")
                step_count = len(workflow_data.get("steps", []))
                
                print(f"   📄 {color(workflow_file.name, Colors.BOLD)}")
                print(f"      Name: {name}")
                print(f"      Steps: {step_count}")
                print(f"      Description: {description}")
                print()
                
            except Exception as e:
                print(f"   ❌ {workflow_file.name}: Error loading ({e})")

def create_sample_workflows():
    """Create sample workflow files."""
    workflows_dir = MYWORK_ROOT / "workflows"
    workflows_dir.mkdir(exist_ok=True)
    
    # Sample CI/CD workflow
    ci_workflow = {
        "name": "CI/CD Pipeline",
        "description": "Continuous Integration and Deployment pipeline",
        "variables": {
            "PROJECT_NAME": "my-app",
            "ENVIRONMENT": "production"
        },
        "steps": [
            {
                "name": "Lint Code",
                "run": "mw lint scan",
                "continue_on_error": False
            },
            {
                "name": "Run Tests",
                "run": "mw test",
                "depends_on": []
            },
            {
                "name": "Build Application",
                "run": "mw build",
                "depends_on": ["Lint Code", "Run Tests"]
            },
            {
                "name": "Deploy to ${ENVIRONMENT}",
                "run": "mw deploy --env ${ENVIRONMENT}",
                "depends_on": ["Build Application"],
                "condition": "${ENVIRONMENT} == 'production'"
            }
        ]
    }
    
    # Sample development workflow
    dev_workflow = {
        "name": "Development Workflow",
        "description": "Daily development tasks",
        "variables": {
            "PROJECT_DIR": "."
        },
        "steps": [
            {
                "name": "Update Dependencies",
                "run": "mw deps update",
                "continue_on_error": True
            },
            {
                "name": "Run Linting",
                "run": "mw lint scan --fix",
                "working_directory": "${PROJECT_DIR}"
            },
            {
                "name": "Run Quick Tests",
                "run": "mw test --quick",
                "depends_on": ["Run Linting"]
            },
            {
                "name": "Check Security",
                "run": "mw security scan",
                "continue_on_error": True
            }
        ]
    }
    
    # Write sample files if they don't exist
    ci_file = workflows_dir / "ci-pipeline.yaml"
    if not ci_file.exists():
        with open(ci_file, 'w') as f:
            yaml.dump(ci_workflow, f, default_flow_style=False)
        print(f"Created sample workflow: {ci_file}")
    
    dev_file = workflows_dir / "development.yaml"
    if not dev_file.exists():
        with open(dev_file, 'w') as f:
            yaml.dump(dev_workflow, f, default_flow_style=False)
        print(f"Created sample workflow: {dev_file}")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Execute multi-step workflows defined in YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("workflow", nargs="?", help="Workflow YAML file to execute")
    parser.add_argument("--list", action="store_true", help="List available workflows")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be executed without running")
    parser.add_argument("--step", type=int, default=1, help="Start from step number n")
    parser.add_argument("--stop-on-error", action="store_true", help="Stop execution on first error")
    parser.add_argument("--parallel", action="store_true", help="Run independent steps in parallel")
    parser.add_argument("--vars", help="Load variables from JSON file")
    parser.add_argument("--var", action="append", default=[], help="Set variable key=value")
    parser.add_argument("--create-samples", action="store_true", help="Create sample workflow files")
    
    args = parser.parse_args()
    
    engine = WorkflowEngine()
    
    if args.create_samples:
        create_sample_workflows()
        return 0
    
    if args.list:
        engine.list_workflows()
        return 0
    
    if not args.workflow:
        parser.print_help()
        return 1
    
    # Load custom variables
    custom_vars = {}
    
    if args.vars:
        vars_file = Path(args.vars)
        if vars_file.exists():
            try:
                with open(vars_file, 'r') as f:
                    custom_vars.update(json.load(f))
            except Exception as e:
                print(f"Error loading variables file: {e}")
                return 1
    
    # Parse --var arguments
    for var_assignment in args.var:
        if '=' in var_assignment:
            key, value = var_assignment.split('=', 1)
            custom_vars[key] = value
        else:
            print(f"Invalid variable format: {var_assignment} (use key=value)")
            return 1
    
    # Resolve workflow path
    workflow_path = Path(args.workflow)
    if not workflow_path.exists():
        # Try in workflows directory
        workflows_dir = MYWORK_ROOT / "workflows"
        workflow_path = workflows_dir / args.workflow
        
        if not workflow_path.exists():
            # Try adding .yaml extension
            workflow_path = workflows_dir / f"{args.workflow}.yaml"
            
            if not workflow_path.exists():
                print(f"Workflow file not found: {args.workflow}")
                return 1
    
    # Execute workflow
    success = engine.execute_workflow(
        workflow_path,
        dry_run=args.dry_run,
        start_step=args.step,
        stop_on_error=args.stop_on_error,
        parallel=args.parallel,
        custom_vars=custom_vars
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
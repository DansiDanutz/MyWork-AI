#!/usr/bin/env python3
"""
Tests for the scaffold.py project creation tool.

Tests template generation, project validation, and file structure creation.
"""

import pytest
import tempfile
import sys
from pathlib import Path
import os

# Add tools directory to path for imports
tools_dir = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(tools_dir))

from scaffold import create_project, list_templates, TEMPLATES, create_structure


class TestScaffoldTemplates:
    """Test scaffold template generation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.projects_dir = Path(self.temp_dir) / "projects"
        self.projects_dir.mkdir(parents=True)
        
        # Mock PROJECTS_DIR for testing
        import scaffold
        self.original_projects_dir = scaffold.PROJECTS_DIR
        scaffold.PROJECTS_DIR = self.projects_dir
        
    def teardown_method(self):
        """Clean up test environment."""
        import scaffold
        scaffold.PROJECTS_DIR = self.original_projects_dir
        
    def test_basic_template_generates_correct_files(self):
        """Test basic template creates the expected file structure."""
        project_name = "test-basic"
        
        success = create_project(project_name, "basic")
        assert success, "Project creation should succeed"
        
        project_path = self.projects_dir / project_name
        assert project_path.exists(), "Project directory should be created"
        
        # Check required files exist
        expected_files = [
            "README.md",
            ".gitignore", 
            ".planning/PROJECT.md",
            ".planning/ROADMAP.md",
            ".planning/STATE.md"
        ]
        
        for file_path in expected_files:
            full_path = project_path / file_path
            assert full_path.exists(), f"File {file_path} should exist"
            assert full_path.stat().st_size > 0, f"File {file_path} should not be empty"
            
        # Check content substitution
        readme_content = (project_path / "README.md").read_text()
        assert project_name in readme_content, "Project name should be in README"
        
    def test_fastapi_template_generates_correct_files(self):
        """Test FastAPI template creates backend structure."""
        project_name = "test-fastapi"
        
        success = create_project(project_name, "fastapi")
        assert success, "FastAPI project creation should succeed"
        
        project_path = self.projects_dir / project_name
        
        # Check FastAPI specific files
        expected_files = [
            "backend/main.py",
            "backend/database/db.py", 
            "backend/database/models.py",
            "backend/requirements.txt",
            ".planning/PROJECT.md"
        ]
        
        for file_path in expected_files:
            full_path = project_path / file_path
            assert full_path.exists(), f"FastAPI file {file_path} should exist"
            
        # Check FastAPI content
        main_py = (project_path / "backend/main.py").read_text()
        assert "FastAPI" in main_py, "main.py should contain FastAPI imports"
        assert project_name in main_py, "main.py should contain project name"
        
    def test_nextjs_template_generates_correct_files(self):
        """Test Next.js template creates frontend structure."""
        project_name = "test-nextjs"
        
        success = create_project(project_name, "nextjs")
        assert success, "Next.js project creation should succeed"
        
        project_path = self.projects_dir / project_name
        
        # Check Next.js specific files
        expected_files = [
            "frontend/package.json",
            "frontend/tsconfig.json",
            "frontend/app/page.tsx",
            "frontend/tailwind.config.js"
        ]
        
        for file_path in expected_files:
            full_path = project_path / file_path
            assert full_path.exists(), f"Next.js file {file_path} should exist"
            
        # Check package.json content
        package_json_path = project_path / "frontend/package.json"
        package_content = package_json_path.read_text()
        assert "next" in package_content, "package.json should contain Next.js dependency"
        # name_lower converts hyphens to underscores
        name_lower = project_name.replace("-", "_")
        assert name_lower in package_content, "package.json should contain project name"
        
    def test_fullstack_template_generates_both_stacks(self):
        """Test fullstack template creates both backend and frontend."""
        project_name = "test-fullstack"
        
        success = create_project(project_name, "fullstack")
        assert success, "Fullstack project creation should succeed"
        
        project_path = self.projects_dir / project_name
        
        # Check both backend and frontend exist
        backend_files = [
            "backend/main.py",
            "backend/database/db.py"
        ]
        
        frontend_files = [
            "frontend/package.json", 
            "frontend/app/page.tsx"
        ]
        
        for file_path in backend_files + frontend_files:
            full_path = project_path / file_path
            assert full_path.exists(), f"Fullstack file {file_path} should exist"
            
    def test_cli_template_generates_cli_structure(self):
        """Test CLI template creates Python CLI structure.""" 
        project_name = "test-cli"
        
        success = create_project(project_name, "cli")
        assert success, "CLI project creation should succeed"
        
        project_path = self.projects_dir / project_name
        
        # Check CLI specific files
        expected_files = [
            "src/__init__.py",
            "src/cli.py",
            "requirements.txt",
            "setup.py"
        ]
        
        for file_path in expected_files:
            full_path = project_path / file_path
            assert full_path.exists(), f"CLI file {file_path} should exist"
            
    def test_invalid_template_name_raises_error(self):
        """Test that invalid template names are handled properly."""
        project_name = "test-invalid"
        
        success = create_project(project_name, "nonexistent-template")
        assert not success, "Invalid template should fail"
        
        # Project should not be created
        project_path = self.projects_dir / project_name
        assert not project_path.exists(), "Project should not be created with invalid template"


class TestProjectNameValidation:
    """Test project name validation rules."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.projects_dir = Path(self.temp_dir) / "projects"
        self.projects_dir.mkdir(parents=True)
        
        # Mock PROJECTS_DIR
        import scaffold
        self.original_projects_dir = scaffold.PROJECTS_DIR
        scaffold.PROJECTS_DIR = self.projects_dir
        
    def teardown_method(self):
        """Clean up test environment."""
        import scaffold
        scaffold.PROJECTS_DIR = self.original_projects_dir
        
    def test_valid_project_names(self):
        """Test that valid project names are accepted."""
        valid_names = [
            "my-app",
            "api-server",
            "todo-list", 
            "app123",
            "test",
            "a",
            "project-v2"
        ]
        
        for name in valid_names:
            success = create_project(name, "basic")
            assert success, f"Valid project name '{name}' should be accepted"
            
            project_path = self.projects_dir / name
            assert project_path.exists(), f"Project '{name}' should be created"
            
    def test_invalid_project_names(self):
        """Test that invalid project names are rejected."""
        invalid_names = [
            "My App",           # spaces
            "my_app",           # underscores
            "my.app",           # dots
            "MyApp",            # uppercase
            "-myapp",           # starts with hyphen
            "myapp-",           # ends with hyphen
            "my--app",          # double hyphens
            "",                 # empty
            "app@example",      # special chars
            "123",              # numbers only
        ]
        
        for name in invalid_names:
            success = create_project(name, "basic")
            assert not success, f"Invalid project name '{name}' should be rejected"
            
            if name:  # Skip empty string check
                project_path = self.projects_dir / name
                assert not project_path.exists(), f"Project '{name}' should not be created"
                
    def test_existing_project_name_rejected(self):
        """Test that existing project names are rejected."""
        project_name = "existing-project"
        
        # Create project first time
        success1 = create_project(project_name, "basic")
        assert success1, "First project creation should succeed"
        
        # Try to create again 
        success2 = create_project(project_name, "basic")
        assert not success2, "Duplicate project name should be rejected"


class TestCreateStructureFunction:
    """Test the create_structure helper function."""
    
    def test_creates_nested_directories(self):
        """Test creating nested directory structures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            
            structure = {
                "dir1": {
                    "subdir": {
                        "file.txt": "content"
                    },
                    "file1.txt": "content1"
                },
                "file2.txt": "content2"
            }
            
            create_structure(base_path, structure, {})
            
            # Check directories exist
            assert (base_path / "dir1").is_dir()
            assert (base_path / "dir1" / "subdir").is_dir() 
            
            # Check files exist with content
            assert (base_path / "dir1" / "subdir" / "file.txt").read_text() == "content"
            assert (base_path / "dir1" / "file1.txt").read_text() == "content1"
            assert (base_path / "file2.txt").read_text() == "content2"
            
    def test_template_substitution(self):
        """Test template variable substitution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            
            structure = {
                "README.md": "# {name}\n\nCreated on {date}"
            }
            
            context = {
                "name": "test-project",
                "date": "2024-01-01"
            }
            
            create_structure(base_path, structure, context)
            
            content = (base_path / "README.md").read_text()
            assert "# test-project" in content
            assert "Created on 2024-01-01" in content
            
    def test_handles_literal_braces(self):
        """Test that literal braces in templates are preserved."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            
            # Content with literal braces (like JSON or code)
            structure = {
                "config.json": '{"key": "value", "array": [1, 2, 3]}'
            }
            
            create_structure(base_path, structure, {"name": "test"})
            
            content = (base_path / "config.json").read_text()
            assert '{"key": "value", "array": [1, 2, 3]}' == content


class TestListTemplates:
    """Test template listing functionality."""
    
    def test_list_templates_shows_all_templates(self, capsys):
        """Test that list_templates shows all available templates."""
        list_templates()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Should show header
        assert "Available Templates" in output
        
        # Should show all template names
        for template_name in TEMPLATES.keys():
            assert template_name in output
            
        # Should show descriptions
        for template_data in TEMPLATES.values():
            assert template_data["description"] in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
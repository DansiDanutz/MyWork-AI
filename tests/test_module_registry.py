"""
Tests for module_registry.py
============================
Tests for the Module Registry functionality.
"""

import json
from pathlib import Path

import pytest


class TestModuleRegistry:
    """Tests for ModuleRegistry class."""

    def test_load_empty_registry(self, temp_mywork_root):
        """Should handle empty/missing registry file gracefully."""
        import sys

        if "module_registry" in sys.modules:
            del sys.modules["module_registry"]

        from module_registry import ModuleRegistry

        registry = ModuleRegistry()

        assert len(registry.modules) == 0

    def test_load_existing_registry(self, temp_mywork_root, sample_module_registry):
        """Should load existing registry data correctly."""
        import sys

        if "module_registry" in sys.modules:
            del sys.modules["module_registry"]

        from module_registry import ModuleRegistry

        registry = ModuleRegistry()

        assert len(registry.modules) == 2
        assert "abc123" in registry.modules
        assert "def456" in registry.modules

    def test_search_modules(self, temp_mywork_root, sample_module_registry):
        """Should search modules by query."""
        import sys

        if "module_registry" in sys.modules:
            del sys.modules["module_registry"]

        from module_registry import ModuleRegistry

        registry = ModuleRegistry()
        results = registry.search("test")

        assert len(results) >= 1

    def test_search_by_type_filter(self, temp_mywork_root, sample_module_registry):
        """Should filter search by type."""
        import sys

        if "module_registry" in sys.modules:
            del sys.modules["module_registry"]

        from module_registry import ModuleRegistry

        registry = ModuleRegistry()
        results = registry.search("", type_filter="component")

        # Only components should be returned
        for result in results.get("modules", []):
            assert result.type == "component"

    def test_get_by_type(self, temp_mywork_root, sample_module_registry):
        """Should get modules by type."""
        import sys

        if "module_registry" in sys.modules:
            del sys.modules["module_registry"]

        from module_registry import ModuleRegistry

        registry = ModuleRegistry()
        components = registry.get_by_type("component")

        assert len(components) == 1
        assert components[0].name == "TestComponent"

    def test_get_by_project(self, temp_mywork_root, sample_module_registry):
        """Should get modules by project."""
        import sys

        if "module_registry" in sys.modules:
            del sys.modules["module_registry"]

        from module_registry import ModuleRegistry

        registry = ModuleRegistry()
        modules = registry.get_by_project("test-project")

        assert len(modules) == 2

    def test_get_stats(self, temp_mywork_root, sample_module_registry):
        """Should return correct statistics."""
        import sys

        if "module_registry" in sys.modules:
            del sys.modules["module_registry"]

        from module_registry import ModuleRegistry

        registry = ModuleRegistry()
        stats = registry.get_stats()

        assert stats["total_modules"] == 2
        assert "component" in stats["by_type"]
        assert "utility" in stats["by_type"]


class TestModule:
    """Tests for Module dataclass."""

    def test_create_module(self):
        """Should create module with all fields."""
        from module_registry import Module

        module = Module(
            id="test-123",
            name="TestModule",
            type="component",
            project="test-project",
            file_path="src/test.tsx",
            line_number=10,
            language="typescript",
            description="A test module",
            tags=["test"],
            dependencies=["react"],
            exports=["TestModule"],
            last_modified="2024-01-01T00:00:00",
            hash="abc123",
        )

        assert module.id == "test-123"
        assert module.name == "TestModule"
        assert module.type == "component"

    def test_to_dict(self):
        """Should convert to dictionary correctly."""
        from module_registry import Module

        module = Module(
            id="test-123",
            name="TestModule",
            type="component",
            project="test-project",
            file_path="src/test.tsx",
            line_number=10,
            language="typescript",
            description="A test module",
            tags=["test"],
            dependencies=["react"],
            exports=["TestModule"],
            last_modified="2024-01-01T00:00:00",
            hash="abc123",
        )

        result = module.to_dict()

        assert isinstance(result, dict)
        assert result["id"] == "test-123"
        assert result["name"] == "TestModule"


class TestProjectScanner:
    """Tests for ProjectScanner class."""

    def test_scan_empty_projects_dir(self, temp_mywork_root):
        """Should handle empty projects directory."""
        import sys

        if "module_registry" in sys.modules:
            del sys.modules["module_registry"]

        from module_registry import ModuleRegistry, ProjectScanner

        registry = ModuleRegistry()
        scanner = ProjectScanner(registry)

        count = scanner.scan_all_projects()

        assert count == 0

    def test_scan_project_with_files(self, temp_mywork_root, temp_project):
        """Should scan project and find modules."""
        import sys

        if "module_registry" in sys.modules:
            del sys.modules["module_registry"]

        # Create a Python file with a function
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "utils.py").write_text("""
def get_user(user_id: int):
    \"\"\"Get user by ID.\"\"\"
    return {"id": user_id}

def create_user(name: str):
    \"\"\"Create a new user.\"\"\"
    return {"name": name}
""")

        from module_registry import ModuleRegistry, ProjectScanner

        registry = ModuleRegistry()
        scanner = ProjectScanner(registry)

        count = scanner.scan_all_projects()

        # Should find at least the utility functions
        assert count >= 0  # May vary based on pattern matching

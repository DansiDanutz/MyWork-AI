"""
Tests for config.py
====================
Tests for the shared configuration module.
"""

import os
from pathlib import Path

import pytest


class TestGetMyworkRoot:
    """Tests for get_mywork_root function."""

    def test_uses_environment_variable(self, temp_mywork_root):
        """Should use MYWORK_ROOT environment variable when set."""
        from config import get_mywork_root

        os.environ["MYWORK_ROOT"] = str(temp_mywork_root)
        result = get_mywork_root()

        assert result == temp_mywork_root

    def test_detects_from_script_location(self, tmp_path):
        """Should detect root from script location when env not set."""
        # This test verifies the fallback mechanism
        old_root = os.environ.pop("MYWORK_ROOT", None)

        try:
            from config import get_mywork_root

            result = get_mywork_root()

            # Should return a valid Path
            assert isinstance(result, Path)
        finally:
            if old_root:
                os.environ["MYWORK_ROOT"] = old_root


class TestPathConstants:
    """Tests for path constant definitions."""

    def test_tools_dir_exists(self, temp_mywork_root):
        """TOOLS_DIR should be a valid path."""
        # Force reimport with new MYWORK_ROOT
        import importlib
        import config

        importlib.reload(config)

        assert config.TOOLS_DIR == temp_mywork_root / "tools"

    def test_projects_dir_constant(self, temp_mywork_root):
        """PROJECTS_DIR should be correct."""
        import importlib
        import config

        importlib.reload(config)

        assert config.PROJECTS_DIR == temp_mywork_root / "projects"

    def test_planning_dir_constant(self, temp_mywork_root):
        """PLANNING_DIR should be correct."""
        import importlib
        import config

        importlib.reload(config)

        assert config.PLANNING_DIR == temp_mywork_root / ".planning"


class TestEnsureDirectories:
    """Tests for ensure_directories function."""

    def test_creates_required_directories(self, temp_mywork_root):
        """Should create all required directories."""
        import importlib
        import config

        importlib.reload(config)

        # Remove directories to test creation
        import shutil

        shutil.rmtree(temp_mywork_root / "projects", ignore_errors=True)
        shutil.rmtree(temp_mywork_root / ".planning", ignore_errors=True)
        shutil.rmtree(temp_mywork_root / ".tmp", ignore_errors=True)

        config.ensure_directories()

        assert (temp_mywork_root / "projects").exists()
        assert (temp_mywork_root / ".planning").exists()
        assert (temp_mywork_root / ".tmp").exists()


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_project_path(self, temp_mywork_root):
        """Should return correct project path."""
        import importlib
        import config

        importlib.reload(config)

        result = config.get_project_path("my-project")

        assert result == temp_mywork_root / "projects" / "my-project"

    def test_list_projects_empty(self, temp_mywork_root):
        """Should return empty list when no projects exist."""
        import importlib
        import config

        importlib.reload(config)

        result = config.list_projects()

        assert result == []

    def test_list_projects_with_projects(self, temp_mywork_root, temp_project):
        """Should return list of project paths."""
        import importlib
        import config

        importlib.reload(config)

        result = config.list_projects()

        assert len(result) == 1
        assert result[0].name == "test-project"

    def test_list_projects_excludes_hidden(self, temp_mywork_root):
        """Should exclude hidden and template directories."""
        import importlib
        import config

        importlib.reload(config)

        # Create hidden and template directories
        (temp_mywork_root / "projects" / ".hidden").mkdir()
        (temp_mywork_root / "projects" / "_template").mkdir()
        (temp_mywork_root / "projects" / "real-project").mkdir()

        result = config.list_projects()

        assert len(result) == 1
        assert result[0].name == "real-project"

"""
Pytest Configuration and Fixtures
==================================
Shared fixtures and configuration for all tests.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add tools directory to path for imports
TOOLS_DIR = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))


@pytest.fixture
def temp_mywork_root(tmp_path):
    """Create a temporary MyWork root directory for testing."""
    # Set up directory structure
    (tmp_path / ".planning").mkdir()
    (tmp_path / ".tmp").mkdir()
    (tmp_path / "projects").mkdir()
    (tmp_path / "tools").mkdir()
    (tmp_path / "workflows").mkdir()

    # Create CLAUDE.md marker file
    (tmp_path / "CLAUDE.md").write_text("# Test MyWork Root")

    # Set environment variable
    old_root = os.environ.get("MYWORK_ROOT")
    os.environ["MYWORK_ROOT"] = str(tmp_path)

    yield tmp_path

    # Restore original
    if old_root:
        os.environ["MYWORK_ROOT"] = old_root
    else:
        os.environ.pop("MYWORK_ROOT", None)


@pytest.fixture
def temp_project(temp_mywork_root):
    """Create a temporary project for testing."""
    project_path = temp_mywork_root / "projects" / "test-project"
    project_path.mkdir(parents=True)

    # Create project structure
    (project_path / ".planning").mkdir()
    (project_path / ".planning" / "PROJECT.md").write_text("# Test Project")
    (project_path / ".planning" / "ROADMAP.md").write_text("# Roadmap")
    (project_path / ".planning" / "STATE.md").write_text("# State")

    return project_path


@pytest.fixture
def sample_brain_data(temp_mywork_root):
    """Create sample brain data for testing."""
    import json
    from datetime import datetime

    brain_data = {
        "version": "1.0",
        "entries": [
            {
                "id": "test-001",
                "type": "pattern",
                "content": "Test pattern for unit tests",
                "context": "Testing",
                "status": "TESTED",
                "tags": ["test", "pattern"],
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "references": 0,
            },
            {
                "id": "test-002",
                "type": "lesson",
                "content": "Always write tests first",
                "context": "Development",
                "status": "EXPERIMENTAL",
                "tags": ["test", "tdd"],
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "references": 0,
            },
        ],
    }

    brain_file = temp_mywork_root / ".planning" / "brain_data.json"
    brain_file.write_text(json.dumps(brain_data, indent=2))

    return brain_file


@pytest.fixture
def sample_module_registry(temp_mywork_root):
    """Create sample module registry for testing."""
    import json
    from datetime import datetime

    registry_data = {
        "version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "module_count": 2,
        "modules": [
            {
                "id": "abc123",
                "name": "TestComponent",
                "type": "component",
                "project": "test-project",
                "file_path": "src/components/TestComponent.tsx",
                "line_number": 1,
                "language": "typescript",
                "description": "A test component",
                "tags": ["test", "component"],
                "dependencies": ["react"],
                "exports": ["TestComponent"],
                "last_modified": datetime.now().isoformat(),
                "hash": "abc123",
            },
            {
                "id": "def456",
                "name": "get_user",
                "type": "utility",
                "project": "test-project",
                "file_path": "utils/user.py",
                "line_number": 10,
                "language": "python",
                "description": "Get user by ID",
                "tags": ["utility", "user"],
                "dependencies": ["sqlalchemy"],
                "exports": ["get_user"],
                "last_modified": datetime.now().isoformat(),
                "hash": "def456",
            },
        ],
    }

    registry_file = temp_mywork_root / ".planning" / "module_registry.json"
    registry_file.write_text(json.dumps(registry_data, indent=2))

    return registry_file

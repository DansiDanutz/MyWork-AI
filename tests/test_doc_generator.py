"""Tests for the documentation generator."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from doc_generator import (
    scan_python_module,
    detect_framework,
    scan_api_routes,
    generate_tree,
    generate_readme,
    run_docs,
)


def _make_project(tmp_path):
    """Create a minimal Python project for testing."""
    (tmp_path / "requirements.txt").write_text("fastapi\npytest\n")
    (tmp_path / "main.py").write_text(
        '"""Main application module."""\n\n'
        'from fastapi import FastAPI\n\n'
        'app = FastAPI()\n\n'
        'class UserService:\n'
        '    """Handles user operations."""\n'
        '    def get_user(self, user_id: int):\n'
        '        """Fetch user by ID."""\n'
        '        pass\n\n'
        '@app.get("/health")\n'
        'def health():\n'
        '    """Health check endpoint."""\n'
        '    return {"ok": True}\n\n'
        '@app.post("/users")\n'
        'def create_user():\n'
        '    return {}\n'
    )
    (tmp_path / "utils.py").write_text(
        '"""Utility functions."""\n\n'
        'def format_name(first: str, last: str) -> str:\n'
        '    """Format a full name."""\n'
        '    return f"{first} {last}"\n'
    )
    return tmp_path


def test_scan_python_module(tmp_path):
    proj = _make_project(tmp_path)
    result = scan_python_module(proj / "main.py")
    assert result is not None
    assert result["module_doc"] == "Main application module."
    assert len(result["classes"]) == 1
    assert result["classes"][0]["name"] == "UserService"
    assert len(result["functions"]) >= 1


def test_detect_framework(tmp_path):
    proj = _make_project(tmp_path)
    info = detect_framework(proj)
    assert info["language"] == "python"
    assert info["framework"] == "FastAPI"
    assert "pytest" in info["features"]


def test_detect_framework_node(tmp_path):
    import json
    (tmp_path / "package.json").write_text(json.dumps({
        "dependencies": {"next": "14.0.0", "react": "18.0.0"},
        "devDependencies": {"tailwindcss": "3.0.0"}
    }))
    (tmp_path / "tsconfig.json").write_text("{}")
    info = detect_framework(tmp_path)
    assert info["language"] == "typescript"
    assert info["framework"] == "Next.js"
    assert "Tailwind CSS" in info["features"]


def test_scan_api_routes(tmp_path):
    proj = _make_project(tmp_path)
    routes = scan_api_routes(proj)
    assert len(routes) >= 2
    methods = [r["method"] for r in routes]
    assert "GET" in methods
    assert "POST" in methods


def test_generate_tree(tmp_path):
    proj = _make_project(tmp_path)
    tree = generate_tree(proj, max_depth=1)
    assert "main.py" in tree
    assert "utils.py" in tree


def test_generate_readme(tmp_path):
    proj = _make_project(tmp_path)
    info = detect_framework(proj)
    modules = []
    for f in proj.glob("*.py"):
        r = scan_python_module(f)
        if r:
            modules.append(r)
    routes = scan_api_routes(proj)
    readme = generate_readme(proj, info, modules, routes)
    assert "# " in readme
    assert "Python" in readme
    assert "FastAPI" in readme
    assert "pip install" in readme


def test_run_docs_generate(tmp_path):
    proj = _make_project(tmp_path)
    result = run_docs(["generate", str(proj)])
    assert result == 0
    out = proj / "docs" / "generated"
    assert (out / "README.md").exists()
    assert (out / "MODULES.md").exists()
    assert (out / "ARCHITECTURE.md").exists()


def test_run_docs_stats(tmp_path):
    proj = _make_project(tmp_path)
    result = run_docs(["stats", str(proj)])
    assert result == 0


def test_run_docs_preview(tmp_path):
    proj = _make_project(tmp_path)
    result = run_docs(["preview", str(proj)])
    assert result == 0


def test_run_docs_help():
    result = run_docs(["--help"])
    assert result == 0


def test_scan_empty_file(tmp_path):
    (tmp_path / "empty.py").write_text("")
    result = scan_python_module(tmp_path / "empty.py")
    # Empty file parses but has no meaningful content
    assert result is not None
    assert result["classes"] == []
    assert result["functions"] == []


def test_scan_syntax_error(tmp_path):
    (tmp_path / "bad.py").write_text("def broken(:\n  pass")
    result = scan_python_module(tmp_path / "bad.py")
    assert result is None

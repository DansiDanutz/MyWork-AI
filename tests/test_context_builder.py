"""Tests for mw context — Smart Context Builder."""
import os
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.context_builder import (
    build_tree, build_context, detect_project_type,
    estimate_tokens, _human_size, read_file_content, main,
)


@pytest.fixture
def sample_project(tmp_path):
    """Create a sample project structure."""
    # Create files
    (tmp_path / "README.md").write_text("# My Project\nA test project.")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\ndependencies = ["fastapi"]')
    (tmp_path / "requirements.txt").write_text("fastapi==0.100.0\nuvicorn==0.23.0")
    
    # Create src dir
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("def main():\n    print('hello')\n")
    (src / "utils.py").write_text("def helper():\n    return 42\n")
    (src / "auth.py").write_text("def login(user, pw):\n    pass\n")
    
    # Create tests dir
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_main.py").write_text("def test_main():\n    assert True\n")
    
    # Create node_modules (should be skipped)
    nm = tmp_path / "node_modules"
    nm.mkdir()
    (nm / "junk.js").write_text("junk")
    
    # Git init
    os.system(f"cd {tmp_path} && git init -q && git add -A && git commit -q -m 'init' 2>/dev/null")
    
    return tmp_path


def test_estimate_tokens():
    assert estimate_tokens("") == 0
    assert estimate_tokens("hello world") > 0
    assert estimate_tokens("a" * 400) == 100


def test_human_size():
    assert _human_size(500) == "500B"
    assert _human_size(2048) == "2KB"
    assert _human_size(1048576) == "1MB"


def test_build_tree(sample_project):
    tree = build_tree(str(sample_project), max_depth=2)
    assert "src/" in tree
    assert "tests/" in tree
    assert "README.md" in tree
    # node_modules should be skipped
    assert "node_modules" not in tree


def test_build_tree_with_focus(sample_project):
    tree = build_tree(str(sample_project), max_depth=3, focus="auth")
    assert "auth" in tree.lower()


def test_build_tree_depth(sample_project):
    tree_shallow = build_tree(str(sample_project), max_depth=1)
    tree_deep = build_tree(str(sample_project), max_depth=3)
    # Deep tree should have more content
    assert len(tree_deep) >= len(tree_shallow)


def test_detect_project_type_python(sample_project):
    info = detect_project_type(str(sample_project))
    assert info["type"] == "python"
    assert info["language"] == "Python"
    assert info["framework"] == "FastAPI"


def test_detect_project_type_node(tmp_path):
    (tmp_path / "package.json").write_text('{"dependencies": {"next": "^14.0.0"}}')
    info = detect_project_type(str(tmp_path))
    assert info["type"] == "node"
    assert info["framework"] == "Next.js"


def test_detect_project_type_unknown(tmp_path):
    info = detect_project_type(str(tmp_path))
    assert info["type"] == "unknown"


def test_build_context_basic(sample_project):
    ctx = build_context(str(sample_project))
    assert "Project Context" in ctx
    assert "Project Structure" in ctx
    assert "Python" in ctx


def test_build_context_with_files(sample_project):
    ctx = build_context(str(sample_project), files=["src/main.py"])
    assert "Requested Files" in ctx
    assert "def main" in ctx


def test_build_context_with_git(sample_project):
    ctx = build_context(str(sample_project), include_git=True)
    assert "Git History" in ctx or "init" in ctx


def test_build_context_with_deps(sample_project):
    ctx = build_context(str(sample_project), include_deps=True)
    assert "fastapi" in ctx.lower()


def test_build_context_with_focus(sample_project):
    ctx = build_context(str(sample_project), focus="auth")
    assert "auth" in ctx.lower()


def test_build_context_token_limit(sample_project):
    ctx = build_context(str(sample_project), max_tokens=100)
    tokens = estimate_tokens(ctx)
    # Should be roughly limited (with some tolerance for truncation message)
    assert tokens < 200


def test_read_file_content(sample_project):
    content = read_file_content(str(sample_project / "src" / "main.py"))
    assert "def main" in content


def test_read_file_content_max_lines(sample_project):
    # Create a long file
    long_file = sample_project / "long.py"
    long_file.write_text("\n".join(f"line {i}" for i in range(500)))
    content = read_file_content(str(long_file), max_lines=10)
    assert "more lines" in content


def test_read_file_nonexistent():
    content = read_file_content("/nonexistent/file.py")
    assert content == ""


def test_main_help(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_main_invalid_path():
    result = main(["/nonexistent/path/xyz"])
    assert result == 1


def test_main_output_file(sample_project, tmp_path):
    out = str(tmp_path / "context.md")
    result = main(["--quiet", "--output", out, str(sample_project)])
    assert result == 0
    assert os.path.exists(out)
    content = open(out).read()
    assert "Project Context" in content

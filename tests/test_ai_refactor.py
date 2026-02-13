"""Tests for mw ai refactor (AST-based static refactoring analyzer)."""

import os
import sys
import tempfile
import textwrap

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.ai_refactor import (
    Refactoring,
    analyze_file,
    apply_auto_fixes,
    format_results,
    get_function_complexity,
    main,
    scan_directory,
)


@pytest.fixture
def tmp_py(tmp_path):
    """Create a temp Python file from source text."""
    def _make(source: str, name: str = "test_code.py") -> str:
        p = tmp_path / name
        p.write_text(textwrap.dedent(source))
        return str(p)
    return _make


class TestLongFunction:
    def test_detects_long_function(self, tmp_py):
        # 60-line function
        lines = "\n".join(f"    x = {i}" for i in range(55))
        src = f"def long_func():\n{lines}\n"
        results = analyze_file(tmp_py(src))
        cats = [r.category for r in results]
        assert "extract-function" in cats

    def test_short_function_ok(self, tmp_py):
        src = "def short():\n    return 1\n"
        results = analyze_file(tmp_py(src))
        assert not any(r.category == "extract-function" for r in results)


class TestDeepNesting:
    def test_detects_deep_nesting(self, tmp_py):
        src = """
        def nested():
            if True:
                if True:
                    if True:
                        if True:
                            if True:
                                pass
        """
        results = analyze_file(tmp_py(src))
        assert any(r.category == "reduce-nesting" for r in results)


class TestComplexity:
    def test_high_complexity(self, tmp_py):
        branches = "\n".join(f"    if x == {i}: pass" for i in range(15))
        src = f"def complex_func(x):\n{branches}\n"
        results = analyze_file(tmp_py(src))
        assert any(r.category == "reduce-complexity" for r in results)


class TestGodClass:
    def test_detects_god_class(self, tmp_py):
        methods = "\n".join(f"    def m{i}(self): pass" for i in range(15))
        src = f"class Big:\n{methods}\n"
        results = analyze_file(tmp_py(src))
        assert any(r.category == "decompose-class" for r in results)


class TestStarImports:
    def test_detects_star_import(self, tmp_py):
        src = "from os import *\n"
        results = analyze_file(tmp_py(src))
        assert any(r.category == "explicit-imports" for r in results)


class TestBareExcepts:
    def test_detects_bare_except(self, tmp_py):
        src = """
        def f():
            try:
                pass
            except:
                pass
        """
        results = analyze_file(tmp_py(src))
        assert any(r.category == "specific-exception" for r in results)

    def test_auto_fix_bare_except(self, tmp_py):
        src = "def f():\n    try:\n        pass\n    except:\n        pass\n"
        path = tmp_py(src)
        refs = analyze_file(path)
        count = apply_auto_fixes(path, refs)
        assert count > 0
        content = open(path).read()
        assert "except Exception as e:" in content


class TestMutableDefaults:
    def test_detects_mutable_default(self, tmp_py):
        src = "def f(items=[]):\n    return items\n"
        results = analyze_file(tmp_py(src))
        assert any(r.category == "immutable-default" for r in results)


class TestTooManyParams:
    def test_detects_too_many_params(self, tmp_py):
        src = "def f(a, b, c, d, e, f, g):\n    pass\n"
        results = analyze_file(tmp_py(src))
        assert any(r.category == "parameter-object" for r in results)

    def test_self_not_counted(self, tmp_py):
        src = "class C:\n    def f(self, a, b, c):\n        pass\n"
        results = analyze_file(tmp_py(src))
        assert not any(r.category == "parameter-object" for r in results)


class TestDeadCode:
    def test_detects_dead_code(self, tmp_py):
        src = """
        def f():
            return 1
            x = 2
        """
        results = analyze_file(tmp_py(src))
        assert any(r.category == "dead-code" for r in results)


class TestFormatResults:
    def test_terminal_format(self, tmp_py):
        src = "from os import *\n"
        path = tmp_py(src)
        refs = analyze_file(path)
        output = format_results(path, refs)
        assert "Refactoring Report" in output

    def test_markdown_format(self, tmp_py):
        src = "from os import *\n"
        path = tmp_py(src)
        refs = analyze_file(path)
        output = format_results(path, refs, as_markdown=True)
        assert "# 🔧" in output

    def test_clean_file(self, tmp_py):
        src = "x = 1\n"
        path = tmp_py(src)
        refs = analyze_file(path)
        output = format_results(path, refs)
        assert "Clean code" in output


class TestScanDirectory:
    def test_scan_finds_issues(self, tmp_path):
        (tmp_path / "bad.py").write_text("from os import *\n")
        (tmp_path / "ok.py").write_text("x = 1\n")
        results = scan_directory(str(tmp_path))
        assert len(results) >= 1

    def test_skips_git_dir(self, tmp_path):
        git = tmp_path / ".git"
        git.mkdir()
        (git / "bad.py").write_text("from os import *\n")
        results = scan_directory(str(tmp_path))
        assert not results


class TestMain:
    def test_help(self):
        assert main(["--help"]) == 0

    def test_missing_file(self):
        assert main(["/nonexistent.py"]) == 1

    def test_file_analysis(self, tmp_py):
        src = "from os import *\ndef f(a,b,c,d,e,f,g):\n    pass\n"
        path = tmp_py(src)
        ret = main([path])
        assert ret == 0  # no critical/high

    def test_report_mode(self, tmp_py):
        src = "from os import *\n"
        path = tmp_py(src)
        main([path, "--report"])
        import pathlib
        report = pathlib.Path(path).with_suffix(".refactor.md")
        assert report.exists()

"""Tests for mw ai optimize — performance optimizer."""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.ai_optimize import PythonOptimizer, analyze_file, cmd_optimize


class TestPythonOptimizer:
    def _analyze(self, code: str):
        opt = PythonOptimizer(code, "<test>")
        return opt.analyze()

    def test_len_eq_zero(self):
        code = "if len(items) == 0:\n    pass"
        results = self._analyze(code)
        assert any("truthiness" in r.title.lower() for r in results)

    def test_len_gt_zero(self):
        code = "if len(items) > 0:\n    pass"
        results = self._analyze(code)
        assert any("truthiness" in r.title.lower() for r in results)

    def test_mutable_default_list(self):
        code = "def func(items=[]):\n    pass"
        results = self._analyze(code)
        assert any("mutable" in r.title.lower() for r in results)

    def test_mutable_default_dict(self):
        code = "def func(data={}):\n    pass"
        results = self._analyze(code)
        assert any("mutable" in r.title.lower() for r in results)

    def test_string_concat_in_loop(self):
        code = 'result = ""\nfor x in items:\n    result += "hello"'
        results = self._analyze(code)
        assert any("concatenation" in r.title.lower() for r in results)

    def test_wildcard_import(self):
        code = "from os import *"
        results = self._analyze(code)
        assert any("wildcard" in r.title.lower() for r in results)

    def test_bare_except(self):
        code = "try:\n    pass\nexcept:\n    pass"
        results = self._analyze(code)
        assert any("bare except" in r.title.lower() for r in results)

    def test_append_in_loop(self):
        code = "result = []\nfor x in items:\n    result.append(x)"
        results = self._analyze(code)
        assert any("comprehension" in r.title.lower() for r in results)

    def test_heavy_import(self):
        code = "import pandas"
        results = self._analyze(code)
        assert any("lazy" in r.title.lower() for r in results)

    def test_clean_code_no_issues(self):
        code = "x = 1\ny = x + 2\nprint(y)"
        results = self._analyze(code)
        assert len(results) == 0

    def test_syntax_error_handled(self):
        code = "def ("
        results = self._analyze(code)
        assert results == []


class TestAnalyzeFile:
    def test_nonexistent_file(self):
        results = analyze_file("/tmp/nonexistent_file_xyz.py")
        assert results == []

    def test_non_python_file(self):
        results = analyze_file("/tmp/test.txt")
        assert results == []

    def test_real_file(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write("def func(items=[]):\n    return items\n")
            f.flush()
            results = analyze_file(f.name)
            assert len(results) > 0
            os.unlink(f.name)


class TestCmdOptimize:
    def test_help(self):
        assert cmd_optimize(["--help"]) == 0

    def test_missing_file(self):
        assert cmd_optimize(["/tmp/no_such_file_abc.py"]) == 1

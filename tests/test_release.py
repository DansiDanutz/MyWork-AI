"""Tests for mw release command."""
import os
import sys
import json
import tempfile
import shutil
import subprocess
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from mw import cmd_release


class TestRelease:
    """Test release command."""

    def setup_method(self):
        self.orig_dir = os.getcwd()
        self.tmpdir = tempfile.mkdtemp()
        os.chdir(self.tmpdir)
        # Init git repo
        subprocess.run(["git", "init"], capture_output=True, cwd=self.tmpdir)
        subprocess.run(["git", "config", "user.email", "test@test.com"], capture_output=True, cwd=self.tmpdir)
        subprocess.run(["git", "config", "user.name", "Test"], capture_output=True, cwd=self.tmpdir)

    def teardown_method(self):
        os.chdir(self.orig_dir)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _create_pyproject(self, version="1.0.0"):
        Path(self.tmpdir, "pyproject.toml").write_text(f'[project]\nname = "test"\nversion = "{version}"\n')
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=self.tmpdir)
        subprocess.run(["git", "commit", "-m", "init"], capture_output=True, cwd=self.tmpdir)

    def _create_package_json(self, version="1.0.0"):
        Path(self.tmpdir, "package.json").write_text(json.dumps({"name": "test", "version": version}))
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=self.tmpdir)
        subprocess.run(["git", "commit", "-m", "init"], capture_output=True, cwd=self.tmpdir)

    def test_status_no_version_file(self):
        """Status works even without version file."""
        ret = cmd_release(["status"])
        assert ret == 0

    def test_status_with_pyproject(self):
        self._create_pyproject("2.0.0")
        ret = cmd_release(["status"])
        assert ret == 0

    def test_dry_run_patch(self):
        self._create_pyproject("1.0.0")
        # Add a commit
        Path(self.tmpdir, "test.py").write_text("# test")
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=self.tmpdir)
        subprocess.run(["git", "commit", "-m", "feat: add test"], capture_output=True, cwd=self.tmpdir)
        ret = cmd_release(["--dry-run", "patch"])
        assert ret == 0
        # Version should NOT have changed
        content = Path(self.tmpdir, "pyproject.toml").read_text()
        assert '1.0.0' in content

    def test_patch_bump(self):
        self._create_pyproject("1.0.0")
        Path(self.tmpdir, "test.py").write_text("# test")
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=self.tmpdir)
        subprocess.run(["git", "commit", "-m", "fix: something"], capture_output=True, cwd=self.tmpdir)
        ret = cmd_release(["patch"])
        assert ret == 0
        content = Path(self.tmpdir, "pyproject.toml").read_text()
        assert '1.0.1' in content

    def test_minor_bump(self):
        self._create_pyproject("1.0.0")
        Path(self.tmpdir, "x.py").write_text("x")
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=self.tmpdir)
        subprocess.run(["git", "commit", "-m", "feat: new feature"], capture_output=True, cwd=self.tmpdir)
        ret = cmd_release(["minor"])
        assert ret == 0
        content = Path(self.tmpdir, "pyproject.toml").read_text()
        assert '1.1.0' in content

    def test_major_bump(self):
        self._create_pyproject("1.2.3")
        Path(self.tmpdir, "y.py").write_text("y")
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=self.tmpdir)
        subprocess.run(["git", "commit", "-m", "feat: breaking change"], capture_output=True, cwd=self.tmpdir)
        ret = cmd_release(["major"])
        assert ret == 0
        content = Path(self.tmpdir, "pyproject.toml").read_text()
        assert '2.0.0' in content

    def test_explicit_version(self):
        self._create_pyproject("1.0.0")
        Path(self.tmpdir, "z.py").write_text("z")
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=self.tmpdir)
        subprocess.run(["git", "commit", "-m", "custom version"], capture_output=True, cwd=self.tmpdir)
        ret = cmd_release(["3.5.0"])
        assert ret == 0
        content = Path(self.tmpdir, "pyproject.toml").read_text()
        assert '3.5.0' in content

    def test_package_json_bump(self):
        self._create_package_json("2.0.0")
        Path(self.tmpdir, "a.js").write_text("//a")
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=self.tmpdir)
        subprocess.run(["git", "commit", "-m", "feat: js feature"], capture_output=True, cwd=self.tmpdir)
        ret = cmd_release(["patch"])
        assert ret == 0
        data = json.loads(Path(self.tmpdir, "package.json").read_text())
        assert data["version"] == "2.0.1"

    def test_changelog_updated(self):
        self._create_pyproject("1.0.0")
        Path(self.tmpdir, "CHANGELOG.md").write_text("# Changelog\n\n## [1.0.0] - 2026-01-01\n- init\n")
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=self.tmpdir)
        subprocess.run(["git", "commit", "-m", "feat: new thing"], capture_output=True, cwd=self.tmpdir)
        ret = cmd_release(["patch"])
        assert ret == 0
        cl = Path(self.tmpdir, "CHANGELOG.md").read_text()
        assert "1.0.1" in cl

    def test_git_tag_created(self):
        self._create_pyproject("1.0.0")
        Path(self.tmpdir, "b.py").write_text("b")
        subprocess.run(["git", "add", "-A"], capture_output=True, cwd=self.tmpdir)
        subprocess.run(["git", "commit", "-m", "feat: tagged"], capture_output=True, cwd=self.tmpdir)
        cmd_release(["patch"])
        r = subprocess.run(["git", "tag"], capture_output=True, text=True, cwd=self.tmpdir)
        assert "v1.0.1" in r.stdout

    def test_help(self):
        ret = cmd_release(["--help"])
        assert ret == 0

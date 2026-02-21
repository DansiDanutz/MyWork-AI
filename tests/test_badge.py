"""
Comprehensive tests for badge.py (mw badge command).
Tests badge generation, version detection, and README updating.
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add tools directory to path
TOOLS_DIR = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import badge


@pytest.fixture
def temp_project_root(tmp_path):
    """Create a temporary project with various config files."""
    # Create pyproject.toml
    (tmp_path / "pyproject.toml").write_text("""
[project]
name = "test-project"
version = "3.0.0"
requires-python = ">=3.9"
""")

    # Create LICENSE
    (tmp_path / "LICENSE").write_text("""
MIT License

Copyright (c) 2024 Test Author
""")

    # Create tools directory with some Python code
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    (tools_dir / "__init__.py").write_text("")
    (tools_dir / "mw.py").write_text("""
def cmd_help():
    pass

def cmd_status():
    pass

def cmd_version():
    pass

def cmd_test():
    pass
""")

    # Create tests directory with some tests
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "__init__.py").write_text("")
    (tests_dir / "test_example.py").write_text("""
def test_example_one():
    assert True

def test_example_two():
    assert 1 + 1 == 2

def test_example_three():
    pass
""")

    # Create README.md
    (tmp_path / "README.md").write_text("""
# Test Project

A test project for badge generation.

<!-- badges-start -->
<!-- badges-end -->

## Features
- Feature 1
- Feature 2
""")

    return tmp_path


class TestVersionDetection:
    """Test version detection from various config files."""

    def test_detect_version_pyproject_toml(self, temp_project_root):
        version = badge.detect_version(temp_project_root)
        assert version == "3.0.0"

    def test_detect_version_package_json(self, tmp_path):
        (tmp_path / "package.json").write_text('{"version": "2.5.1"}')
        version = badge.detect_version(tmp_path)
        assert version == "2.5.1"

    def test_detect_version_version_file(self, tmp_path):
        (tmp_path / "VERSION").write_text("1.2.3\n")
        version = badge.detect_version(tmp_path)
        assert version == "1.2.3"

    def test_detect_version_no_config(self, tmp_path):
        version = badge.detect_version(tmp_path)
        assert version is None


class TestTestCounting:
    """Test test function counting."""

    def test_count_tests(self, temp_project_root):
        count = badge.count_tests(temp_project_root)
        assert count == 3

    def test_count_tests_no_tests_dir(self, tmp_path):
        count = badge.count_tests(tmp_path)
        assert count == 0


class TestCommandCounting:
    """Test command counting from mw.py."""

    def test_count_commands(self, temp_project_root):
        count = badge.count_commands(temp_project_root)
        assert count == 4  # help, status, version, test

    def test_count_commands_no_mw_py(self, tmp_path):
        count = badge.count_commands(tmp_path)
        assert count == 0


class TestLOCCounting:
    """Test lines of code counting."""

    def test_count_loc(self, temp_project_root):
        loc = badge.count_loc(temp_project_root)
        assert loc > 0

    def test_count_loc_empty_project(self, tmp_path):
        loc = badge.count_loc(tmp_path)
        assert loc == 0


class TestLicenseDetection:
    """Test license type detection."""

    def test_detect_license_mit(self, temp_project_root):
        lic = badge.detect_license(temp_project_root)
        assert lic == "MIT"

    def test_detect_license_apache(self, tmp_path):
        (tmp_path / "LICENSE").write_text("""
Apache License
Version 2.0
""")
        lic = badge.detect_license(tmp_path)
        assert lic == "Apache-2.0"

    def test_detect_license_gpl(self, tmp_path):
        (tmp_path / "LICENSE").write_text("""
GNU GPL
Version 3, 29 June 2007
""")
        lic = badge.detect_license(tmp_path)
        assert lic == "GPL-3.0"

    def test_detect_license_no_file(self, tmp_path):
        lic = badge.detect_license(tmp_path)
        assert lic == "unknown"

    def test_detect_license_custom(self, tmp_path):
        (tmp_path / "LICENSE").write_text("""
Copyright 2024 Me
All rights reserved.
""")
        lic = badge.detect_license(tmp_path)
        assert lic == "custom"


class TestPythonVersionDetection:
    """Test Python version detection."""

    def test_detect_python_version(self, temp_project_root):
        version = badge.detect_python_version(temp_project_root)
        assert version == ">=3.9"

    def test_detect_python_version_no_pyproject(self, tmp_path):
        version = badge.detect_python_version(tmp_path)
        assert version is None


class TestBadgeURLGeneration:
    """Test shields.io URL generation."""

    def test_shields_url_basic(self):
        url = badge.shields_url("version", "v3.0.0", "blue")
        assert "version-v3.0.0-blue" in url
        assert "img.shields.io" in url

    def test_shields_url_custom_style(self):
        url = badge.shields_url("tests", "150", "green", "for-the-badge")
        assert "style=for-the-badge" in url

    def test_shields_url_special_chars(self):
        url = badge.shields_url("lines of code", "10k+", "informational")
        assert "lines%20of%20code" in url


class TestBadgeGeneration:
    """Test badge generation for all badge types."""

    def test_generate_badges_version(self, temp_project_root):
        badges = badge.generate_badges(temp_project_root)
        version_badge = next((b for b in badges if b['name'] == 'version'), None)
        assert version_badge is not None
        assert version_badge['value'] == 'v3.0.0'
        assert version_badge['color'] == 'blue'

    def test_generate_badges_python(self, temp_project_root):
        badges = badge.generate_badges(temp_project_root)
        py_badge = next((b for b in badges if b['name'] == 'python'), None)
        assert py_badge is not None
        assert py_badge['value'] == '>=3.9'

    def test_generate_badges_tests(self, temp_project_root):
        badges = badge.generate_badges(temp_project_root)
        test_badge = next((b for b in badges if b['name'] == 'tests'), None)
        assert test_badge is not None
        assert test_badge['value'] == '3'
        # With only 3 tests, should be yellow (<50)
        assert test_badge['color'] == 'yellow'

    def test_generate_badges_commands(self, temp_project_root):
        badges = badge.generate_badges(temp_project_root)
        cmd_badge = next((b for b in badges if b['name'] == 'commands'), None)
        assert cmd_badge is not None
        assert cmd_badge['value'] == '4'
        assert cmd_badge['color'] == 'purple'

    def test_generate_badges_loc(self, temp_project_root):
        badges = badge.generate_badges(temp_project_root)
        loc_badge = next((b for b in badges if b['name'] == 'loc'), None)
        assert loc_badge is not None
        assert loc_badge['value'] is not None
        assert loc_badge['color'] == 'informational'

    def test_generate_badges_license(self, temp_project_root):
        badges = badge.generate_badges(temp_project_root)
        lic_badge = next((b for b in badges if b['name'] == 'license'), None)
        assert lic_badge is not None
        assert lic_badge['value'] == 'MIT'
        assert lic_badge['color'] == 'green'

    def test_generate_badges_platform(self, temp_project_root):
        badges = badge.generate_badges(temp_project_root)
        platform_badge = next((b for b in badges if b['name'] == 'platform'), None)
        assert platform_badge is not None
        assert "linux | macOS | windows" in platform_badge['value']
        assert platform_badge['color'] == 'lightgrey'

    def test_generate_badges_count(self, temp_project_root):
        badges = badge.generate_badges(temp_project_root)
        # Should have version, python, tests, commands, loc, license, platform
        assert len(badges) >= 6


class TestBadgeFormatting:
    """Test badge output formatting."""

    def test_format_badges_md(self, temp_project_root):
        badges = badge.generate_badges(temp_project_root)
        md = badge.format_badges_md(badges)
        assert '![' in md
        assert '](https://img.shields.io' in md
        assert md.count('![') == len(badges)

    def test_format_badges_html(self, temp_project_root):
        badges = badge.generate_badges(temp_project_root)
        html = badge.format_badges_html(badges)
        assert '<img src="' in html
        assert 'alt=' in html
        assert html.count('<img') == len(badges)


class TestReadmeUpdate:
    """Test README.md updating with badges."""

    def test_update_readme_with_markers(self, temp_project_root):
        badges = badge.generate_badges(temp_project_root)
        result = badge.update_readme(temp_project_root, badges)
        assert result is True

        readme_content = (temp_project_root / "README.md").read_text()
        assert '<!-- badges-start -->' in readme_content
        assert '<!-- badges-end -->' in readme_content
        assert '![' in readme_content  # Badge images present

    def test_update_readme_no_markers(self, tmp_path):
        # Create README without markers
        (tmp_path / "README.md").write_text("# Simple Project\n\nContent here\n")
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\nversion = "1.0.0"\n')

        badges = badge.generate_badges(tmp_path)
        result = badge.update_readme(tmp_path, badges)
        assert result is True

        readme_content = (tmp_path / "README.md").read_text()
        # Should have inserted badges after heading
        assert '<!-- badges-start -->' in readme_content

    def test_update_readme_no_readme(self, tmp_path):
        badges = badge.generate_badges(tmp_path)
        result = badge.update_readme(tmp_path, badges)
        assert result is False


class TestBadgeColors:
    """Test badge color selection based on values."""

    def test_test_count_color_high(self, tmp_path):
        # Create project with many tests
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_content = "\n".join([f"def test_{i}(): pass" for i in range(150)])
        (tests_dir / "test_many.py").write_text(test_content)
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\nversion = "1.0.0"\n')

        badges = badge.generate_badges(tmp_path)
        test_badge = next((b for b in badges if b['name'] == 'tests'), None)
        assert test_badge is not None
        assert test_badge['color'] == 'brightgreen'  # >= 100 tests

    def test_test_count_color_medium(self, tmp_path):
        # Create project with medium tests
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_content = "\n".join([f"def test_{i}(): pass" for i in range(75)])
        (tests_dir / "test_medium.py").write_text(test_content)
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\nversion = "1.0.0"\n')

        badges = badge.generate_badges(tmp_path)
        test_badge = next((b for b in badges if b['name'] == 'tests'), None)
        assert test_badge is not None
        assert test_badge['color'] == 'green'  # >= 50 tests

    def test_loc_formatting_k(self, tmp_path):
        # Create project with large LOC (mocked)
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\nversion = "1.0.0"\n')
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        # Create a file with many lines
        (tools_dir / "large.py").write_text("\n".join([f"line_{i}" for i in range(12000)]))

        badges = badge.generate_badges(tmp_path)
        loc_badge = next((b for b in badges if b['name'] == 'loc'), None)
        assert loc_badge is not None
        assert 'k+' in loc_badge['value'] or str(loc_badge['value']).isdigit()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_project(self, tmp_path):
        badges = badge.generate_badges(tmp_path)
        # Should still work, just with fewer badges
        assert isinstance(badges, list)
        # Platform badge should always be present
        assert any(b['name'] == 'platform' for b in badges)

    def test_malformed_pyproject(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("this is not valid toml [[[")
        version = badge.detect_version(tmp_path)
        assert version is None

    def test_malformed_package_json(self, tmp_path):
        (tmp_path / "package.json").write_text("{invalid json}")
        version = badge.detect_version(tmp_path)
        assert version is None

    def test_zero_tests(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\nversion = "1.0.0"\n')
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "empty.py").write_text("# No tests here")

        badges = badge.generate_badges(tmp_path)
        # Tests badge should not appear when count is 0
        assert not any(b['name'] == 'tests' for b in badges)


class TestCLIThroughSubprocess:
    """Integration tests via CLI subprocess."""

    def test_badge_generate_runs(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "badge.py"), "generate"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Should run without error
        assert result.returncode in (0, 1)

    def test_badge_help(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "badge.py"), "help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0
        assert "Badge Generator" in result.stdout

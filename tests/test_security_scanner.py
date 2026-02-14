"""Tests for security scanner."""
import os
import sys
import json
import tempfile
import shutil
import pytest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from tools.security_scanner import (
    scan_secrets, scan_permissions, scan_gitignore,
    scan_code_patterns, full_scan, print_report
)


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory."""
    return tmp_path


class TestScanSecrets:
    def test_detects_api_key(self, temp_project):
        f = temp_project / "config.py"
        f.write_text('API_KEY = "sk-abc123def456ghi789jkl012mno345"')
        findings = scan_secrets(str(temp_project))
        assert len(findings) >= 1
        assert any('API Key' in f['type'] or 'Key' in f['type'] for f in findings)

    def test_detects_password(self, temp_project):
        f = temp_project / "settings.py"
        f.write_text('password = "super_secret_password_123"')
        findings = scan_secrets(str(temp_project))
        assert len(findings) >= 1

    def test_ignores_comments(self, temp_project):
        f = temp_project / "config.py"
        f.write_text('# api_key = "sk-abc123def456ghi789jkl012mno345"\n')
        findings = scan_secrets(str(temp_project))
        assert len(findings) == 0

    def test_clean_file(self, temp_project):
        f = temp_project / "clean.py"
        f.write_text('x = 42\nname = "hello"\n')
        findings = scan_secrets(str(temp_project))
        assert len(findings) == 0

    def test_detects_bearer_token(self, temp_project):
        f = temp_project / "api.py"
        f.write_text('headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9abcdef"}')
        findings = scan_secrets(str(temp_project))
        assert len(findings) >= 1

    def test_skips_git_dir(self, temp_project):
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        f = git_dir / "config"
        f.write_text('token = "sk-abc123def456ghi789jkl012mno345"')
        findings = scan_secrets(str(temp_project))
        assert len(findings) == 0

    def test_masks_values(self, temp_project):
        f = temp_project / "config.py"
        f.write_text('API_KEY = "sk-abc123def456ghi789jkl012mno345"')
        findings = scan_secrets(str(temp_project))
        for finding in findings:
            assert '...' in finding.get('masked_value', '') or '***' in finding.get('masked_value', '')


class TestScanGitignore:
    def test_missing_gitignore(self, temp_project):
        findings = scan_gitignore(str(temp_project))
        assert any(f['type'] == 'No .gitignore' for f in findings)

    def test_complete_gitignore(self, temp_project):
        gi = temp_project / ".gitignore"
        gi.write_text('.env\n*.pem\n*.key\n*.p12\ncredentials.json\nsecrets.json\n*.sqlite\n*.db\n')
        findings = scan_gitignore(str(temp_project))
        assert len(findings) == 0

    def test_missing_env_pattern(self, temp_project):
        gi = temp_project / ".gitignore"
        gi.write_text('*.pem\n*.key\n')
        findings = scan_gitignore(str(temp_project))
        assert any('.env' in f.get('detail', '') for f in findings)


class TestScanCodePatterns:
    def test_detects_eval(self, temp_project):
        f = temp_project / "bad.py"
        f.write_text('result = eval(user_input)\n')  # noqa: security
        findings = scan_code_patterns(str(temp_project))
        assert any('eval' in f['type'] for f in findings)

    def test_detects_pickle(self, temp_project):
        f = temp_project / "bad.py"
        f.write_text('import pickle\ndata = pickle.loads(raw_data)\n')  # noqa: security
        findings = scan_code_patterns(str(temp_project))
        assert any('pickle' in f['type'].lower() for f in findings)

    def test_detects_ssl_disabled(self, temp_project):
        f = temp_project / "api.py"
        f.write_text('requests.get(url, verify=False)\n')  # noqa: security
        findings = scan_code_patterns(str(temp_project))
        assert any('SSL' in f['type'] for f in findings)

    def test_clean_code(self, temp_project):
        f = temp_project / "good.py"
        f.write_text('def add(a, b):\n    return a + b\n')
        findings = scan_code_patterns(str(temp_project))
        assert len(findings) == 0


class TestFullScan:
    def test_returns_summary(self, temp_project):
        results = full_scan(str(temp_project))
        assert 'summary' in results
        assert 'total_findings' in results['summary']
        assert 'score' in results['summary']

    def test_score_perfect_for_clean(self, temp_project):
        gi = temp_project / ".gitignore"
        gi.write_text('.env\n*.pem\n*.key\n*.p12\ncredentials.json\nsecrets.json\n*.sqlite\n*.db\n')
        results = full_scan(str(temp_project))
        assert results['summary']['score'] >= 80

    def test_print_report_no_crash(self, temp_project, capsys):
        results = full_scan(str(temp_project))
        print_report(results)
        captured = capsys.readouterr()
        assert 'Security Report' in captured.out

    def test_has_all_sections(self, temp_project):
        results = full_scan(str(temp_project))
        for key in ['secrets', 'permissions', 'dependencies', 'gitignore', 'code_patterns']:
            assert key in results

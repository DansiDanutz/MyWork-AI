"""Tests for mw deploy and mw monitor commands."""
import os
import sys
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from mw import cmd_deploy, cmd_monitor, _save_deploy_record


class TestDeployCommand:
    """Tests for cmd_deploy."""

    def test_deploy_no_args_detects_platform(self):
        """Deploy with no args should auto-detect platform."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a package.json to trigger vercel detection
            with open(os.path.join(tmpdir, "package.json"), "w") as f:
                json.dump({"name": "test"}, f)
            
            with patch("os.getcwd", return_value=tmpdir):
                with patch("subprocess.run") as mock_run:
                    # Git status check
                    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                    result = cmd_deploy([])
                    # Should attempt vercel deploy
                    assert mock_run.called

    def test_deploy_unknown_platform(self):
        """Deploy with unknown platform should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("os.getcwd", return_value=tmpdir):
                result = cmd_deploy(["--platform", "heroku"])
                assert result == 1

    def test_deploy_no_project_no_detection(self):
        """Deploy in empty dir should fail gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("os.getcwd", return_value=tmpdir):
                result = cmd_deploy([])
                assert result == 1

    def test_deploy_dockerfile_detects_docker(self, tmp_path):
        """Should detect Docker platform from Dockerfile."""
        (tmp_path / "Dockerfile").write_text("FROM python:3.11")
        
        with patch("os.getcwd", return_value=str(tmp_path)):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="abc123", stderr="")
                cmd_deploy([])
                # Should have called docker build
                calls = [str(c) for c in mock_run.call_args_list]
                assert any("docker" in c for c in calls)

    def test_deploy_railway_json_detects_railway(self, tmp_path):
        """Should detect Railway from railway.json."""
        (tmp_path / "railway.json").write_text("{}")
        
        with patch("os.getcwd", return_value=str(tmp_path)):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                cmd_deploy([])

    def test_deploy_prod_blocks_uncommitted(self, tmp_path):
        """Prod deploy should block if uncommitted changes."""
        (tmp_path / "package.json").write_text('{"name":"test"}')
        
        with patch("os.getcwd", return_value=str(tmp_path)):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="M file.js\n", stderr="")
                result = cmd_deploy(["--prod"])
                assert result == 1


class TestSaveDeployRecord:
    """Tests for _save_deploy_record."""

    def test_save_creates_file(self, tmp_path):
        """Should create deploy record file."""
        _save_deploy_record(str(tmp_path), "vercel", "https://example.vercel.app", True)
        record_file = tmp_path / ".mw-deploys.json"
        assert record_file.exists()
        data = json.loads(record_file.read_text())
        assert len(data) == 1
        assert data[0]["platform"] == "vercel"
        assert data[0]["production"] is True

    def test_save_appends(self, tmp_path):
        """Should append to existing records."""
        _save_deploy_record(str(tmp_path), "vercel", "url1", False)
        _save_deploy_record(str(tmp_path), "railway", "url2", True)
        data = json.loads((tmp_path / ".mw-deploys.json").read_text())
        assert len(data) == 2

    def test_save_caps_at_50(self, tmp_path):
        """Should keep only last 50 records."""
        record_file = tmp_path / ".mw-deploys.json"
        record_file.write_text(json.dumps([{"i": i} for i in range(55)]))
        _save_deploy_record(str(tmp_path), "docker", "url", False)
        data = json.loads(record_file.read_text())
        assert len(data) == 50


class TestMonitorCommand:
    """Tests for cmd_monitor."""

    def test_monitor_no_deploys(self):
        """Monitor with no deploy records shows helpful message."""
        with patch("glob.glob", return_value=[]):
            with patch("os.listdir", return_value=[]):
                result = cmd_monitor([])
                assert result == 0

    def test_monitor_reads_records(self, tmp_path):
        """Monitor should read deploy records."""
        deploy_file = tmp_path / ".mw-deploys.json"
        deploy_file.write_text(json.dumps([{
            "timestamp": "2026-02-11T09:00:00",
            "platform": "vercel",
            "url": "https://test.vercel.app",
            "production": True,
            "project": "test-project"
        }]))
        
        with patch("glob.glob", return_value=[str(deploy_file)]):
            with patch("os.listdir", return_value=[]):
                result = cmd_monitor([])
                assert result == 0

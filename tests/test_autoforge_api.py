"""
Tests for AutoForge API Module
================================
Phase 3: Testing & Reliability — AutoForge API unit tests.
"""

import os
import sys
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))


class TestGetAutoforgePython:
    """Tests for get_autoforge_python() utility."""

    def test_returns_string(self):
        from autoforge_api import get_autoforge_python
        result = get_autoforge_python()
        assert isinstance(result, str)

    def test_returns_sys_executable_when_no_venv(self, tmp_path):
        with patch("autoforge_api.AUTOFORGE_PATH", tmp_path):
            from autoforge_api import get_autoforge_python
            result = get_autoforge_python()
            assert result == sys.executable

    def test_finds_venv_python(self, tmp_path):
        venv_python = tmp_path / "venv" / "bin" / "python"
        venv_python.parent.mkdir(parents=True)
        venv_python.write_text("#!/usr/bin/env python3")
        with patch("autoforge_api.AUTOFORGE_PATH", tmp_path):
            from autoforge_api import get_autoforge_python
            result = get_autoforge_python()
            assert result == str(venv_python)

    def test_finds_dot_venv_python(self, tmp_path):
        venv_python = tmp_path / ".venv" / "bin" / "python"
        venv_python.parent.mkdir(parents=True)
        venv_python.write_text("#!/usr/bin/env python3")
        with patch("autoforge_api.AUTOFORGE_PATH", tmp_path):
            from autoforge_api import get_autoforge_python
            result = get_autoforge_python()
            assert result == str(venv_python)


class TestAutoForgeAPI:
    """Tests for AutoForgeAPI class."""

    def setup_method(self):
        from autoforge_api import AutoForgeAPI
        self.api = AutoForgeAPI(base_url="http://127.0.0.1:9999")

    def test_init_sets_base_url(self):
        assert self.api.base_url == "http://127.0.0.1:9999"

    def test_is_server_running_true(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        self.api.client = MagicMock()
        self.api.client.get.return_value = mock_response
        assert self.api.is_server_running() is True

    def test_is_server_running_false_on_connect_error(self):
        import httpx
        self.api.client = MagicMock()
        self.api.client.get.side_effect = httpx.ConnectError("refused")
        assert self.api.is_server_running() is False

    def test_get_agent_status_success(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "running", "features_done": 5}
        self.api.client = MagicMock()
        self.api.client.get.return_value = mock_response
        result = self.api.get_agent_status("my-project")
        assert result["status"] == "running"
        self.api.client.get.assert_called_once_with(
            "http://127.0.0.1:9999/api/projects/my-project/agent/status"
        )

    def test_get_agent_status_connect_error(self):
        import httpx
        self.api.client = MagicMock()
        self.api.client.get.side_effect = httpx.ConnectError("refused")
        result = self.api.get_agent_status("my-project")
        assert result["status"] == "unknown"
        assert "error" in result

    def test_start_agent_success(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "started"}
        self.api.client = MagicMock()
        self.api.client.post.return_value = mock_response
        result = self.api.start_agent("my-project", model="test-model", concurrency=2)
        assert result["status"] == "started"
        call_args = self.api.client.post.call_args
        assert "my-project" in call_args[0][0]
        assert call_args[1]["json"]["model"] == "test-model"
        assert call_args[1]["json"]["max_concurrency"] == 2

    def test_start_agent_connect_error(self):
        import httpx
        self.api.client = MagicMock()
        self.api.client.post.side_effect = httpx.ConnectError("refused")
        result = self.api.start_agent("my-project")
        assert "error" in result

    def test_stop_agent_success(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "stopped"}
        self.api.client = MagicMock()
        self.api.client.post.return_value = mock_response
        result = self.api.stop_agent("my-project")
        assert result["status"] == "stopped"

    def test_pause_agent_success(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "paused"}
        self.api.client = MagicMock()
        self.api.client.post.return_value = mock_response
        result = self.api.pause_agent("my-project")
        assert result["status"] == "paused"

    def test_resume_agent_success(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "running"}
        self.api.client = MagicMock()
        self.api.client.post.return_value = mock_response
        result = self.api.resume_agent("my-project")
        assert result["status"] == "running"

    def test_get_features_success(self):
        features = [{"name": "auth", "passes": True}, {"name": "api", "passes": False}]
        mock_response = MagicMock()
        mock_response.json.return_value = features
        self.api.client = MagicMock()
        self.api.client.get.return_value = mock_response
        result = self.api.get_features("my-project")
        assert len(result) == 2

    def test_list_projects_success(self):
        projects = [{"name": "proj-a"}, {"name": "proj-b"}]
        mock_response = MagicMock()
        mock_response.json.return_value = projects
        self.api.client = MagicMock()
        self.api.client.get.return_value = mock_response
        result = self.api.list_projects()
        assert len(result) == 2

    def test_list_projects_error(self):
        self.api.client = MagicMock()
        self.api.client.get.side_effect = Exception("timeout")
        result = self.api.list_projects()
        assert "error" in result


class TestNotifyWebhook:
    """Tests for notify_webhook() function."""

    @patch("autoforge_api.httpx.post")
    @patch("autoforge_api.WEBHOOK_URL", "https://hooks.example.com/test")
    def test_sends_webhook_when_url_set(self, mock_post):
        from autoforge_api import notify_webhook
        notify_webhook("test_event", {"project": "demo"})
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]["json"]
        assert payload["event"] == "test_event"
        assert payload["project"] == "demo"
        assert "timestamp" in payload

    @patch("autoforge_api.httpx.post")
    @patch("autoforge_api.WEBHOOK_URL", "")
    def test_skips_webhook_when_no_url(self, mock_post):
        from autoforge_api import notify_webhook
        notify_webhook("test_event", {"project": "demo"})
        mock_post.assert_not_called()

    @patch("autoforge_api.httpx.post")
    @patch("autoforge_api.WEBHOOK_URL", "https://hooks.example.com/test")
    def test_handles_webhook_failure_gracefully(self, mock_post):
        from autoforge_api import notify_webhook
        mock_post.side_effect = Exception("Connection refused")
        # Should not raise
        notify_webhook("test_event", {"project": "demo"})


class TestGetProgress:
    """Tests for get_progress() function."""

    @patch("autoforge_api.AutoForgeAPI")
    def test_returns_progress_from_api(self, MockAPI):
        mock_api = MockAPI.return_value
        mock_api.is_server_running.return_value = True
        mock_api.get_features.return_value = [
            {"name": "auth", "passes": True, "in_progress": False},
            {"name": "api", "passes": False, "in_progress": True},
            {"name": "ui", "passes": False, "in_progress": False},
        ]
        mock_api.get_agent_status.return_value = {"status": "running"}

        from autoforge_api import get_progress
        result = get_progress("test-proj")
        assert result["total"] == 3
        assert result["passing"] == 1
        assert result["in_progress"] == 1
        assert result["pending"] == 1
        assert result["source"] == "api"

    @patch("autoforge_api.AutoForgeAPI")
    def test_returns_error_when_no_server_no_db(self, MockAPI):
        mock_api = MockAPI.return_value
        mock_api.is_server_running.return_value = False

        from autoforge_api import get_progress
        with patch("autoforge_api.MYWORK_PROJECTS", Path("/nonexistent")):
            result = get_progress("test-proj")
            assert "error" in result


class TestBackwardsCompatAlias:
    """Tests that backward compatibility alias exists."""

    def test_autoforge_client_alias(self):
        from autoforge_api import AutoForgeClient, AutoForgeAPI
        assert AutoForgeClient is AutoForgeAPI

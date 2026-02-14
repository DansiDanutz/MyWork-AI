"""Tests for mw serve / web dashboard."""
import json
import sys
import threading
import time
import urllib.request
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.web_dashboard import (
    DashboardHandler,
    get_brain_stats,
    get_commands,
    get_git_log,
    get_projects,
    get_system_status,
    cmd_serve,
    DASHBOARD_HTML,
)


class TestGetProjects:
    def test_returns_list(self):
        result = get_projects()
        assert isinstance(result, list)

    def test_project_has_name(self):
        projects = get_projects()
        for p in projects:
            assert "name" in p
            assert "path" in p
            assert "language" in p


class TestGetBrainStats:
    def test_returns_dict(self):
        result = get_brain_stats()
        assert isinstance(result, dict)
        assert "entries" in result
        assert "categories" in result
        assert "size_kb" in result

    def test_entries_is_int(self):
        result = get_brain_stats()
        assert isinstance(result["entries"], int)


class TestGetGitLog:
    def test_returns_list(self):
        result = get_git_log(5)
        assert isinstance(result, list)

    def test_commits_have_fields(self):
        commits = get_git_log(3)
        for c in commits:
            assert "hash" in c
            assert "short" in c
            assert "message" in c
            assert "author" in c
            assert "when" in c


class TestGetSystemStatus:
    def test_returns_dict(self):
        result = get_system_status()
        assert isinstance(result, dict)
        assert "python" in result
        assert "framework_version" in result
        assert result["framework_version"] == "2.1.0"

    def test_has_timestamp(self):
        result = get_system_status()
        assert "timestamp" in result


class TestGetCommands:
    def test_returns_list(self):
        cmds = get_commands()
        assert isinstance(cmds, list)
        assert len(cmds) > 10

    def test_command_structure(self):
        cmds = get_commands()
        for c in cmds:
            assert "name" in c
            assert "desc" in c
            assert "category" in c

    def test_has_core_commands(self):
        names = [c["name"] for c in get_commands()]
        assert "status" in names
        assert "projects" in names
        assert "ai" in names


class TestDashboardHTML:
    def test_html_exists(self):
        assert len(DASHBOARD_HTML) > 1000

    def test_html_has_title(self):
        assert "MyWork-AI Dashboard" in DASHBOARD_HTML

    def test_html_has_api_calls(self):
        assert "/api/status" in DASHBOARD_HTML
        assert "/api/projects" in DASHBOARD_HTML
        assert "/api/commits" in DASHBOARD_HTML


class TestServerIntegration:
    """Test the actual HTTP server briefly."""

    def test_server_starts_and_serves(self):
        import http.server
        server = http.server.HTTPServer(("127.0.0.1", 0), DashboardHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()
        time.sleep(0.1)
        try:
            resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/")
            html = resp.read().decode()
            assert "MyWork-AI" in html
            assert resp.status == 200
        finally:
            server.server_close()

    def test_api_status_endpoint(self):
        import http.server
        server = http.server.HTTPServer(("127.0.0.1", 0), DashboardHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()
        time.sleep(0.1)
        try:
            resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/commands")
            data = json.loads(resp.read().decode())
            assert isinstance(data, list)
            assert len(data) > 0
        finally:
            server.server_close()

    def test_api_projects_endpoint(self):
        import http.server
        server = http.server.HTTPServer(("127.0.0.1", 0), DashboardHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()
        time.sleep(0.1)
        try:
            resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/projects")
            data = json.loads(resp.read().decode())
            assert isinstance(data, list)
        finally:
            server.server_close()

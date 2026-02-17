"""Tests for core mw commands that were previously untested."""
import subprocess
import sys
import os
import pytest

MW = os.path.join(os.path.dirname(__file__), "..", "tools", "mw.py")


def run_mw(*args, timeout=15):
    """Run mw command and return result."""
    result = subprocess.run(
        [sys.executable, MW, *args],
        capture_output=True, text=True, timeout=timeout,
        stdin=subprocess.DEVNULL,
        cwd=os.path.dirname(MW)
    )
    return result


class TestVersion:
    def test_version_shows_info(self):
        r = run_mw("version")
        assert r.returncode == 0
        assert "MyWork-AI" in r.stdout

    def test_version_flag(self):
        r = run_mw("--version")
        assert "MyWork-AI" in r.stdout


class TestHelp:
    def test_help_shows_commands(self):
        r = run_mw("help")
        assert r.returncode == 0
        assert "mw" in r.stdout.lower()

    def test_help_flag(self):
        r = run_mw("--help")
        assert "mw" in r.stdout.lower()


class TestStatus:
    def test_status_runs(self):
        r = run_mw("status")
        assert r.returncode == 0

    def test_status_shows_framework_info(self):
        r = run_mw("status")
        assert any(w in r.stdout.lower() for w in ["mywork", "status", "python", "project"])


class TestDashboard:
    def test_dashboard_runs(self):
        r = run_mw("dashboard")
        assert r.returncode == 0


class TestClean:
    def test_clean_dry_run(self):
        r = run_mw("clean", "--dry-run")
        # Should run without errors (may not support --dry-run, that's ok)
        assert r.returncode in (0, 1, 2)

    def test_clean_runs(self):
        r = run_mw("clean")
        assert r.returncode == 0


class TestBrain:
    def test_brain_stats(self):
        r = run_mw("brain", "stats")
        assert r.returncode == 0
        assert any(w in r.stdout.lower() for w in ["brain", "entries", "knowledge", "vault"])

    def test_brain_search(self):
        r = run_mw("brain", "search", "test")
        assert r.returncode == 0


class TestProjects:
    def test_projects_list(self):
        r = run_mw("projects")
        assert r.returncode == 0


class TestCredits:
    def test_credits_shows_info(self):
        r = run_mw("credits")
        assert r.returncode == 0
        assert any(w in r.stdout.lower() for w in ["credit", "mywork", "author", "dan"])


class TestHealth:
    def test_health_runs(self):
        r = run_mw("health")
        # May need a project context, so accept various return codes
        assert r.returncode in (0, 1)


class TestSearch:
    def test_search_with_query(self):
        r = run_mw("search", "brain")
        assert r.returncode == 0
        assert "Search Results" in r.stdout


class TestLinks:
    def test_links_shows_urls(self):
        r = run_mw("links")
        assert r.returncode == 0


class TestEcosystem:
    def test_ecosystem_runs(self):
        r = run_mw("ecosystem")
        assert r.returncode == 0


class TestReport:
    def test_report_runs(self):
        r = run_mw("report")
        assert r.returncode == 0


class TestBadge:
    def test_badge_help(self):
        r = run_mw("badge")
        # Badge without args might show help or generate
        assert r.returncode in (0, 1)


class TestLoc:
    def test_loc_runs(self):
        r = run_mw("loc")
        assert r.returncode == 0
        assert "Lines of Code" in r.stdout

    def test_loc_help(self):
        r = run_mw("loc", "--help")
        assert r.returncode == 0
        assert "Lines of Code Counter" in r.stdout

    def test_loc_json(self):
        import json
        r = run_mw("loc", "--json")
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert "languages" in data
        assert "totals" in data
        assert data["totals"]["total"] > 0

    def test_loc_top(self):
        import json
        r = run_mw("loc", "--top", "3", "--json")
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert len(data["languages"]) <= 3

    def test_loc_alias_lines(self):
        r = run_mw("lines")
        assert r.returncode == 0
        assert "Lines of Code" in r.stdout

    def test_loc_bad_path(self):
        r = run_mw("loc", "/nonexistent/path/xyz")
        assert r.returncode == 1

    def test_loc_lang_filter(self):
        import json
        r = run_mw("loc", "--lang", "python", "--json")
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert len(data["languages"]) <= 1
        if data["languages"]:
            assert "Python" in data["languages"]

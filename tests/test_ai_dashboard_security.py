"""Security contracts for the personal AI Dashboard backend."""

import ast
import importlib.util
from pathlib import Path

import pytest
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "projects" / "ai-dashboard" / "backend"
ADMIN_TOKEN = "configured-admin-token-with-32-chars"


def load_security_module():
    spec = importlib.util.spec_from_file_location("ai_dashboard_security", BACKEND / "security.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_admin_auth_fails_closed_without_configuration(monkeypatch):
    monkeypatch.delenv("AI_DASHBOARD_ADMIN_TOKEN", raising=False)
    security = load_security_module()

    with pytest.raises(HTTPException) as error:
        security.require_admin("Bearer anything")

    assert error.value.status_code == 503


def test_example_environment_cannot_authenticate():
    example = (BACKEND / ".env.example").read_text().splitlines()
    configured = next(
        line.partition("=")[2]
        for line in example
        if line.startswith("AI_DASHBOARD_ADMIN_TOKEN=")
    )

    assert configured == ""


@pytest.mark.parametrize("authorization", [None, "", "Basic token", "Bearer wrong-token"])
def test_admin_auth_rejects_missing_or_invalid_bearer(monkeypatch, authorization):
    monkeypatch.setenv("AI_DASHBOARD_ADMIN_TOKEN", ADMIN_TOKEN)
    security = load_security_module()

    with pytest.raises(HTTPException) as error:
        security.require_admin(authorization)

    assert error.value.status_code == 401


def test_admin_auth_accepts_exact_bearer(monkeypatch):
    monkeypatch.setenv("AI_DASHBOARD_ADMIN_TOKEN", ADMIN_TOKEN)
    security = load_security_module()

    assert security.require_admin(f"Bearer {ADMIN_TOKEN}") is None


def test_admin_auth_fails_closed_for_weak_configuration(monkeypatch):
    monkeypatch.setenv("AI_DASHBOARD_ADMIN_TOKEN", "too-short")
    security = load_security_module()

    with pytest.raises(HTTPException) as error:
        security.require_admin("Bearer too-short")

    assert error.value.status_code == 503


def test_billing_identity_fails_closed_without_configuration(monkeypatch):
    monkeypatch.delenv("AI_DASHBOARD_BILLING_EMAIL", raising=False)
    monkeypatch.delenv("AI_DASHBOARD_FRONTEND_ORIGIN", raising=False)
    security = load_security_module()

    with pytest.raises(HTTPException) as error:
        security.require_billing_identity()

    assert error.value.status_code == 503


@pytest.mark.parametrize(
    "email,origin",
    [
        ("not-an-email", "https://dashboard.example.com"),
        ("admin@ops@example.com", "https://dashboard.example.com"),
        ("admin..ops@example.com", "https://dashboard.example.com"),
        ("admin@example.com", "http://dashboard.example.com"),
        ("admin@example.com", "https://dashboard.example.com/path"),
        ("admin@example.com", "https://user@dashboard.example.com"),
        ("admin@example.com", "https://dashboard example.com"),
        ("admin@example.com", "https://-dashboard.example.com"),
        ("admin@example.com", "https://dashboard.example.com:invalid"),
    ],
)
def test_billing_identity_rejects_untrusted_values(monkeypatch, email, origin):
    monkeypatch.setenv("AI_DASHBOARD_BILLING_EMAIL", email)
    monkeypatch.setenv("AI_DASHBOARD_FRONTEND_ORIGIN", origin)
    security = load_security_module()

    with pytest.raises(HTTPException) as error:
        security.require_billing_identity()

    assert error.value.status_code == 503


def test_billing_identity_accepts_configured_https_origin(monkeypatch):
    monkeypatch.setenv("AI_DASHBOARD_BILLING_EMAIL", "admin@example.com")
    monkeypatch.setenv("AI_DASHBOARD_FRONTEND_ORIGIN", "https://dashboard.example.com/")
    security = load_security_module()

    assert security.require_billing_identity() == (
        "admin@example.com",
        "https://dashboard.example.com",
    )


def protected_functions(path):
    tree = ast.parse(path.read_text())

    def is_admin_dependency(default):
        return (
            isinstance(default, ast.Call)
            and isinstance(default.func, ast.Name)
            and default.func.id == "Depends"
            and any(
                isinstance(argument, ast.Name) and argument.id == "require_admin"
                for argument in default.args
            )
        )

    return {
        node.name: any(is_admin_dependency(default) for default in node.args.defaults)
        or any(is_admin_dependency(default) for default in node.args.kw_defaults if default)
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_every_privileged_dashboard_route_requires_admin():
    main = protected_functions(BACKEND / "main.py")
    billing = protected_functions(BACKEND / "routes" / "billing.py")

    expected_main = {
        "trigger_video_scrape",
        "trigger_news_scrape",
        "trigger_projects_scrape",
        "get_automations",
        "get_automation",
        "create_automation",
        "update_automation",
        "generate_video",
        "check_video_status",
        "approve_automation",
        "get_scheduler_status",
        "run_job",
    }
    expected_billing = {"checkout", "customer_portal"}

    assert {name for name in expected_main if not main.get(name)} == set()
    assert {name for name in expected_billing if not billing.get(name)} == set()
    assert billing["stripe_webhook"] is False


def test_dashboard_development_server_defaults_to_loopback():
    source = (BACKEND / "main.py").read_text()
    shell_launcher = (BACKEND.parent / "start.sh").read_text()
    windows_launcher = (BACKEND.parent / "start.bat").read_text()

    assert 'os.getenv("AI_DASHBOARD_HOST", "127.0.0.1")' in source
    assert '${AI_DASHBOARD_HOST:-127.0.0.1}' in shell_launcher
    assert 'set "AI_DASHBOARD_HOST=127.0.0.1"' in windows_launcher
    assert "--host 0.0.0.0" not in shell_launcher
    assert "--host 0.0.0.0" not in windows_launcher


def test_dspy_disk_cache_is_disabled():
    source = (BACKEND / "services" / "prompt_optimizer.py").read_text()

    assert "dspy.configure_cache(enable_disk_cache=False, enable_memory_cache=True)" in source


def test_frontend_uses_authenticated_server_proxy_for_backend_access():
    frontend = BACKEND.parent / "frontend"
    api_client = (frontend / "lib" / "api.ts").read_text()
    billing_client = (frontend / "lib" / "billing.ts").read_text()
    pricing_client = (frontend / "app" / "pricing" / "page.tsx").read_text()
    billing_backend = (BACKEND / "routes" / "billing.py").read_text()
    security_backend = (BACKEND / "security.py").read_text()
    middleware = (frontend / "middleware.ts").read_text()
    proxy = (frontend / "app" / "api" / "backend" / "[...path]" / "route.ts").read_text()
    vercel = (frontend / "vercel.json").read_text()

    assert 'const API_BASE = "/api/backend"' in api_client
    assert 'const API_BASE = "/api/backend"' in billing_client
    assert "user@example.com" not in pricing_client
    assert "success_url" not in billing_client
    assert "require_billing_identity()" in billing_backend
    assert "AI_DASHBOARD_BILLING_EMAIL" in security_backend
    assert "NEXT_PUBLIC_API_URL" not in api_client + billing_client + vercel
    assert "AI_DASHBOARD_BROWSER_SECRET" in middleware
    assert 'AI_DASHBOARD_ADMIN_TOKEN?.trim()' in middleware + proxy
    assert 'headers.set("authorization", `Bearer ${config.backendToken}`)' in proxy
    assert "const headers = new Headers" in proxy
    assert 'redirect: "manual"' in proxy

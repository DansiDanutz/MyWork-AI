"""
API Hub Tests — Full CRUD + Usage + Dashboard
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi.testclient import TestClient
from database.db import Base, engine
from main import app

# Reset DB for each test run
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "API Hub" in r.json()["service"]


def test_add_key():
    r = client.post("/api/keys", json={
        "name": "Test OpenRouter",
        "provider": "openrouter",
        "key_value": "sk-or-v1-test1234567890abcdef",
        "base_url": "https://openrouter.ai/api/v1"
    })
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Test OpenRouter"
    assert data["provider"] == "openrouter"
    assert "***" in data["key_preview"]  # Key is masked
    assert "test1234567890" not in data["key_preview"]  # Full key NOT exposed
    assert data["is_active"] == True
    return data["id"]


def test_list_keys():
    r = client.get("/api/keys")
    assert r.status_code == 200
    keys = r.json()
    assert len(keys) >= 1
    # Verify no full keys exposed
    for key in keys:
        assert "key_value" not in key


def test_add_multiple_providers():
    providers = [
        {"name": "DeepSeek", "provider": "deepseek", "key_value": "sk-deepseek-test123456"},
        {"name": "Gemini", "provider": "gemini", "key_value": "AIzaSy-gemini-test123456"},
        {"name": "OpenAI", "provider": "openai", "key_value": "sk-proj-openai-test123456"},
    ]
    for p in providers:
        r = client.post("/api/keys", json=p)
        assert r.status_code == 201


def test_get_single_key():
    r = client.get("/api/keys/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_get_nonexistent_key():
    r = client.get("/api/keys/999")
    assert r.status_code == 404


def test_log_usage():
    r = client.post("/api/keys/1/log-usage?tokens=1500&cost=0.003&endpoint=/chat/completions&status_code=200&response_time_ms=450")
    assert r.status_code == 200
    assert r.json()["total_requests"] == 1

    # Log more usage
    for i in range(4):
        client.post(f"/api/keys/1/log-usage?tokens={1000+i*100}&cost={0.002+i*0.001}")
    
    r = client.get("/api/keys/1")
    assert r.json()["total_requests"] == 5


def test_get_usage():
    r = client.get("/api/keys/1/usage")
    assert r.status_code == 200
    data = r.json()
    assert data["total_requests"] == 5
    assert data["total_tokens"] > 0
    assert len(data["recent_logs"]) == 5


def test_deactivate_key():
    r = client.post("/api/keys/1/deactivate")
    assert r.status_code == 200
    
    # Should not appear in active-only list
    r = client.get("/api/keys?active_only=true")
    ids = [k["id"] for k in r.json()]
    assert 1 not in ids


def test_activate_key():
    r = client.post("/api/keys/1/activate")
    assert r.status_code == 200
    
    r = client.get("/api/keys/1")
    assert r.json()["is_active"] == True


def test_filter_by_provider():
    r = client.get("/api/keys?provider=openrouter")
    assert r.status_code == 200
    for key in r.json():
        assert key["provider"] == "openrouter"


def test_dashboard():
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert data["total_keys"] == 4
    assert data["active_keys"] == 4
    assert "openrouter" in data["providers"]
    assert "deepseek" in data["providers"]
    assert len(data["top_keys"]) > 0


def test_delete_key():
    r = client.delete("/api/keys/4")
    assert r.status_code == 200
    
    r = client.get("/api/keys/4")
    assert r.status_code == 404


def test_delete_nonexistent():
    r = client.delete("/api/keys/999")
    assert r.status_code == 404


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

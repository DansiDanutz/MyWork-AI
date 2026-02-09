"""
API Hub — Centralized API Key Manager
FastAPI application entry point.
"""
from datetime import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.db import get_db, init_db
from database.models import APIKey, UsageLog
from schemas import APIKeyCreate, APIKeyResponse, APIKeyUsage, DashboardResponse, UsageLogResponse

app = FastAPI(
    title="API Hub",
    description="Centralized API Key Manager — manage keys, track usage, monitor providers",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


def mask_key(key: str) -> str:
    """Show only last 6 characters of a key."""
    if len(key) <= 6:
        return "***"
    return "***" + key[-6:]


# ─── CRUD Endpoints ───────────────────────────────────────

@app.post("/api/keys", response_model=APIKeyResponse, status_code=201)
def add_key(payload: APIKeyCreate, db: Session = Depends(get_db)):
    """Add a new API key."""
    key = APIKey(
        name=payload.name,
        provider=payload.provider.lower(),
        key_value=payload.key_value,
        key_preview=mask_key(payload.key_value),
        base_url=payload.base_url,
        expires_at=payload.expires_at,
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return key


@app.get("/api/keys", response_model=List[APIKeyResponse])
def list_keys(provider: str = None, active_only: bool = True, db: Session = Depends(get_db)):
    """List all API keys (masked)."""
    query = db.query(APIKey)
    if provider:
        query = query.filter(APIKey.provider == provider.lower())
    if active_only:
        query = query.filter(APIKey.is_active == True)
    return query.order_by(APIKey.created_at.desc()).all()


@app.get("/api/keys/{key_id}", response_model=APIKeyResponse)
def get_key(key_id: int, db: Session = Depends(get_db)):
    """Get a specific API key (masked)."""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    return key


@app.delete("/api/keys/{key_id}")
def delete_key(key_id: int, db: Session = Depends(get_db)):
    """Revoke/delete an API key."""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    db.delete(key)
    db.commit()
    return {"message": f"Key '{key.name}' deleted", "id": key_id}


@app.post("/api/keys/{key_id}/deactivate")
def deactivate_key(key_id: int, db: Session = Depends(get_db)):
    """Deactivate a key without deleting it."""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    key.is_active = False
    db.commit()
    return {"message": f"Key '{key.name}' deactivated"}


@app.post("/api/keys/{key_id}/activate")
def activate_key(key_id: int, db: Session = Depends(get_db)):
    """Re-activate a key."""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    key.is_active = True
    db.commit()
    return {"message": f"Key '{key.name}' activated"}


# ─── Usage Tracking ───────────────────────────────────────

@app.post("/api/keys/{key_id}/log-usage")
def log_usage(key_id: int, tokens: int = 0, cost: float = 0.0,
              endpoint: str = None, status_code: int = 200,
              response_time_ms: int = None, db: Session = Depends(get_db)):
    """Log usage for a key."""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")

    log = UsageLog(
        api_key_id=key_id,
        endpoint=endpoint,
        tokens_used=tokens,
        cost=cost,
        status_code=status_code,
        response_time_ms=response_time_ms,
    )
    db.add(log)

    # Update key totals
    key.total_requests += 1
    key.total_tokens += tokens
    key.total_cost += cost
    db.commit()
    return {"message": "Usage logged", "total_requests": key.total_requests}


@app.get("/api/keys/{key_id}/usage", response_model=APIKeyUsage)
def get_usage(key_id: int, limit: int = 20, db: Session = Depends(get_db)):
    """Get usage stats and recent logs for a key."""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")

    logs = db.query(UsageLog).filter(
        UsageLog.api_key_id == key_id
    ).order_by(UsageLog.created_at.desc()).limit(limit).all()

    return APIKeyUsage(
        key_id=key.id,
        name=key.name,
        provider=key.provider,
        total_requests=key.total_requests,
        total_tokens=key.total_tokens,
        total_cost=key.total_cost,
        recent_logs=[UsageLogResponse.model_validate(l) for l in logs],
    )


# ─── Dashboard ────────────────────────────────────────────

@app.get("/api/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    """Usage dashboard — overview of all keys and providers."""
    keys = db.query(APIKey).all()
    active = [k for k in keys if k.is_active]

    # Group by provider
    providers = {}
    for k in keys:
        if k.provider not in providers:
            providers[k.provider] = {"keys": 0, "requests": 0, "tokens": 0, "cost": 0.0}
        providers[k.provider]["keys"] += 1
        providers[k.provider]["requests"] += k.total_requests
        providers[k.provider]["tokens"] += k.total_tokens
        providers[k.provider]["cost"] += k.total_cost

    # Top keys by usage
    top = sorted(keys, key=lambda k: k.total_requests, reverse=True)[:5]

    return DashboardResponse(
        total_keys=len(keys),
        active_keys=len(active),
        total_requests=sum(k.total_requests for k in keys),
        total_tokens=sum(k.total_tokens for k in keys),
        total_cost=sum(k.total_cost for k in keys),
        providers=providers,
        top_keys=[{"name": k.name, "provider": k.provider, "requests": k.total_requests} for k in top],
    )


@app.get("/health")
def health():
    return {"status": "healthy", "service": "api-hub", "version": "1.0.0"}


@app.get("/")
def root():
    return {
        "service": "API Hub",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "keys": "/api/keys",
            "dashboard": "/api/dashboard",
            "health": "/health",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

# API Hub — Centralized API Key Manager

## Vision
A lightweight FastAPI service that manages API keys, tracks usage, and provides a unified gateway for multiple AI providers (OpenRouter, DeepSeek, Gemini, etc.).

## Tech Stack
- FastAPI + Uvicorn
- SQLite + SQLAlchemy
- Pydantic v2
- JWT Auth (PyJWT)

## Features
- Store and manage API keys for multiple providers
- Track usage per key (requests, tokens, cost)
- API key rotation and expiry
- Health monitoring for each provider
- Usage dashboard endpoint
- Rate limiting per key

## API Endpoints
- `POST /api/keys` — Add a new API key
- `GET /api/keys` — List all keys (masked)
- `GET /api/keys/{id}/usage` — Usage stats for a key
- `DELETE /api/keys/{id}` — Revoke a key
- `POST /api/keys/{id}/rotate` — Rotate a key
- `GET /api/health` — Check all provider health
- `GET /api/dashboard` — Usage summary

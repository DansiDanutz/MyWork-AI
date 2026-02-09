# API Hub Roadmap

## Phase 1: Foundation ← CURRENT
- [x] FastAPI setup with CORS
- [ ] Database models (APIKey, UsageLog)
- [ ] Basic CRUD endpoints (add/list/delete keys)
- [ ] Key masking (never expose full key in responses)
- [ ] Health endpoint

## Phase 2: Core Features
- [ ] Usage tracking middleware
- [ ] Provider health checks (ping endpoints)
- [ ] Key rotation endpoint
- [ ] Key expiry and auto-disable
- [ ] Rate limiting per key

## Phase 3: Dashboard & Polish
- [ ] Usage dashboard endpoint (totals, per-key, per-provider)
- [ ] Cost estimation
- [ ] Export usage as CSV
- [ ] Tests (unit + integration)
- [ ] Documentation

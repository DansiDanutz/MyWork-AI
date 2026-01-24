# MyWork Marketplace

> You Build. You Share. You Sell.

An AI-powered development marketplace where developers can monetize production-ready projects.

## Vision

Create an ecosystem where:
1. **Builders** create and sell their projects
2. **Buyers** get production-ready solutions
3. **Brain** grows smarter with every contribution
4. **Everyone** benefits from shared knowledge

## Business Model

- **Free:** Framework access, basic Brain
- **Pro ($49/mo):** Sell on marketplace, Cloud Brain
- **Fees:** 10% platform fee on sales

## Quick Start

```bash
# Development setup
cd backend && pip install -r requirements.txt
cd frontend && npm install

# Run development servers
./start-dev.sh
```

## Project Structure

```
marketplace/
├── .planning/           # GSD project management
│   ├── PROJECT.md       # Vision and scope
│   ├── REQUIREMENTS.md  # Feature requirements
│   ├── ROADMAP.md       # Development phases
│   └── STATE.md         # Current progress
├── backend/             # FastAPI backend
│   ├── api/             # API endpoints
│   ├── services/        # Business logic
│   └── models/          # Database models
├── frontend/            # Next.js frontend
│   ├── app/             # Pages (App Router)
│   └── components/      # UI components
└── docs/                # Documentation
    ├── BUSINESS_PLAN.md # Business strategy
    └── TECHNICAL_SPEC.md# Technical details
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, TypeScript, Tailwind |
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL (Supabase) |
| Auth | Clerk |
| Payments | Stripe Connect |
| Vector DB | Pinecone |
| Hosting | Vercel + Railway |

## Roadmap

| Phase | Duration | Focus |
|-------|----------|-------|
| 1. Foundation | 4 weeks | Auth, DB, API |
| 2. Products | 2 weeks | Listings, Search |
| 3. Payments | 2 weeks | Stripe, Orders |
| 4. Reviews | 2 weeks | Ratings, Dashboard |
| 5. Brain | 1 week | Knowledge API |
| 6. Subscriptions | 1 week | Tiers |
| 7. Launch | 2 weeks | Admin, Polish |

## Development

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL
- Stripe account
- Clerk account

### Environment Variables

```bash
# Backend
DATABASE_URL=postgresql://...
CLERK_SECRET_KEY=sk_...
STRIPE_SECRET_KEY=sk_...
ANTHROPIC_API_KEY=sk-ant-...

# Frontend
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_...
```

### Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Contributing

See `.planning/` for current status and next tasks.

## License

MIT - See LICENSE file.

---

Built with MyWork AI Framework.

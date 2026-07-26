# AI Dashboard

Your personal AI command center for tracking top AI content and automating
YouTube video creation.

## Quick Start

```bash

# From this project folder

./start.sh  # Mac/Linux
start.bat   # Windows

# Access

# Dashboard: http://localhost:3000

# API Docs: http://localhost:8000/docs

```markdown

## Features

### 1. YouTube AI Video Scraper

- Scrapes top AI/ML videos from YouTube every 8 hours
- Quality scoring based on views, likes, engagement
- Powered by Apify

### 2. AI News Aggregator

- Aggregates from TechCrunch, The Verge, MIT Tech Review
- Hacker News AI content integration
- Updates every 4 hours

### 3. GitHub Trending Projects

- Tracks top 20 AI/ML open source projects
- Weekly star growth tracking
- Updates every 12 hours

### 4. YouTube Automation Pipeline

- Prompt → DSPy Optimization → Claude Script → HeyGen Video → Upload
- Full approval workflow before YouTube upload

## Project Structure

```yaml
ai-dashboard/
├── .planning/          # GSD: Project-specific planning
├── backend/            # FastAPI backend
│   ├── main.py
│   ├── database/
│   ├── scrapers/
│   └── services/
├── frontend/           # Next.js 14 frontend
│   ├── app/
│   ├── components/
│   └── lib/
├── start.sh/start.bat  # Start scripts
├── RESEARCH.md         # Initial research notes
└── README.md           # This file

```markdown

## API Endpoints

| Endpoint | Method | Description |
| ---------- | -------- | ------------- |
| `/api/videos` | GET | Get top AI videos |
| `/api/videos/scrape` | POST | Trigger video scrape |
| `/api/news` | GET | Get latest AI news |
| `/api/news/trending` | GET | Get trending news |
| `/api/projects` | GET | Get top projects |
| `/api/automation` | GET/POST | Manage automations |
| `/api/stats` | GET | Dashboard statistics |

## Scheduler

| Task | Interval | Description |
| ------ | ---------- | ------------- |
| YouTube Scraper | 8 hours | Fetches top AI videos |
| News Aggregator | 4 hours | Aggregates AI news |
| GitHub Trending | 12 hours | Tracks trending projects |

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, SQLite, APScheduler, DSPy
**Frontend:** Next.js 15, TypeScript, Tailwind CSS

## Environment

Uses API keys from environment (backend `.env` by default via `load_dotenv()`):

- `APIFY_API_KEY` - YouTube scraping
- `ANTHROPIC_API_KEY` - Claude for scripts
- `HEYGEN_API_KEY` - AI video creation
- `YOUTUBE_API_KEY` - YouTube scraping fallback
- `YOUTUBE_OAUTH_CLIENT_ID` / `YOUTUBE_OAUTH_CLIENT_SECRET` /

  `YOUTUBE_OAUTH_REFRESH_TOKEN` - YouTube uploads

- `YOUTUBE_UPLOAD_PRIVACY_STATUS` - Upload privacy (default: unlisted)
- `SIMULATE_YOUTUBE_UPLOAD` - Set true to simulate uploads without OAuth
- `GITHUB_TOKEN` - Higher rate limits
- `AI_DASHBOARD_ADMIN_TOKEN` - At least 32 random characters; required as a bearer token
  for privileged scrape, automation, scheduler, and billing control routes
- `AI_DASHBOARD_BROWSER_USERNAME` - HTTP Basic username for the personal frontend
- `AI_DASHBOARD_BROWSER_SECRET` - Separate random value of at least 32 characters used to
  authenticate browser requests before the frontend can proxy to the backend
- `AI_DASHBOARD_BACKEND_URL` - Server-only backend origin used by the frontend proxy
- `AI_DASHBOARD_HOST` - Direct development-server bind address (default: `127.0.0.1`)

The frontend challenges every dashboard request with HTTP Basic authentication. Its
same-origin `/api/backend/*` route validates that separate browser credential, rejects
cross-origin mutations, and adds `AI_DASHBOARD_ADMIN_TOKEN` only on the server. Never expose
either secret through a `NEXT_PUBLIC_*` variable, and use this flow only over HTTPS outside
loopback development. The backend token and browser secret must not be the same value.

Before using `start.sh` or `start.bat`, export distinct `AI_DASHBOARD_ADMIN_TOKEN` and
`AI_DASHBOARD_BROWSER_SECRET` values of at least 32 characters. Production deployments must
configure those two secrets and `AI_DASHBOARD_BROWSER_USERNAME` in the provider before the
frontend is promoted.

### Dependency audit exception

DSPy currently resolves DiskCache 5.6.3, for which `pip-audit` reports
`PYSEC-2026-2447` (unsafe pickle deserialization) with no fixed release. The dashboard
disables DSPy disk caching before use and retains memory caching only. CI ignores exactly
that advisory for the deployed requirements and continues to block every other finding.
[Issue #6](https://github.com/DansiDanutz/MyWork-AI/issues/6) tracks removal of the
exception when a compatible fix ships.

## YouTube Upload Smoke Test

Run from the backend directory after setting OAuth env vars:

```bash
cd backend
python3 scripts/youtube_upload_smoke.py --dry-run

# Real upload (requires --confirm and a local video file)
python3 scripts/youtube_upload_smoke.py --video /path/to/video.mp4 --confirm
```

## Development

**Backend only:**

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload

```yaml

**Frontend only:**

```bash
cd frontend
npm run dev

```text

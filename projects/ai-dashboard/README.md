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

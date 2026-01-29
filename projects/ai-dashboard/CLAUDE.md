# AI Dashboard - AI Agent Instructions

## Project Overview

**Purpose**: Personal AI command center for content aggregation and automation.

**Status**: ✅ MVP Complete, Audited (Phase 7 complete)

**Tech Stack**:
- Backend: FastAPI + Python 3.9+
- Frontend: Next.js 14 + React + TypeScript
- Database: SQLite
- Scraping: BeautifulSoup, yt-dlp, Feedparser
- Automation: APScheduler, Python-OAuth2
- Deployment: Railway (backend), Vercel (frontend)

**Key Context**:
- This is a **personal tool**, not a multi-user SaaS
- The MVP is **complete and audited** - focus on polish, not new features
- All scrapers run on **scheduled intervals** via APScheduler
- The **YouTube automation pipeline** is the most complex part - be careful

---

## Quick Start for AI Agents

When working on the AI Dashboard:

1. **First, check current state**: Read `.planning/STATE.md`
2. **Understand the architecture**: Read `backend/` code structure
3. **For scraper work**: Focus on `backend/scrapers/` directory
4. **For frontend work**: Focus on `frontend/app/` directory
5. **For automation pipeline**: Focus on `backend/services/youtube_automation.py`
6. **For GSD operations**: Use `/gsd:progress` to see current status

**Start Commands**:
```bash
cd projects/ai-dashboard
./start.sh        # Mac/Linux
start.bat         # Windows
```

---

## Common Workflows

### Adding a New Scraper

**When to use**: User wants to add a new content source (website, API, feed)

**Steps**:
1. Create scraper file in `backend/scrapers/new_scraper.py`
2. Add database model to `backend/database/models.py` (if needed)
3. Add API endpoints in `backend/main.py` (GET/POST endpoints)
4. Create frontend page in `frontend/app/new-scraper/page.tsx`
5. Add scheduler job in `backend/main.py` (if scheduled)
6. Add environment variables to `backend/.env.example`
7. Test manually before deploying

**Example**:
```python
# backend/scrapers/new_source.py
from typing import List, Dict
from database.db import Session
from database.models import NewsItem
import requests
from bs4 import BeautifulSoup

class NewSourceScraper:
    def __init__(self):
        self.base_url = "https://example.com"

    def scrape(self) -> List[Dict]:
        """Scrape content from new source"""
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        items = []

        for article in soup.find_all('article'):
            items.append({
                'title': article.find('h2').text,
                'url': article.find('a')['href'],
                'summary': article.find('p').text,
                'source': 'New Source',
                'scraped_at': datetime.now()
            })

        return items
```

---

### Modifying Frontend Pages

**When to use**: User wants to change the UI/UX of a page

**Key Files**:
- Pages: `frontend/app/[page-name]/page.tsx`
- Components: `frontend/components/`
- API calls: Use `fetch()` to `http://localhost:8000/api/...`

**Steps**:
1. Identify the page to modify in `frontend/app/`
2. Check if there's a corresponding component in `frontend/components/`
3. Update the UI as needed
4. Test API calls are working
5. Check responsive design (mobile, tablet, desktop)

**Frontend Structure**:
```
frontend/
├── app/
│   ├── page.tsx              # Dashboard (main)
│   ├── news/
│   │   ├── page.tsx          # News listing
│   │   └── NewsClient.tsx    # Client component
│   ├── videos/
│   │   ├── page.tsx          # Videos listing
│   │   └── VideosClient.tsx  # Client component
│   ├── projects/
│   │   ├── page.tsx          # Projects listing
│   │   └── ProjectsClient.tsx
│   ├── youtube-bot/
│   │   ├── page.tsx          # YouTube bot main
│   │   └── [id]/
│   │       └── page.tsx      # Automation detail
│   ├── settings/
│   │   └── page.tsx          # Settings page
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/
│   ├── AppShell.tsx          # Main app shell
│   └── Sidebar.tsx           # Navigation sidebar
└── lib/
    └── api.ts                # API utility functions
```

---

### Working on YouTube Automation Pipeline

**When to use**: User wants to modify YouTube upload/automation

**⚠️ CRITICAL**: This is the most complex part of the system. Be careful!

**Key Files**:
- `backend/services/youtube_automation.py` - Main automation logic
- `backend/.env` - OAuth credentials (NEVER commit)
- `backend/.env.example` - Template for credentials
- `backend/main.py` - API endpoints for automation

**How it Works**:
1. User authenticates via YouTube OAuth
2. System stores OAuth token in database
3. Automation jobs are scheduled via APScheduler
4. Jobs use OAuth token to upload videos to YouTube
5. Status is tracked in database

**Steps to Modify**:
1. **Always test OAuth flow first** - Don't break authentication
2. Check `backend/.env.example` for required environment variables
3. Read `youtube_automation.py` completely before making changes
4. Test with small uploads before large automation jobs
5. Check quota limits (YouTube API has daily limits)

**Common Tasks**:
- Add new automation type → Create new function in `youtube_automation.py`
- Modify upload parameters → Update video metadata in automation function
- Add new trigger → Add new API endpoint in `main.py`
- Debug OAuth issues → Check token storage in database

---

### Modifying the Scheduler

**When to use**: User wants to change scraping intervals or add scheduled jobs

**Key File**: `backend/main.py` (lines with `@scheduler.scheduled_job`)

**How it Works**:
- APScheduler runs in background
- Jobs are defined with cron-like syntax
- Each job calls a scraper function
- Results are stored in database

**Example**:
```python
# Add new scheduled job
@scheduler.scheduled_job(
    'cron',
    hour='*/6',  # Every 6 hours
    id='new_source_scraper'
)
def run_new_source_scraper():
    """Run new source scraper every 6 hours"""
    from scrapers.new_source import NewSourceScraper
    scraper = NewSourceScraper()
    items = scraper.scrape()
    # Store in database...
```

**Steps**:
1. Define job with `@scheduler.scheduled_job` decorator
2. Use cron syntax for timing
3. Call scraper function
4. Store results in database
5. Add error handling (try/except)

---

## Project-Specific Context

### This is a Personal Tool

- **NOT multi-user**: No authentication system (no login/logout)
- **NOT a SaaS**: No user accounts, no subscriptions
- **Single user**: You (the owner) are the only user
- **Focus on utility**: Make it useful for one person, not many

### MVP is Complete

- All core features are implemented
- All phases are complete (Phase 1-7)
- Project has been audited
- **Focus on polish**: Bug fixes, performance, UX improvements
- **Avoid new features**: Unless they're critical

### YouTube Automation is Complex

The YouTube upload automation is the most complex part:
- OAuth 2.0 authentication flow
- Token management and refresh
- Video upload with progress tracking
- Error handling for quota limits
- Background job processing

**Be extra careful when modifying this!**

---

## File Organization Guide

### Backend Structure

```
backend/
├── main.py                 # FastAPI app, routes, scheduler
├── database/
│   ├── db.py              # Database connection
│   └── models.py          # SQLAlchemy models
├── scrapers/
│   ├── github_trending.py # GitHub trending scraper
│   ├── news_aggregator.py # News feed scraper
│   └── youtube_scraper.py # YouTube video scraper
├── services/
│   ├── youtube_automation.py   # YouTube upload automation
│   ├── scheduler_service.py    # Scheduler management
│   └── prompt_optimizer.py     # AI prompt optimization
├── .env                   # Environment variables (NEVER COMMIT)
├── .env.example           # Environment template
└── requirements.txt       # Python dependencies
```

### Frontend Structure

```
frontend/
├── app/
│   ├── page.tsx           # Dashboard (main page)
│   ├── layout.tsx         # Root layout
│   ├── news/              # News pages
│   ├── videos/            # Video pages
│   ├── projects/          # Project pages
│   ├── youtube-bot/       # YouTube automation pages
│   ├── settings/          # Settings pages
│   └── globals.css        # Global styles
├── components/
│   ├── AppShell.tsx       # Main app component
│   └── Sidebar.tsx        # Navigation
├── lib/
│   └── api.ts             # API utility
├── tailwind.config.js     # Tailwind CSS config
├── next.config.js         # Next.js config
└── package.json           # NPM dependencies
```

---

## Integration with Framework Documentation

This `CLAUDE.md` is **project-specific** and works with the framework `CLAUDE.md`:

1. **Framework CLAUDE.md** (`/Users/dansidanutz/Desktop/MyWork/CLAUDE.md`):
   - How to use GSD commands
   - How to use WAT workflows
   - How to use Autocoder
   - How to use framework tools (mw, brain, etc.)

2. **This CLAUDE.md** (project-specific):
   - How to work on ai-dashboard specifically
   - Project-specific workflows
   - File organization
   - Important notes

**When to use which**:
- Use framework CLAUDE.md for: GSD commands, framework tools, general patterns
- Use this CLAUDE.md for: ai-dashboard specific work, file locations, workflows

---

## Current Status

Check `.planning/STATE.md` for latest status, but generally:
- ✅ Phase 1: Foundation Setup (Complete)
- ✅ Phase 2: Content Sources (Complete)
- ✅ Phase 3: Dashboard UI (Complete)
- ✅ Phase 4: Automation (Complete)
- ✅ Phase 5: YouTube Bot (Complete)
- ✅ Phase 6: Prompt Optimization (Complete)
- ✅ Phase 7: Testing & Polish (Complete)
- ✅ Audit Passed

---

## Important Notes

1. **No Authentication**: This is a personal tool with no login system
2. **SQLite Database**: Uses SQLite (not PostgreSQL) for simplicity
3. **Scheduled Scraping**: All scrapers run on intervals via APScheduler
4. **YouTube OAuth**: Uses OAuth 2.0 for YouTube uploads - be careful with tokens
5. **Deployment**: Backend on Railway, Frontend on Vercel
6. **Focus on Polish**: MVP is complete - fix bugs, improve UX, don't add new features

---

## Testing

**Backend Testing**:
```bash
cd backend
pytest                  # Run all tests
pytest -v              # Verbose output
pytest tests/test_scrapers.py  # Test specific file
```

**Manual Testing**:
1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser: `http://localhost:3000`
4. Test all features manually

---

## Common Issues

### Scraper Not Working
- Check if target website structure changed
- Verify scraping logic in `scrapers/*.py`
- Check database connection
- Look at error logs in backend console

### YouTube Upload Failing
- Check OAuth token is valid (stored in database)
- Verify quota limits not exceeded
- Check video format is supported
- Look at error logs for specific error

### Frontend Not Loading
- Check backend is running on port 8000
- Check API calls are correct (`/api/...`)
- Look at browser console for errors
- Verify environment variables are set

---

## When in Doubt

1. Check `.planning/STATE.md` for current status
2. Check `.planning/PROJECT.md` for project vision
3. Check `.planning/ROADMAP.md` for what's been done
4. Check framework CLAUDE.md for general patterns
5. Check this CLAUDE.md for project-specific instructions

---

## Summary

This is a **complete personal AI dashboard**. Focus on:
- ✅ Bug fixes
- ✅ Performance improvements
- ✅ UX polish
- ❌ NOT new features (unless critical)

When in doubt, check the planning docs and ask questions!

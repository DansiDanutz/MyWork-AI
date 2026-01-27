# External Integrations

**Analysis Date:** 2026-01-24

## APIs & External Services

**Web Scraping & Content Collection:**

- Apify - YouTube video scraping and web scraping
  - SDK/Client: `apify-client` 1.6.0
  - Auth: `APIFY_API_KEY` environment variable
  - Used in: `backend/scrapers/youtube_scraper.py`
  - Purpose: Scrapes top AI-related YouTube videos based on search queries

**AI/LLM & Content Generation:**

- Anthropic Claude - LLM for script and content generation
  - SDK/Client: `anthropic` 0.18.1
  - Auth: `ANTHROPIC_API_KEY` environment variable
  - Used in: `backend/services/prompt_optimizer.py`, `backend/services/youtube_automation.py`
  - Models: claude-3-5-sonnet-20241022
  - DSPy Framework: Uses DSPy 2.4.0 for prompt engineering and optimization

**Video Generation:**

- HeyGen - AI video generation from scripts
  - Auth: `HEYGEN_API_KEY` environment variable
  - Used in: `backend/services/youtube_automation.py`
  - Purpose: Converts video scripts to AI-generated videos

**YouTube Integration:**

- YouTube Data API v3 - For video metadata and uploads
  - SDK/Client: `google-api-python-client` 2.118.0
  - Auth: `YOUTUBE_API_KEY` environment variable
  - OAuth: `google-auth-oauthlib` 1.2.0 for OAuth flows
  - Used in: `backend/services/youtube_automation.py`
  - Capabilities: Upload videos, update metadata, search videos

**News Aggregation:**

- RSS Feeds (multiple sources configured):
  - TechCrunch AI: `https://techcrunch.com/category/artificial-intelligence/feed/`
  - The Verge AI: `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml`
  - MIT Technology Review: `https://www.technologyreview.com/feed/`
  - VentureBeat AI: `https://venturebeat.com/category/ai/feed/`
  - Towards Data Science: `https://towardsdatascience.com/feed`
  - Google AI Blog: `https://blog.google/technology/ai/rss/`
  - OpenAI Blog: `https://openai.com/blog/rss/`
  - Anthropic Research: `https://www.anthropic.com/feed.xml`
  - Hugging Face Blog: `https://huggingface.co/blog/feed.xml`
  - SDK/Client: `feedparser` 6.0.10
  - Used in: `backend/scrapers/news_aggregator.py`

**Hacker News API:**

- Base URL: `https://hacker-news.firebaseio.com/v0` (Firebase API)
- Algolia Search: `https://hn.algolia.com/api/v1`
- HTTP Client: `httpx` 0.25.1+
- Used in: `backend/scrapers/news_aggregator.py`
- Purpose: Aggregates AI-related content from Hacker News

**GitHub API:**

- Trending projects and repository data
- Auth: `GITHUB_TOKEN` (optional, for higher rate limits)
- Used in: `backend/scrapers/github_trending.py`
- Purpose: Tracks top open-source AI/ML projects

## Data Storage

**Databases:**

- SQLite 3
  - Type: Embedded relational database
  - Location: `backend/dashboard.db`
  - Connection: SQLAlchemy ORM (`sqlalchemy` 2.0.25)
  - Async Driver: `aiosqlite` 0.19.0
  - Tables:
    - `youtube_videos` - Scraped YouTube videos with engagement metrics
    - `ai_news` - Aggregated news articles
    - `github_projects` - Trending GitHub projects
    - `youtube_automation` - YouTube video automation pipeline records
    - `scraper_logs` - Execution logs of scraper jobs

**File Storage:**

- Thumbnail URLs stored in database (from YouTube, RSS feeds, GitHub)
- Images proxied through Next.js (allowed domains: `i.ytimg.com`, `img.youtube.com`, `avatars.githubusercontent.com`)

**Caching:**

- Not detected

## Authentication & Identity

**Auth Provider:**

- Custom (no centralized auth system)

**Implementation:**

- No user authentication system in current codebase
- Environment-based API key management via `.env`
- Frontend connects directly to FastAPI backend without auth layer

**OAuth Integration:**

- Google OAuth via `google-auth-oauthlib` 1.2.0 for YouTube uploads
- Configured for Google Cloud API credentials

## Monitoring & Observability

**Error Tracking:**

- Not detected (no Sentry, Rollbar, etc.)

**Logs:**

- Python logging module (backend)
  - Format: `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"`
  - Level: INFO
  - Used in: All backend services and scrapers
- Browser console (frontend)
  - Error logging in API calls (`/Users/dansidanutz/Desktop/MyWork/frontend/app/page.tsx`)

**Scraper Monitoring:**

- `ScraperLog` model tracks execution status, items scraped, errors, and timestamps
- Accessible via `/api/stats` and `/api/scheduler/status` endpoints

## CI/CD & Deployment

**Hosting:**

- Frontend: Can run on any Node.js hosting (Vercel, Netlify, self-hosted)
- Backend: Can run on any Python-capable server (AWS, Heroku, self-hosted)
- Development: Local development with `npm run dev` and `python main.py`

**CI Pipeline:**

- Not detected (no GitHub Actions, GitLab CI, etc.)

**Start Scripts:**

- `/Users/dansidanutz/Desktop/MyWork/start.sh` - Shell script for Mac/Linux
- `/Users/dansidanutz/Desktop/MyWork/start.bat` - Batch script for Windows

## Environment Configuration

**Required env vars:**

**Frontend:**

- `NEXT_PUBLIC_API_URL` - Backend API URL (defaults to `http://localhost:8000`)

**Backend:**

- `APIFY_API_KEY` - Required for YouTube scraping (get at: https://console.apify.com/)
- `ANTHROPIC_API_KEY` - Required for Claude-powered content generation (get at: https://console.anthropic.com/)
- `YOUTUBE_API_KEY` - Required for YouTube uploads (get at: https://console.cloud.google.com/apis/credentials)
- `HEYGEN_API_KEY` - Required for video generation (get at: https://app.heygen.com/settings)
- `GITHUB_TOKEN` - Optional, for higher GitHub API rate limits (generate at: https://github.com/settings/tokens)

**Secrets location:**

- Backend: `.env` file in `/Users/dansidanutz/Desktop/MyWork/backend/`
- Template: `.env.example` files provided
- Frontend: Environment variables passed at build time (NEXT_PUBLIC_* prefix)

## Webhooks & Callbacks

**Incoming:**

- Not detected

**Outgoing:**

- YouTube upload via YouTube Data API (not technically a webhook, but HTTP POST)
- HeyGen video generation requests (HTTP POST to HeyGen API)

## Scheduled Tasks

**APScheduler Integration:**

- Framework: `apscheduler` 3.10.4
- Used in: `backend/services/scheduler_service.py`
- Jobs:
  - YouTube scraper - runs every 8 hours
  - News aggregator - runs every 4 hours
  - GitHub trending scraper - runs every 12 hours
- Accessed via `/api/scheduler/status` endpoint

## API Communication

**Frontend to Backend:**

- HTTP REST API using axios (`axios` 1.6.5)
- Base URL configured in `frontend/lib/api.ts`
- Endpoints:
  - `GET /api/videos` - Fetch scraped videos
  - `GET /api/news` - Fetch news articles
  - `GET /api/news/trending` - Get trending news
  - `GET /api/projects` - Fetch GitHub projects
  - `GET /api/projects/trending` - Get trending projects
  - `GET /api/automation` - List video automations
  - `GET /api/automation/{id}` - Get automation details
  - `POST /api/automation` - Create new automation
  - `PATCH /api/automation/{id}` - Update automation
  - `POST /api/automation/{id}/approve` - Approve and upload to YouTube
  - `GET /api/stats` - Dashboard statistics
  - `POST /api/{videos|news|projects}/scrape` - Trigger scraper manually
  - `GET /api/scheduler/status` - Get scheduler status

**CORS Configuration:**

- Allowed origins: `http://localhost:3000`, `http://127.0.0.1:3000`
- Allowed methods: All (*)
- Allowed headers: All (*)
- Credentials: Enabled

---

*Integration audit: 2026-01-24*

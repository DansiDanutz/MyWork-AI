# Architecture

**Analysis Date:** 2026-01-24

## Pattern Overview

**Overall:** Three-tier client-server architecture with specialized data
collection and AI automation pipelines.

**Key Characteristics:**

- **Frontend-Backend Separation**: Next.js frontend communicates with FastAPI

  backend via REST API

- **Scheduled Data Collection**: Automated scrapers (YouTube, News, GitHub) on

  configurable intervals

- **AI-Powered Automation**: Multi-step video generation pipeline using Claude,

  HeyGen, and YouTube APIs

- **Responsive UI**: Dashboard with stateful data fetching and manual trigger

  options

- **Persistent Storage**: SQLite database with ORM for all collected data and

  automation state

## Layers

**Presentation Layer (Frontend):**

- Purpose: User interface for browsing content, managing automations, and

  triggering operations

- Location: `frontend/app/`, `frontend/components/`
- Contains: Next.js pages, React components, TypeScript types
- Depends on: REST API (`lib/api.ts`), external CDNs for images
- Used by: End users (browser)

**API Layer (Backend):**

- Purpose: REST endpoints for data retrieval, scraper control, and automation

  management

- Location: `backend/main.py` (all endpoints defined here)
- Contains: FastAPI route handlers, Pydantic request/response models
- Depends on: Database layer, service layer, scrapers
- Used by: Frontend, external integrations

**Business Logic / Service Layer:**

- Purpose: Complex operations like video automation pipeline, prompt

  optimization, scheduling

- Location: `backend/services/` (SchedulerService, YouTubeAutomationService,

  PromptOptimizer)

- Contains: Service classes with async methods
- Depends on: Database, external APIs (Anthropic, HeyGen, YouTube)
- Used by: API handlers, scheduled jobs

**Data Collection Layer:**

- Purpose: Fetch data from external sources and store in database
- Location: `backend/scrapers/` (YouTubeScraper, NewsAggregator,

  GitHubTrendingScraper)

- Contains: Scraper classes with async methods
- Depends on: Database, external APIs (YouTube, HackerNews, GitHub, Apify)
- Used by: SchedulerService (scheduled), API handlers (manual triggers)

**Data Layer (Database):**

- Purpose: Persistent storage of scraped content, automations, and operational

  logs

- Location: `backend/database/` (models.py, db.py)
- Contains: SQLAlchemy ORM models, database connection management
- Depends on: SQLite (local file-based)
- Used by: All services, API handlers

## Data Flow

**Data Collection Flow (Scrapers → Database → API → Frontend):**

1. **Scheduler** initiates scraper (every 4-12 hours) OR manual trigger via API
2. **Scraper** fetches data from external source (YouTube API, RSS, GitHub API,

Apify)

1. **Scraper** calculates metrics (quality score for videos, trending score for

projects)

1. **Scraper** stores data in database via SQLAlchemy ORM
2. **API endpoint** (`/api/videos`, `/api/news`, `/api/projects`) queries

database

1. **Frontend** fetches via `lib/api.ts` and displays with filters/sorting
2. **User** views data, can trigger manual scrape to refresh

**Video Automation Flow (Prompt → Script → Video → YouTube):**

1. **User** enters prompt in `/youtube-bot` modal
2. **Frontend** calls `POST /api/automation` with prompt
3. **YouTubeAutomationService.create_video_draft()** executes:
   - Optimize prompt using DSPy (PromptOptimizer)
   - Generate video content (title, description, script, tags) using Claude
   - Store draft record in `youtube_automation` table
4. **Frontend** displays draft with edit capabilities
5. **User** reviews and clicks generate-video
6. **YouTubeAutomationService.generate_heygen_video()** executes:
   - Call HeyGen API with script
   - Poll for completion
   - Update database with video URL
7. **User** approves video
8. **YouTubeAutomationService.approve_and_upload()** executes:
   - Upload to YouTube using YouTube API
   - Update status to "uploaded"
   - Store YouTube URL

**State Management:**

- **Frontend State**: React `useState` for UI state (loading, errors, form

  inputs)

- **Backend State**: Database records (YouTubeAutomation with status field) track

  pipeline progress

- **Async Operations**: AsyncIO scheduler manages background tasks, async/await

  for API calls

- **No Real-time Updates**: Frontend polls via manual refresh or fetch calls; no

  WebSocket

## Key Abstractions

**Scraper Classes** (YouTubeScraper, NewsAggregator, GitHubTrendingScraper):

- Purpose: Encapsulate data fetching and storage logic for each source
- Examples: `backend/scrapers/youtube_scraper.py`,

  `backend/scrapers/news_aggregator.py`

- Pattern: Class with async methods that fetch, transform, calculate metrics, and

  persist to database

**Service Classes** (YouTubeAutomationService, SchedulerService,
PromptOptimizer):

- Purpose: Orchestrate complex workflows across multiple external services
- Examples: `backend/services/youtube_automation.py`,

  `backend/services/scheduler_service.py`

- Pattern: Async service with methods for each step of multi-step processes

**ORM Models** (YouTubeVideo, AINews, GitHubProject, YouTubeAutomation,
ScraperLog):

- Purpose: Represent database tables with calculated properties and relationships
- Examples: `backend/database/models.py`
- Pattern: SQLAlchemy declarative models with methods like

  `calculate_quality_score()`, `calculate_trending_score()`

**API Response Types** (Pydantic models):

- Purpose: Define and validate request/response schemas
- Examples: VideoResponse, NewsResponse, ProjectResponse, AutomationResponse
- Pattern: Pydantic BaseModel with typed fields, `Config.from_attributes = True`

  for ORM conversion

**API Client** (`frontend/lib/api.ts`):

- Purpose: Centralized axios instance and typed functions for all backend calls
- Example: `getVideos()`, `createAutomation()`, `approveAutomation()`
- Pattern: Export axios instance + typed async functions

## Entry Points

**Backend Entry:**

- Location: `backend/main.py`
- Triggers: `uvicorn run main:app` or `python main.py`
- Responsibilities: Initialize FastAPI app, register CORS middleware, set up

  lifespan events (init_db, start scheduler), define all API routes

**Frontend Entry:**

- Location: `frontend/app/page.tsx` (root dashboard)
- Triggers: Browser navigation to `http://localhost:3000`
- Responsibilities: Fetch and display stats, show recent scrapes, provide quick

  actions to navigate to other pages

**Scheduler Entry:**

- Location: `backend/services/scheduler_service.py` (SchedulerService.start())
- Triggers: Called during FastAPI lifespan startup
- Responsibilities: Create AsyncIOScheduler, register 3 jobs (YouTube every 8h,

  News every 4h, GitHub every 12h), start scheduler

## Error Handling

**Strategy:** Try-catch at multiple levels with graceful degradation.

**Patterns:**

- **Frontend**: Try-catch in fetch functions, set error state, display error UI

  with retry button

- **Backend**: Try-catch in route handlers, raise HTTPException with appropriate

  status codes (404, 500)

- **Services**: Log errors, update database status field to "failed", allow

  manual retry via API

- **Scrapers**: Log errors during fetch, log to ScraperLog table with

  error_message field, continue to next scraper

## Cross-Cutting Concerns

**Logging:**

- Python `logging` module configured in `main.py` with format `"%(asctime)s -

  %(name)s - %(levelname)s - %(message)s"`

- All services and scrapers log info/error messages
- Frontend uses `console.error()` for debugging

**Validation:**

- Frontend: Pydantic models validate request payloads before sending to API
- Backend: Pydantic models validate incoming requests in route handlers
- Database: Foreign keys, unique constraints on natural keys (video_id, url,

  repo_id)

**Authentication:**

- Not implemented. API accessible from localhost:3000. External APIs (YouTube,

  Anthropic, HeyGen) use API keys stored in `.env`

**CORS:**

- Configured in `main.py` to allow requests from `http://localhost:3000` and

  `http://127.0.0.1:3000`

---

## Architecture Analysis

**Generated:** 2026-01-24

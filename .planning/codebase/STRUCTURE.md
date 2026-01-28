# Codebase Structure

**Analysis Date:** 2026-01-24

## Directory Layout

```markdown

/Users/dansidanutz/Desktop/MyWork/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # Entry point, all API routes, FastAPI app setup
│   ├── requirements.txt        # Python dependencies
│   ├── .env                   # Environment variables (API keys, secrets)
│   ├── database/
│   │   ├── __init__.py        # Exports get_db, init_db, models
│   │   ├── models.py          # SQLAlchemy ORM models (5 tables)
│   │   └── db.py              # Database connection, session factories
│   ├── scrapers/
│   │   ├── __init__.py        # Exports all scraper classes
│   │   ├── youtube_scraper.py # YouTubeScraper class
│   │   ├── news_aggregator.py # NewsAggregator class
│   │   └── github_trending.py # GitHubTrendingScraper class
│   ├── services/
│   │   ├── __init__.py        # Exports all service classes
│   │   ├── scheduler_service.py    # SchedulerService (APScheduler wrapper)
│   │   ├── youtube_automation.py   # YouTubeAutomationService (multi-step pipeline)
│   │   └── prompt_optimizer.py     # PromptOptimizer (DSPy + Claude)
│   ├── venv/                  # Python virtual environment
│   └── dashboard.db           # SQLite database (created on first run)
│
├── frontend/                   # Next.js React frontend
│   ├── app/                   # Next.js app directory (file-based routing)
│   │   ├── layout.tsx         # Root layout with Sidebar and main content area
│   │   ├── page.tsx           # Dashboard home page (stats overview)
│   │   ├── globals.css        # Global Tailwind styles
│   │   ├── videos/
│   │   │   └── page.tsx       # Videos browsing page with scrape trigger
│   │   ├── news/
│   │   │   └── page.tsx       # News browsing page with scrape trigger
│   │   ├── projects/
│   │   │   └── page.tsx       # GitHub projects browsing page
│   │   └── youtube-bot/
│   │       └── page.tsx       # Video automation creation and management
│   ├── components/
│   │   └── Sidebar.tsx        # Navigation sidebar component
│   ├── lib/
│   │   └── api.ts             # Axios client, API types, API functions
│   ├── package.json           # NPM dependencies
│   ├── next.config.js         # Next.js config (image domains)
│   ├── tailwind.config.js     # Tailwind CSS config
│   ├── tsconfig.json          # TypeScript config
│   └── node_modules/          # NPM packages
│
├── tools/                     # Python scripts for WAT framework
│   └── [tool scripts]         # External data processing tools
│
├── workflows/                 # WAT framework workflow definitions
│   └── [workflow files]       # Markdown SOPs
│
├── .planning/
│   └── codebase/              # Codebase analysis documents
│                              # (ARCHITECTURE.md, STRUCTURE.md, etc.)
│
├── .claude/                   # Claude Code config
├── .tmp/                      # Temporary files (regenerated)
├── .env                       # Root environment variables
├── .mcp.json                  # MCP server config
├── CLAUDE.md                  # Project instructions (WAT framework)
└── README.md                  # Project documentation

```text

## Directory Purposes

**backend/:**

- Purpose: FastAPI REST API server, data collection, automation pipeline
- Contains: Python source code, database, configuration
- Key files: `main.py` (all routes), `database/models.py` (ORM), `services/`

  (business logic)

**backend/database/:**

- Purpose: Data persistence layer
- Contains: SQLAlchemy models, connection management
- Key files: `models.py` (5 ORM tables), `db.py` (session management)

**backend/scrapers/:**

- Purpose: External data collection and storage
- Contains: Async scraper classes for YouTube, News, GitHub
- Key files: `youtube_scraper.py`, `news_aggregator.py`, `github_trending.py`

**backend/services/:**

- Purpose: Business logic, scheduling, complex workflows
- Contains: Service classes for automation pipeline, scheduler, prompt

  optimization

- Key files: `youtube_automation.py` (main pipeline), `scheduler_service.py`

  (APScheduler), `prompt_optimizer.py` (DSPy)

**frontend/:**

- Purpose: User interface
- Contains: Next.js app, React components, styles
- Key files: `app/page.tsx` (dashboard), `components/Sidebar.tsx` (navigation),

  `lib/api.ts` (API client)

**frontend/app/:**

- Purpose: Next.js pages using file-based routing
- Contains: Page components (one per route)
- Key files: `page.tsx` (routes: /, /videos, /news, /projects, /youtube-bot)

**frontend/components/:**

- Purpose: Reusable React components
- Contains: Sidebar navigation, shared UI components
- Key files: `Sidebar.tsx` (navigation menu)

**frontend/lib/:**

- Purpose: Frontend utilities and API client
- Contains: Typed axios instance, API functions, TypeScript types
- Key files: `api.ts` (all API calls)

**tools/, workflows/, .planning/:**

- Purpose: WAT framework support files (not core application)
- Contains: External scripts, markdown SOPs, analysis documents

## Key File Locations

**Entry Points:**

- `backend/main.py`: FastAPI app initialization and all API route definitions
- `frontend/app/page.tsx`: Root dashboard page (home route)
- `frontend/app/layout.tsx`: Root layout wrapper with Sidebar

**Configuration:**

- `backend/.env`: Backend API keys and secrets
- `frontend/next.config.js`: Next.js settings (image domains, etc.)
- `backend/requirements.txt`: Python dependencies

**Core Logic:**

- `backend/services/youtube_automation.py`: Complete video automation pipeline

  (5-step process)

- `backend/services/scheduler_service.py`: Background job scheduler with 3 jobs
- `backend/scrapers/youtube_scraper.py`: YouTube data fetching and storage
- `backend/database/models.py`: All 5 ORM models (YouTubeVideo, AINews,

  GitHubProject, YouTubeAutomation, ScraperLog)

**Testing:**

- No test files found in codebase

**API Communication:**

- `frontend/lib/api.ts`: All frontend-to-backend API calls (30+ functions

  exported)

- `backend/main.py`: All REST endpoints (GET /api/videos, POST /api/automation,

  etc.)

## Naming Conventions

**Files:**

- Python: snake_case (youtube_scraper.py, scheduler_service.py)
- TypeScript/React: PascalCase for components (Sidebar.tsx), camelCase for

  utilities (api.ts)

- Configuration: lowercase with dots (next.config.js, tailwind.config.js)

**Directories:**

- lowercase, plural for collections (scrapers/, services/, components/)
- lowercase, feature-based naming (youtube-bot/, app/)

**Classes:**

- PascalCase (YouTubeScraper, NewsAggregator, GitHubTrendingScraper,

  SchedulerService, YouTubeAutomationService)

**Functions/Methods:**

- snake_case in Python (scrape_videos, get_top_videos, calculate_quality_score)
- camelCase in TypeScript (getVideos, createAutomation, getAutomations)

**Database Tables:**

- PascalCase class name, snake_case table name: `class YouTubeVideo:

  __tablename__ = "youtube_videos"`

**Route Endpoints:**

- kebab-case with `/api/` prefix: `/api/videos`, `/api/news`, `/api/projects`,

  `/api/automation`, `/api/scheduler`

## Where to Add New Code

**New Data Source (e.g., Twitter scraper):**

- Implementation: `backend/scrapers/twitter_scraper.py` (extend with class

  inheriting from base or similar pattern)

- Database: Add new model in `backend/database/models.py` (e.g., TwitterPost)
- API: Add routes in `backend/main.py` (GET `/api/twitter`, POST

  `/api/twitter/scrape`)

- Scheduler: Register new job in `backend/services/scheduler_service.py`
- Frontend: Add new page in `frontend/app/twitter/page.tsx`, add to Sidebar

  navigation

**New API Endpoint:**

- Location: Add route in `backend/main.py` (follow existing pattern: define

  Pydantic model, route handler, HTTP method)

- Response Type: Define Pydantic model if needed (e.g., TwitterResponse)
- Frontend: Add function in `frontend/lib/api.ts` to call new endpoint

**New Frontend Page:**

- Location: `frontend/app/[feature]/page.tsx` (e.g., `app/settings/page.tsx`)
- Navigation: Add to navigation array in `frontend/components/Sidebar.tsx`
- API calls: Use functions from `frontend/lib/api.ts`

**New Service/Business Logic:**

- Location: `backend/services/[service_name].py`
- Pattern: Async class with methods for operations
- Usage: Import in `backend/main.py` route handlers or

  `backend/services/scheduler_service.py`

**Utilities (Helper Functions):**

- Python: `backend/utils/` or as methods on service classes
- TypeScript: `frontend/lib/` (add to `api.ts` or create `frontend/lib/utils.ts`)

**Reusable Components:**

- Location: `frontend/components/[ComponentName].tsx`
- Usage: Import in pages under `frontend/app/`

## Special Directories

**backend/venv/:**

- Purpose: Python virtual environment
- Generated: Yes (created by `python -m venv venv`)
- Committed: No (in .gitignore)

**frontend/node_modules/:**

- Purpose: NPM package dependencies
- Generated: Yes (created by `npm install`)
- Committed: No (in .gitignore)

**frontend/.next/:**

- Purpose: Next.js build artifacts and cache
- Generated: Yes (created by `npm run build`)
- Committed: No (in .gitignore)

**backend/dashboard.db:**

- Purpose: SQLite database file
- Generated: Yes (created on first API startup via `init_db()`)
- Committed: No (should be in .gitignore or regenerated)

**.env files:**

- Purpose: Environment variables (API keys, database URL, etc.)
- Generated: No (must be created manually)
- Committed: No (security - credentials should never be in git)

**.planning/codebase/:**

- Purpose: Generated codebase analysis documents
- Generated: Yes (created by `/gsd:map-codebase` command)
- Committed: Yes (these are reference documents)

---

*Structure analysis: 2026-01-24*

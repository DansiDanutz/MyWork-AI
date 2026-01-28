# Coding Conventions

**Analysis Date:** 2026-01-24

## Naming Patterns

**Files:**

- Components: PascalCase with .tsx extension (e.g., `Sidebar.tsx`)
- Pages: lowercase with hyphens in directories (e.g., `app/youtube-bot/page.tsx`,

  `app/projects/page.tsx`)

- Utilities/Services: camelCase with .ts extension (e.g., `api.ts`,

  `youtube_scraper.py`)

- Backend Python modules: snake_case (e.g., `youtube_automation.py`,

  `prompt_optimizer.py`)

**Functions:**

- React components: PascalCase (e.g., `Dashboard`, `Sidebar`, `VideosPage`)
- Async functions: descriptive camelCase with `async` prefix where applicable

  (e.g., `fetchStats`, `handleScrape`, `create_video_draft`)

- Service methods: camelCase for JS/TS, snake_case for Python (e.g.,

  `getVideos()`, `scrape_videos()`)

- Utility functions: camelCase for JS/TS (e.g., `formatNumber()`)

**Variables:**

- State: camelCase (e.g., `videos`, `loading`, `error`, `showCreateModal`)
- Database columns: snake_case in models (e.g., `video_id`, `channel_name`,

  `quality_score`)

- Constants: UPPER_SNAKE_CASE for Python (e.g., `AI_SEARCH_QUERIES`), const

  declarations in TS

- UI-related vars: camelCase (e.g., `targetAudience`, `videoLength`)

**Types:**

- Interfaces/Types: PascalCase (e.g., `Video`, `News`, `Project`, `Automation`,

  `Stats`)

- Database models: PascalCase class names (e.g., `YouTubeVideo`, `AINews`,

  `GitHubProject`)

- Pydantic models: PascalCase (e.g., `VideoResponse`, `NewsResponse`,

  `AutomationCreate`)

## Code Style

**Formatting:**

- Frontend uses Next.js defaults (ESLint with Next.js config)
- No explicit Prettier config found - relies on default Next.js formatting
- TypeScript strict mode enabled (`strict: true` in tsconfig.json)
- Python uses standard PEP 8 conventions (observed in all Python files)

**Linting:**

- Frontend: `eslint 8.56.0` with `eslint-config-next` package
- Run with: `npm run lint` in frontend directory
- Python: No formal linting configuration found, but code follows PEP 8 standards

**Line length:** Frontend uses default (typically 120 for TypeScript), Python
varies but generally under 100 chars

## Import Organization

**Order (Frontend - TypeScript/React):**

1. React/Next.js built-ins (e.g., `import { useEffect, useState } from 'react'`)
2. Next.js imports (e.g., `import Link from 'next/link'`)
3. Third-party libraries (e.g., `import axios from 'axios'`)
4. Local imports using @ alias (e.g., `import { getStats } from '@/lib/api'`)

**Example from `/Users/dansidanutz/Desktop/MyWork/frontend/app/page.tsx`:**

```

typescript

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Video, Newspaper, FolderGit2, Bot, RefreshCw, Clock } from 'lucide-react';
import { getStats, Stats } from '@/lib/api';

```

text

**Order (Backend - Python):**

1. Standard library imports
2. Third-party imports (FastAPI, SQLAlchemy, httpx, etc.)
3. Local imports (database, models, scrapers, services)

**Path Aliases:**

- Frontend: `@/*` maps to root directory (e.g., `@/components`, `@/lib`)
- Used extensively: `import { Sidebar } from '@/components/Sidebar'`

## Error Handling

**Frontend (React):**

- Try-catch blocks around async operations in event handlers and useEffect
- Error state stored in component state (e.g., `const [error, setError] =

  useState<string | null>(null)`)

- User-friendly error messages displayed as alerts (e.g., `'Failed to load

  videos'`)

- Detailed errors logged to console for debugging: `console.error(err)`

**Pattern from
`/Users/dansidanutz/Desktop/MyWork/frontend/app/videos/page.tsx`:**

```

typescript

const fetchVideos = async () => {
  try {

```

javascript

setLoading(true);
const data = await getVideos(50);
setVideos(data);
setError(null);

```

text

  } catch (err) {

```

text

setError('Failed to load videos');
console.error(err);

```

text

  } finally {

```

text

setLoading(false);

```

text

  }
};

```

text

**Backend (FastAPI/Python):**

- HTTPException used for API errors with appropriate status codes
- Exceptions logged with logger.error()
- Database errors handled with try-except and rollback on failure
- ScraperLog records failures in database with error_message field

**Pattern from `/Users/dansidanutz/Desktop/MyWork/backend/main.py`:**

```

python
@app.post("/api/videos/scrape")
async def trigger_video_scrape(db: Session = Depends(get_db)):

```

yaml

try:

```

text

scraper = YouTubeScraper()
await scraper.scrape_videos(db)
return {"status": "success", "message": "YouTube scrape completed"}

```

text

except Exception as e:

```

text

raise HTTPException(status_code=500, detail=str(e))

```

text

```

text

```

text

## Logging

**Framework:** Python uses built-in `logging` module; Frontend uses
`console.log/error/warn`

**Setup (Backend):**

- Configured in `main.py` with basicConfig:

```

python
logging.basicConfig(

```

text

level=logging.INFO,
format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

```

text

)
logger = logging.getLogger(**name**)

```

text

**Patterns:**

- Service startup/shutdown logged at INFO level
- Scraper activity logged at INFO level (e.g., `logger.info(f"YouTube scraper

  completed: {saved_count} videos saved")`)

- Errors logged at ERROR level with context
- Warnings logged when optional APIs not available (e.g., APIFY_API_KEY not set)

**Frontend:**

- Errors logged to console for development: `console.error(err)`
- No structured logging library used
- Simple fallback for debugging failed async operations

## Comments

**When to Comment:**

- Docstrings on classes and functions explaining purpose and parameters
- Inline comments for complex logic or non-obvious calculations (e.g., scoring

  algorithms)

- Section comments in large files (e.g., `# ============ API Endpoints

  ============`)

**JSDoc/TSDoc:**

- Backend Python uses standard docstrings on functions and classes
- Frontend has minimal commenting, relying on clear naming

**Example from
`/Users/dansidanutz/Desktop/MyWork/backend/scrapers/youtube_scraper.py`:**

```

python
def scrape_videos(

```

yaml

self,
db: Session,
queries: List[str] = None,
max_results_per_query: int = 20,
published_after_days: int = 7

```

text

) -> List[Dict]:

```

python

"""
Scrape AI-related videos from YouTube

Args:

```

text

db: Database session
queries: List of search queries (defaults to AI_SEARCH_QUERIES)
max_results_per_query: Max videos per query
published_after_days: Only get videos from last N days

```

text

Returns:

```

text

List of scraped video data

```

text

"""

```

text

```

text

## Function Design

**Size:** Functions are kept relatively focused:

- React event handlers: 5-20 lines
- API call wrappers: 2-10 lines
- Service methods: 10-50 lines
- Complex scrapers: 50-100+ lines (understandable given complexity)

**Parameters:**

- Frontend: Props destructured in function parameters
- Backend: Use FastAPI's `Depends()` for database injection, query parameters

  from `Query()`

- Optional parameters given sensible defaults (e.g., `limit = 20`)

**Return Values:**

- Async functions return promises/awaited types
- API functions return properly typed objects (Pydantic models for backend, typed

  interfaces for frontend)

- Query functions return lists or single objects as appropriate

**Example from `/Users/dansidanutz/Desktop/MyWork/frontend/lib/api.ts`:**

```

typescript

export async function getVideos(limit = 20): Promise<Video[]> {
  const { data } = await api.get(`/api/videos?limit=${limit}`);
  return data;
}

```

text

## Module Design

**Exports:**

- API module exports axios instance and typed functions: `export const api =

  axios.create(...)`

- Components export as default: `export default function Dashboard() { ... }`
- Utilities export named functions: `export async function getVideos(limit = 20):

  Promise<Video[]>`

**Barrel Files:**

- Database module uses index file for re-exports (`database/__init__.py` imports

  models)

- Frontend has minimal barrel exports, mostly direct imports

**Separation of Concerns:**

- API layer: `lib/api.ts` - all HTTP requests and type definitions
- Components: `components/Sidebar.tsx` - UI only
- Pages: `app/page.tsx`, `app/videos/page.tsx` - page logic + component

  composition

- Backend services: `services/*.py` - business logic (YouTube automation, prompt

  optimization)

- Backend scrapers: `scrapers/*.py` - data collection logic
- Database: `database/*.py` - models and connection

## State Management

**Frontend:**

- Local component state using `useState`
- No global state management library (Redux, Zustand, etc.)
- Props passed down for simple data flow

**Backend:**

- Database as source of truth (SQLAlchemy ORM)
- Scheduler maintains in-memory job status (APScheduler)
- Service classes maintain session/client objects

## Type Safety

**Frontend:**

- TypeScript strict mode enabled
- All Pydantic models from backend have corresponding TypeScript interfaces in

  `lib/api.ts`

- React components typed with function parameters and return types

**Backend:**

- Pydantic models for request/response validation
- SQLAlchemy ORM models for database entities
- Type hints on function parameters and returns
- Optional fields use `Optional[T]` from typing module

---

*Convention analysis: 2026-01-24*

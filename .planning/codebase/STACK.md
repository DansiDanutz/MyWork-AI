# Technology Stack

**Analysis Date:** 2026-01-24

## Languages

**Primary:**

- TypeScript 5.3.3 - Frontend (Next.js app, React components, API client)
- Python 3.13 - Backend (FastAPI, scrapers, services)

**Secondary:**

- JavaScript - Build and configuration files

## Runtime

**Environment:**

- Node.js 22.18.0 - Frontend development and build
- Python 3.13.7 - Backend server and scheduled tasks

**Package Manager:**

- npm - Frontend dependencies
- pip - Backend dependencies (requirements.txt)
- Lockfile: npm has node_modules; Python uses requirements.txt

## Frameworks

**Core:**

- Next.js 14.1.0 - React meta-framework for SSR/static generation
- React 18.2.0 - UI component library
- React DOM 18.2.0 - React rendering for web

**Backend:**

- FastAPI 0.109.0+ - Async web framework and REST API
- Uvicorn 0.27.0+ - ASGI application server

**Styling:**

- Tailwind CSS 3.4.1 - Utility-first CSS framework (frontend)
- PostCSS 8.4.33 - CSS transformation tool
- Autoprefixer 10.4.17 - Vendor prefixing for CSS

**Data Visualization:**

- Recharts 2.10.4 - React charting library (for dashboards/analytics)

**Testing:**

- Not detected

**Build/Dev:**

- TypeScript 5.3.3 - Type checking and compilation
- ESLint 8.56.0 - JavaScript/TypeScript linting
- ESLint Next.js config 14.1.0 - Next.js specific linting rules

## Key Dependencies

**Frontend (React/Next.js Layer):**

- axios 1.6.5 - HTTP client for API calls to backend (`/Users/dansidanutz/Desktop/MyWork/frontend/lib/api.ts`)
- date-fns 3.3.1 - Date manipulation and formatting
- lucide-react 0.312.0 - Icon library for UI
- clsx 2.1.0 - Conditional className utility
- tailwind-merge 2.2.1 - Merge Tailwind CSS classes without conflicts

**Backend (FastAPI Layer):**

- httpx 0.25.1+ - Async HTTP client for making requests to external APIs
- feedparser 6.0.10 - RSS feed parsing for news aggregation
- python-dateutil 2.8.2 - Date/time parsing and manipulation
- SQLAlchemy 2.0.25 - ORM for database abstraction (`/Users/dansidanutz/Desktop/MyWork/backend/database/`)
- aiosqlite 0.19.0 - Async SQLite driver for database queries

**AI/LLM Integration:**

- anthropic 0.18.1 - Claude API client for content generation (`/Users/dansidanutz/Desktop/MyWork/backend/services/prompt_optimizer.py`)
- dspy-ai 2.4.0 - Framework for optimizing LLM pipelines (uses DSPy signatures for prompt engineering)

**Scraping & Data Collection:**

- apify-client 1.6.0 - Apify web scraping platform client (`/Users/dansidanutz/Desktop/MyWork/backend/scrapers/youtube_scraper.py`)
- google-api-python-client 2.118.0 - Google APIs (YouTube Data API)
- google-auth-oauthlib 1.2.0 - OAuth authentication for Google services

**Scheduling:**

- apscheduler 3.10.4 - Job scheduling library for running scrapers on schedule

**Environment:**

- python-dotenv 1.0.0 - Load environment variables from .env files

## Configuration

**Environment:**
Configuration via environment variables in `.env` files:

- `/Users/dansidanutz/Desktop/MyWork/backend/.env` - Backend API keys (Apify, Anthropic, YouTube, HeyGen, GitHub)
- Frontend uses `NEXT_PUBLIC_API_URL` for backend connection (defaults to `http://localhost:8000`)

**Key configs required:**

- APIFY_API_KEY - YouTube and web scraping
- ANTHROPIC_API_KEY - Claude LLM for content generation
- YOUTUBE_API_KEY - YouTube Data API for video uploads
- HEYGEN_API_KEY - AI video generation
- GITHUB_TOKEN - GitHub API (optional, for higher rate limits)

**Build:**

- `next.config.js` - Next.js configuration (allows images from ytimg.com, youtube.com, avatars.githubusercontent.com)
- `tsconfig.json` - TypeScript compiler settings with path aliases (`@/*` → root directory)
- `.env.example` - Template for required environment variables

## Database

**Type:** SQLite

- Location: `/Users/dansidanutz/Desktop/MyWork/backend/dashboard.db`
- Sync Connection: `sqlite:///{DB_PATH}` (SQLAlchemy)
- Async Connection: `sqlite+aiosqlite:///{DB_PATH}` (for FastAPI)
- Tables: YouTubeVideo, AINews, GitHubProject, YouTubeAutomation, ScraperLog

## Platform Requirements

**Development:**

- Node.js 18+ (frontend development)
- Python 3.10+ (backend server)
- pip (Python package manager)
- npm (Node.js package manager)
- Git (version control)

**Production:**

- Node.js 22+ for running Next.js server
- Python 3.13+ for FastAPI backend
- SQLite 3+ (embedded database)
- Port 3000 - Frontend server (Next.js)
- Port 8000 - Backend API (Uvicorn)

**External Services (cloud/SaaS):**

- Apify (YouTube/web scraping)
- Anthropic (Claude API)
- Google Cloud (YouTube Data API, OAuth)
- HeyGen (AI video generation)
- GitHub (trending projects, optional token)

---

*Stack analysis: 2026-01-24*

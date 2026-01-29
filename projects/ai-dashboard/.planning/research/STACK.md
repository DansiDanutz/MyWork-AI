# AI Dashboard - Technology Stack

**Last Updated**: 2026-01-29
**Project Status**: MVP Complete, Phase 7 (Production-Ready)

---

## Backend Stack

### Core Framework
- **FastAPI** (0.104.1)
  - Modern, fast web framework for building APIs with Python 3.9+
  - Automatic OpenAPI documentation
  - Built-in validation with Pydantic
  - Async support for high performance

**Why FastAPI?**
- Modern Python async/await support
- Automatic API documentation (/docs)
- Type hints and Pydantic validation
- Fast performance (comparable to NodeJS and Go)
- Easy WebSocket support
- Great for building RESTful APIs

### Python Version
- **Python 3.9+**
  - Type hints support
  - Async/await syntax
  - Modern standard library features

### Database
- **SQLite** (3.x)
  - Lightweight, serverless database
  - Perfect for single-user applications
  - Zero configuration
  - Included in Python standard library

**Why SQLite?**
- This is a personal tool, not multi-user SaaS
- No need for PostgreSQL or MySQL
- Simple backup and migration
- Fast enough for single-user workload
- Easy to reset during development

### ORM
- **SQLAlchemy** (2.0.x)
  - Python SQL toolkit and ORM
  - Async support
  - Declarative model definitions
  - Migration support via Alembic

**Why SQLAlchemy?**
- Industry standard for Python ORMs
- Async support for FastAPI
- Powerful query building
- Easy to work with existing databases

### Scraping & Data Collection
- **BeautifulSoup4** (4.12.x)
  - Web scraping library
  - HTML/XML parsing
  - Gentle on malformed HTML

- **Requests** (2.31.x)
  - HTTP library for humans
  - Simple API for making HTTP requests
  - Session management
  - Multipart file uploads

- **Feedparser** (6.0.x)
  - RSS and Atom feed parsing
  - Handles various feed formats
  - Enclosure support for podcasts

- **yt-dlp** (2023.x)
  - YouTube video download
  - Metadata extraction
  - Format selection
  - Thumbnail download

### Automation & Scheduling
- **APScheduler** (3.10.x)
  - Advanced Python scheduler
  - Cron-like scheduling
  - Job persistence
  - Async support

**Why APScheduler?**
- Built-in job persistence
- Cron-like syntax for scheduling
- Async job execution
- Easy to manage multiple jobs
- Works great with FastAPI

### OAuth & Authentication
- **Python-OAuth2** (4.x)
  - OAuth 2.0 library for YouTube
  - Token management
  - Refresh token support
  - Easy integration with YouTube API

- **Google API Python Client** (2.x)
  - YouTube Data API v3
  - Video upload
  - Metadata management
  - Playlist management

### Utilities
- **Pydantic** (2.0.x)
  - Data validation using Python type annotations
  - Settings management
  - JSON serialization

- **python-dotenv** (1.0.x)
  - Read environment variables from .env files
  - Configuration management

- **aiofiles** (23.x)
  - Async file operations
  - Non-blocking file I/O

---

## Frontend Stack

### Core Framework
- **Next.js 14** (App Router)
  - React framework with built-in routing
  - Server-side rendering (SSR)
  - Static site generation (SSG)
  - API routes
  - File-based routing

**Why Next.js 14?**
- Latest App Router architecture
- Server components for better performance
- Built-in API routes for backend proxy
- Great TypeScript support
- Excellent developer experience

### React
- **React 18** (Client Components)
  - UI library
  - Hooks for state management
  - Context for global state
  - Client-side rendering

### TypeScript
- **TypeScript 5.x**
  - Static type checking
  - Better IDE support
  - Catch errors at compile time
  - Self-documenting code

**Why TypeScript?**
- Type safety reduces bugs
- Better autocomplete in IDEs
- Easier refactoring
- Self-documenting code
- Industry standard for modern React

### Styling
- **Tailwind CSS 3.x**
  - Utility-first CSS framework
  - Responsive design
  - Dark mode support
  - JIT compiler for production

**Why Tailwind?**
- Rapid UI development
- Consistent design system
- Responsive utilities
- No custom CSS needed
- Small production bundle

### State Management
- **React Context API**
  - Global state for user settings
  - Theme management
  - Simple and built-in

- **React Hooks**
  - useState for local state
  - useEffect for side effects
  - useContext for global state
  - Custom hooks for reusable logic

### Data Fetching
- **Native fetch API**
  - Browser built-in
  - No additional dependencies
  - Async/await support
  - AbortController for cancellation

**Why not React Query or SWR?**
- This is a simple personal tool
- Native fetch is sufficient
- No need for complex caching
- Keep dependencies minimal

### Icons
- **Lucide React** (0.x)
  - Lightweight icon library
  - Tree-shakeable
  - Consistent design
  - 1000+ icons

---

## Deployment Stack

### Backend Deployment
- **Railway**
  - Cloud platform for hosting APIs
  - Automatic deploys from Git
  - Built-in PostgreSQL (not used here)
  - Environment variable management
  - Logs and metrics

**Why Railway?**
- Simple deployment workflow
- Generous free tier
- Easy environment variable management
- Good for personal projects
- Auto-restart on crashes

### Frontend Deployment
- **Vercel**
  - Next.js creators' platform
  - Zero-config deployment
  - Automatic SSL
  - Edge network
  - Preview deployments

**Why Vercel?**
- Built by Next.js creators
- Zero-config deployment
- Best platform for Next.js
- Free tier sufficient
- Automatic HTTPS

### Domain & DNS
- Custom domain via Vercel
- Automatic SSL certificate
- DNS managed via Vercel

---

## Development Tools

### Backend Development
- **pytest** (7.x)
  - Testing framework
  - Async test support
  - Fixtures for setup/teardown
  - Coverage reporting

- **pytest-asyncio** (0.21.x)
  - Async test support
  - Fixture support
  - Easy test writing

- **black** (23.x)
  - Python code formatter
  - Consistent style
  - Auto-formatting

- **ruff** (0.1.x)
  - Fast Python linter
  - Replaces flake8, pylint, isort
  - Very fast

### Frontend Development
- **ESLint** (8.x)
  - JavaScript/TypeScript linter
  - Next.js config
  - Catch bugs early

- **Prettier** (3.x)
  - Code formatter
  - Consistent style
  - Auto-format on save

- **TypeScript Compiler** (tsc)
  - Type checking
  - Catch errors at compile time

### Version Control
- **Git**
  - Version control
  - Branching strategy
  - Commit hooks

### Package Managers
- **pip** (Python)
  - Package installation
  - Virtual environment management

- **npm** (Node.js)
  - Frontend package management
  - Script running

---

## API & Integrations

### External APIs Used

**GitHub Trending API**:
- Scrapes trending repositories
- Public API (no auth needed)
- Rate limited but sufficient

**YouTube Data API v3**:
- Video upload
- Metadata retrieval
- Playlist management
- Requires OAuth 2.0

**News Feeds**:
- RSS/Atom feeds
- Various news sources
- No authentication needed

---

## Monitoring & Logging

### Backend
- **Python logging**
  - Structured logging
  - Log levels (DEBUG, INFO, WARNING, ERROR)
  - File and console output

- **Railway logs**
  - Real-time logs
  - Log aggregation
  - Error tracking

### Frontend
- **Browser console**
  - Development debugging
  - Error tracking
  - Performance monitoring

- **Vercel Analytics**
  - Page views
  - Web vitals
  - Performance metrics

---

## Security

### Authentication
- **YouTube OAuth 2.0**
  - Token-based authentication
  - Refresh token support
  - Secure token storage

### API Security
- **CORS**
  - Configured for frontend domain
  - Prevents unauthorized access

- **Environment Variables**
  - Sensitive data in .env files
  - Never committed to Git
  - Separate .env.example for documentation

### Data Privacy
- **No user tracking**
  - Personal tool only
  - No analytics
  - No third-party scripts

---

## Performance

### Backend
- **Async operations**
  - Non-blocking I/O
  - Concurrent request handling
  - Efficient resource usage

- **Database optimization**
  - Indexed queries
  - Efficient schema design
  - Connection pooling

### Frontend
- **Next.js optimizations**
  - Automatic code splitting
  - Lazy loading
  - Image optimization
  - Font optimization

- **Tailwind CSS**
  - JIT compiler
  - Purge unused CSS
  - Small bundle size

---

## Testing Strategy

### Backend Tests
- **Unit tests**
  - Test individual functions
  - Mock external dependencies
  - Fast execution

- **Integration tests**
  - Test API endpoints
  - Test database operations
  - Test scrapers

### Frontend Tests
- **Manual testing**
  - Browser testing
  - Feature verification
  - Responsive design testing

---

## Alternatives Considered

### Backend Framework
**Considered**: Flask, Django
**Chose**: FastAPI
**Why**: Modern, async support, automatic docs, type hints

### Database
**Considered**: PostgreSQL, MongoDB
**Chose**: SQLite
**Why**: Personal tool, no multi-user needed, simple, fast enough

### Frontend Framework
**Considered**: Vue, Svelte, Vanilla React
**Chose**: Next.js 14
**Why**: App Router, server components, best DX, built-in API routes

### State Management
**Considered**: Redux, Zustand, Jotai
**Chose**: React Context
**Why**: Simple, built-in, sufficient for this app

### Styling
**Considered**: CSS Modules, Styled Components, Emotion
**Chose**: Tailwind CSS
**Why**: Rapid development, consistent design, responsive utilities

---

## Version History

### Current Stack (Phase 7)
- FastAPI 0.104.1
- Next.js 14 (App Router)
- Python 3.9+
- SQLite 3.x
- TypeScript 5.x

### Previous Versions
- Phase 1-3: Next.js 13 (Pages Router)
- Phase 4-6: Migrated to Next.js 14 (App Router)

---

## Dependencies Summary

### Backend Production Dependencies
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
aiofiles==23.2.1
apscheduler==3.10.4
python-oauth2==4.1.0
google-api-python-client==2.108.0
beautifulsoup4==4.12.2
requests==2.31.0
feedparser==6.0.10
yt-dlp==2023.10.13
python-dotenv==1.0.0
```

### Backend Development Dependencies
```
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
black==23.12.0
ruff==0.1.8
```

### Frontend Dependencies
```json
{
  "next": "14.0.4",
  "react": "18.2.0",
  "react-dom": "18.2.0",
  "typescript": "5.3.3",
  "tailwindcss": "3.3.6",
  "lucide-react": "0.294.0"
}
```

---

## Conclusion

This stack was chosen for:
- **Simplicity**: Personal tool, not enterprise SaaS
- **Modern**: Latest stable versions
- **Performance**: Fast and responsive
- **Maintainability**: Type-safe, well-documented
- **Deployment**: Easy to deploy and manage

**Key Principle**: Use the right tool for the job, not the most popular or complex one.

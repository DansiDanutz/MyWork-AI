# AI Dashboard - System Architecture

**Last Updated**: 2026-01-29
**Project Status**: MVP Complete, Phase 7 (Production-Ready)

---

## Architecture Overview

The AI Dashboard follows a **classic three-tier architecture** with a scheduled scraping pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 14)                    │
│                   https://vercel.app/                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                  https://railway.app/                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Endpoints                            │  │
│  │  • GET /api/news        • GET /api/videos           │  │
│  │  • GET /api/projects    • GET /api/github-trending   │  │
│  │  • POST /api/youtube/upload                        │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Scheduled Jobs (APScheduler)                │  │
│  │  • News scraper (every 30 min)                      │  │
│  │  • Video scraper (every hour)                       │  │
│  │  • GitHub scraper (every hour)                      │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ SQLAlchemy
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database (SQLite)                        │
│                   ai_dashboard.db                          │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              External APIs (Scraping Targets)               │
│  • News Websites (RSS feeds)                               │
│  • YouTube (yt-dlp + YouTube API)                          │
│  • GitHub Trending (scraping)                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Backend Components

#### FastAPI Application (`backend/main.py`)

**Responsibilities**:
- API endpoint definitions
- CORS middleware
- Scheduler initialization
- OAuth flow handling
- Database session management

**Key Classes/Functions**:
```python
app = FastAPI(title="AI Dashboard API")

# API Routes
@app.get("/api/news")
@app.get("/api/videos")
@app.get("/api/projects")
@app.post("/api/youtube/upload")

# Scheduler Jobs
scheduler.add_job(scrape_news, 'interval', minutes=30)
scheduler.add_job(scrape_videos, 'interval', hours=1)
```

#### Scrapers (`backend/scrapers/`)

**News Aggregator** (`news_aggregator.py`):
- Fetches RSS/Atom feeds
- Parses feed data
- Stores news items in database
- Multiple news sources

**YouTube Scraper** (`youtube_scraper.py`):
- Fetches channel videos via yt-dlp
- Extracts metadata
- Downloads thumbnails
- Stores video items in database

**GitHub Trending** (`github_trending.py`):
- Scrapes GitHub trending page
- Extracts repository data
- Stores trending repos in database

#### Automation Service (`backend/services/youtube_automation.py`)

**YouTube Upload Automation**:
- OAuth 2.0 flow
- Token management
- Video upload with progress
- Metadata assignment
- Playlist management

**Key Workflows**:
1. User initiates OAuth → YouTube consent → Token stored
2. User selects video → Automation job created
3. Job uploads video → Progress tracked → Completion
4. Metadata assigned → Playlist updated → Done

#### Database Layer (`backend/database/`)

**Connection** (`db.py`):
- SQLAlchemy engine
- Session factory
- Context manager for sessions

**Models** (`models.py`):
```python
class NewsItem(Base):
    title, url, summary, source, published_at, scraped_at

class VideoItem(Base):
    title, video_id, thumbnail_url, channel, duration, scraped_at

class GitHubRepo(Base):
    name, url, stars, language, description, scraped_at

class YouTubeUpload(Base):
    title, video_path, status, progress, created_at, uploaded_at
```

---

### Frontend Components

#### App Structure (`frontend/app/`)

**Pages** (Server Components):
- `page.tsx` - Dashboard (main page)
- `news/page.tsx` - News listing
- `videos/page.tsx` - Videos listing
- `projects/page.tsx` - Projects listing
- `youtube-bot/page.tsx` - YouTube automation
- `settings/page.tsx` - Settings

**Components** (Client Components):
- `DashboardClient.tsx` - Dashboard data fetching
- `NewsClient.tsx` - News data fetching and display
- `VideosClient.tsx` - Videos data fetching and display
- `ProjectsClient.tsx` - Projects data fetching and display
- `YouTubeBotClient.tsx` - YouTube automation interface

**Shared Components** (`frontend/components/`):
- `AppShell.tsx` - Main app layout with navigation
- `Sidebar.tsx` - Navigation sidebar

#### API Integration (`frontend/lib/api.ts`)

**API Functions**:
```typescript
async function fetchNews(): Promise<NewsItem[]>
async function fetchVideos(): Promise<VideoItem[]>
async function fetchGitHubTrending(): Promise<GitHubRepo[]>
async function uploadYouTubeVideo(data: UploadData): Promise<UploadResponse>
```

**Error Handling**:
- Try/catch blocks
- User-friendly error messages
- Loading states
- Retry logic for failed requests

---

## Data Flow

### Scraping Pipeline

```
1. Scheduler Triggers (APScheduler)
   │
   ▼
2. Scraper Executed
   │
   ├─→ News Aggregator: Fetch RSS feeds → Parse → Store in DB
   ├─→ Video Scraper: Fetch channel → Extract metadata → Store in DB
   └─→ GitHub Scraper: Scrape trending → Parse → Store in DB
   │
   ▼
3. Database Updated (SQLite)
   │
   ▼
4. Frontend Fetches Data (Next.js API route or direct)
   │
   ▼
5. Data Displayed in UI (React components)
```

### YouTube Upload Pipeline

```
1. User Initiates OAuth (Frontend)
   │
   ▼
2. OAuth Flow (Backend + YouTube API)
   ├─→ Redirect to YouTube consent
   ├─→ User grants permissions
   └─→ Token stored in database
   │
   ▼
3. User Selects Video (Frontend)
   │
   ▼
4. Upload Job Created (Backend)
   │
   ▼
5. Video Upload (YouTube API)
   ├─→ Initialize upload
   ├─→ Upload chunks
   ├─→ Update progress
   └─→ Complete upload
   │
   ▼
6. Metadata Assigned (YouTube API)
   │
   ▼
7. Playlist Updated (YouTube API)
   │
   ▼
8. Upload Complete (Frontend notified)
```

### API Request Flow

```
1. User Action (Frontend)
   │
   ▼
2. Component Fetches Data (useEffect or event handler)
   │
   ▼
3. API Call (fetch() or api.ts function)
   │
   ├─→ To Backend API: https://backend.railway.app/api/...
   └─→ To Next.js API Route: /api/... (proxy to backend)
   │
   ▼
4. Backend Processes Request
   ├─→ Validate request
   ├─→ Query database
   └─→ Return JSON response
   │
   ▼
5. Frontend Renders Data
   ├─→ Update state
   └─→ Re-render component
```

---

## Database Schema

### Tables

**news_items**:
```sql
CREATE TABLE news_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    summary TEXT,
    source TEXT NOT NULL,
    published_at TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_news_published ON news_items(published_at DESC);
CREATE INDEX idx_news_source ON news_items(source);
```

**video_items**:
```sql
CREATE TABLE video_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    video_id TEXT UNIQUE NOT NULL,
    thumbnail_url TEXT,
    channel TEXT NOT NULL,
    duration INTEGER,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_video_scraped ON video_items(scraped_at DESC);
```

**github_repos**:
```sql
CREATE TABLE github_repos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    stars INTEGER,
    language TEXT,
    description TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_github_stars ON github_repos(stars DESC);
```

**youtube_uploads**:
```sql
CREATE TABLE youtube_uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    video_path TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    youtube_video_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_at TIMESTAMP
);
CREATE INDEX idx_uploads_status ON youtube_uploads(status);
```

---

## Security Architecture

### Authentication

**YouTube OAuth 2.0**:
```
1. Frontend: User clicks "Connect YouTube"
2. Backend: Generates OAuth URL
3. Frontend: Redirects to YouTube
4. User: Grants permissions
5. YouTube: Redirects back with auth code
6. Backend: Exchanges code for token
7. Backend: Stores token in database
8. Frontend: Shows "Connected" status
```

**Token Storage**:
- Access tokens stored in database
- Refresh tokens for automatic renewal
- Tokens encrypted at rest (future enhancement)

### API Security

**CORS Configuration**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Environment Variables**:
- YouTube OAuth secrets in `.env`
- Database path in `.env`
- Never committed to Git

---

## Deployment Architecture

### Backend Deployment (Railway)

```
┌─────────────────────────────────────┐
│         Railway Container            │
│  ┌───────────────────────────────┐  │
│  │   FastAPI Application        │  │
│  │   • Uvicorn server           │  │
│  │   • SQLite database          │  │
│  │   • APScheduler              │  │
│  │   • Scrapers                 │  │
│  └───────────────────────────────┘  │
│                                     │
│  • Environment Variables            │
│  • Automatic Git Deploys            │
│  • Health Checks                    │
│  • Logging & Metrics               │
└─────────────────────────────────────┘
```

**Deployment Workflow**:
1. Push to Git (`main` branch)
2. Railway detects new commit
3. Builds container (installs dependencies)
4. Runs health checks
5. Deploys to production
6. Zero-downtime rollout

### Frontend Deployment (Vercel)

```
┌─────────────────────────────────────┐
│         Vercel Edge Network         │
│  ┌───────────────────────────────┐  │
│  │   Next.js Application         │  │
│  │   • Server Components         │  │
│  │   • Client Components         │  │
│  │   • Static Assets             │  │
│  │   • API Routes (proxy)        │  │
│  └───────────────────────────────┘  │
│                                     │
│  • Automatic HTTPS                  │
│  • CDN Caching                      │
│  • Edge Functions                   │
│  • Analytics                        │
└─────────────────────────────────────┘
```

**Deployment Workflow**:
1. Push to Git (`main` branch)
2. Vercel detects new commit
3. Builds application (npm run build)
4. Runs tests (if configured)
5. Deploys to preview
6. Promotes to production

---

## Performance Optimization

### Backend Optimizations

**Async Operations**:
- All scrapers run asynchronously
- Non-blocking I/O for HTTP requests
- Concurrent scraping of multiple sources

**Database Optimization**:
- Indexed queries on frequently queried columns
- Efficient schema design
- Connection pooling (future: when moving to PostgreSQL)

**Caching Strategy** (future):
- Cache scraped data for 5 minutes
- Reduce external API calls
- Improve response times

### Frontend Optimizations

**Next.js Optimizations**:
- Automatic code splitting
- Lazy loading of components
- Image optimization (next/image)
- Font optimization (next/font)
- Bundle size optimization

**Tailwind CSS**:
- JIT compiler (production)
- Purges unused CSS
- Small final bundle size

**API Calls**:
- Fetch data on server (server components)
- Reduce client-side JavaScript
- Progressive enhancement

---

## Scalability Considerations

### Current Capacity (Personal Tool)

**Backend**:
- Handles 1-10 concurrent users (single user realistically)
- 1000s of news items, videos, repos
- 10s of YouTube uploads per day

**Database**:
- SQLite suitable for < 100K rows per table
- No concurrent write issues (single user)
- Simple backup (copy file)

### Future Scalability (If Needed)

**Backend**:
- Add Redis for caching
- Add Celery for background jobs
- Move to PostgreSQL for multi-user
- Add read replicas for scaling

**Frontend**:
- Add CDN for static assets
- Add Redis for session caching
- Add database read replicas
- Implement rate limiting

---

## Monitoring & Observability

### Backend Monitoring

**Railway Metrics**:
- CPU usage
- Memory usage
- Request count
- Error rate
- Response time

**Application Logging**:
```python
logging.basicConfig(level=logging.INFO)
logger.info("Scraping completed: {count} items")
logger.error("Scraping failed: {error}")
```

### Frontend Monitoring

**Vercel Analytics**:
- Page views
- Web vitals (LCP, FID, CLS)
- Performance scores
- Device breakdown

**Browser Console**:
- Development debugging
- Error tracking
- Performance monitoring

---

## Error Handling

### Backend Error Handling

**Scraping Errors**:
```python
try:
    items = scraper.scrape()
except Exception as e:
    logger.error(f"Scraping failed: {e}")
    # Continue with other scrapers
```

**API Errors**:
```python
@app.get("/api/news")
async def get_news():
    try:
        news = db.query(NewsItem).all()
        return news
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
```

**YouTube Upload Errors**:
```python
try:
    video_id = upload_video(token, video_data)
except HttpError as e:
    logger.error(f"YouTube API error: {e}")
    # Update upload status to failed
    update_upload_status(upload_id, "failed")
```

### Frontend Error Handling

**API Call Errors**:
```typescript
try {
  const news = await fetchNews();
  setNews(news);
} catch (error) {
  console.error("Failed to fetch news:", error);
  setError("Failed to load news. Please try again.");
}
```

**User-Friendly Messages**:
- "Failed to load news"
- "Upload failed. Please try again."
- "Connection lost. Please refresh."

---

## Technology Choices Rationale

### Why FastAPI?
- Modern async Python framework
- Automatic API documentation
- Type hints and validation
- Fast performance
- Easy WebSocket support

### Why SQLite?
- Personal tool (no multi-user needed)
- Zero configuration
- Fast enough for single user
- Easy backup and migration
- No server overhead

### Why Next.js 14?
- App Router (latest architecture)
- Server components (better performance)
- Built-in API routes (backend proxy)
- Great TypeScript support
- Excellent DX

### Why Tailwind CSS?
- Rapid UI development
- Consistent design system
- Responsive utilities
- No custom CSS needed
- Small production bundle

---

## Architecture Patterns Used

### 1. **Three-Tier Architecture**
- Presentation layer (Next.js frontend)
- Application layer (FastAPI backend)
- Data layer (SQLite database)

### 2. **Separation of Concerns**
- Frontend handles UI and user interaction
- Backend handles business logic and data
- Database handles persistence

### 3. **Async/Await Pattern**
- Backend uses async for I/O operations
- Frontend uses async for API calls
- Non-blocking, concurrent execution

### 4. **Repository Pattern** (implicit)
- Scrapers abstract data sources
- API endpoints abstract database operations
- Frontend components abstract UI logic

### 5. **Scheduled Job Pattern**
- APScheduler manages periodic tasks
- Scrapers run on intervals
- Automation jobs queued and executed

---

## Future Architecture Enhancements

### Phase 8+ Enhancements

**Potential Improvements**:
1. **Add Redis** for caching scraped data
2. **Add Celery** for background job processing
3. **Add PostgreSQL** for better scalability
4. **Add WebSocket** support for real-time updates
5. **Add GraphQL** for flexible API queries

**When to Implement**:
- When performance becomes an issue
- When adding multi-user support
- When building more complex features
- When user base grows significantly

---

## Conclusion

The AI Dashboard architecture is designed for:
- **Simplicity**: Personal tool, not enterprise SaaS
- **Performance**: Fast and responsive
- **Maintainability**: Clean separation of concerns
- **Scalability**: Can scale if needed (with refactoring)

**Key Architecture Decisions**:
1. **Three-tier architecture** for separation of concerns
2. **Scheduled scraping** for fresh data
3. **OAuth for YouTube** for secure uploads
4. **SQLite for simplicity** (can upgrade later)
5. **Next.js App Router** for modern frontend

This architecture supports the current needs (personal tool) while allowing for future growth if needed.

# AI Dashboard - Code Structure

**Last Updated**: 2026-01-29
**Project Status**: MVP Complete, Phase 7 (Production-Ready)

---

## Project Structure Overview

```
ai-dashboard/
├── backend/                    # FastAPI backend application
│   ├── main.py                 # FastAPI app, routes, scheduler
│   ├── database/               # Database layer
│   ├── scrapers/               # Data collection scripts
│   ├── services/               # Business logic services
│   ├── tests/                  # Backend tests
│   ├── .env                    # Environment variables (NEVER COMMIT)
│   ├── .env.example            # Environment template
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # Next.js 14 frontend application
│   ├── app/                    # App Router pages
│   ├── components/             # Shared components
│   ├── lib/                    # Utility libraries
│   ├── public/                 # Static assets
│   ├── tests/                  # Frontend tests
│   ├── package.json            # NPM dependencies
│   ├── next.config.js          # Next.js configuration
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   └── tsconfig.json           # TypeScript configuration
│
├── start.sh                    # Start script (Mac/Linux)
├── start.bat                   # Start script (Windows)
└── README.md                   # Project documentation
```

---

## Backend Structure

### `/backend/main.py`

**Purpose**: FastAPI application entry point

**Key Sections**:
```python
# 1. FastAPI App Initialization
app = FastAPI(title="AI Dashboard API")

# 2. CORS Middleware
app.add_middleware(CORSMiddleware, ...)

# 3. Database Initialization
from database.db import engine, Base
Base.metadata.create_all(bind=engine)

# 4. Scheduler Initialization
scheduler = BackgroundScheduler()
scheduler.add_job(scrape_news, 'interval', minutes=30)
scheduler.add_job(scrape_videos, 'interval', hours=1)
scheduler.start()

# 5. API Routes
@app.get("/api/news")
@app.get("/api/videos")
@app.get("/api/projects")
@app.post("/api/youtube/upload")
```

**When to modify**:
- Adding new API endpoints
- Changing scheduler configuration
- Modifying CORS settings
- Adding middleware

---

### `/backend/database/`

**Purpose**: Database models and connection management

#### `db.py`
**Purpose**: Database connection and session management

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./ai_dashboard.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**When to modify**:
- Changing database URL
- Adding connection pooling
- Configuring session options

#### `models.py`
**Purpose**: SQLAlchemy ORM models

```python
class NewsItem(Base):
    __tablename__ = "news_items"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    summary = Column(Text)
    source = Column(String, nullable=False)
    published_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)

class VideoItem(Base):
    __tablename__ = "video_items"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    video_id = Column(String, unique=True, nullable=False)
    thumbnail_url = Column(String)
    channel = Column(String, nullable=False)
    duration = Column(Integer)

class GitHubRepo(Base):
    __tablename__ = "github_repos"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    stars = Column(Integer)
    language = Column(String)
    description = Column(String)
```

**When to modify**:
- Adding new tables
- Adding new columns
- Changing relationships
- Adding indexes

---

### `/backend/scrapers/`

**Purpose**: Data collection scripts

#### `news_aggregator.py`
**Purpose**: Aggregate news from RSS/Atom feeds

```python
class NewsAggregator:
    def __init__(self):
        self.sources = [
            "https://example.com/feed.xml",
            "https://news.example.com/rss",
        ]

    def scrape(self):
        """Scrape all news sources"""
        items = []
        for source in self.sources:
            feed = feedparser.parse(source)
            for entry in feed.entries:
                items.append({
                    'title': entry.title,
                    'url': entry.link,
                    'summary': entry.get('summary'),
                    'source': source,
                    'published_at': entry.get('published'),
                })
        return items
```

**When to modify**:
- Adding new news sources
- Changing parsing logic
- Adding filtering criteria
- Modifying data extraction

#### `youtube_scraper.py`
**Purpose**: Scrape YouTube channel videos

```python
class YouTubeScraper:
    def __init__(self, channel_url):
        self.channel_url = channel_url

    def scrape(self):
        """Scrape videos from channel"""
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(self.channel_url, download=False)
            items = []
            for video in info['entries']:
                items.append({
                    'title': video['title'],
                    'video_id': video['id'],
                    'thumbnail_url': video['thumbnail'],
                    'channel': video['channel'],
                    'duration': video['duration'],
                })
            return items
```

**When to modify**:
- Adding new channels
- Changing video metadata extraction
- Adding filtering by date/views
- Modifying thumbnail logic

#### `github_trending.py`
**Purpose**: Scrape GitHub trending repositories

```python
class GitHubTrendingScraper:
    def scrape(self):
        """Scrape GitHub trending page"""
        url = "https://github.com/trending"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        repos = []
        for article in soup.find_all('article'):
            repos.append({
                'name': article.find('h2').text.strip(),
                'url': "https://github.com" + article.find('a')['href'],
                'stars': int(article.find('span', class_='stars').text.replace(',', '')),
                'language': article.find('span', class_='lang').text,
                'description': article.find('p', class_='description').text,
            })
        return repos
```

**When to modify**:
- Changing trending page URL
- Adding filters (language, time range)
- Modifying data extraction
- Adding error handling

---

### `/backend/services/`

**Purpose**: Business logic services

#### `youtube_automation.py`
**Purpose**: YouTube upload automation service

```python
class YouTubeAutomationService:
    def __init__(self, access_token):
        self.access_token = access_token
        self.youtube = googleapiclient.discover('youtube', 'v3')
        self.credentials = Credentials(token=self.access_token)

    def upload_video(self, video_path, title, description):
        """Upload video to YouTube"""
        request = self.youtube.videos().insert(
            part='snippet,status',
            body={
                'snippet': {
                    'title': title,
                    'description': description,
                },
                'status': {
                    'privacyStatus': 'public'
                }
            },
            media_body=MediaFileUpload(video_path)
        )
        response = request.execute()
        return response['id']
```

**When to modify**:
- Adding metadata options
- Modifying upload logic
- Adding progress tracking
- Adding error handling

#### `scheduler_service.py`
**Purpose**: APScheduler management

```python
def setup_scheduler(app):
    """Setup and start scheduler"""
    scheduler = BackgroundScheduler()

    # Add jobs
    scheduler.add_job(
        scrape_all_news,
        'interval',
        minutes=30,
        id='news_scraper'
    )

    scheduler.add_job(
        scrape_all_videos,
        'interval',
        hours=1,
        id='video_scraper'
    )

    scheduler.start()
```

**When to modify**:
- Adding new scheduled jobs
- Changing job intervals
- Modifying job logic
- Adding job error handling

---

### `/backend/.env.example`

**Purpose**: Environment variable template

```bash
# Database
DATABASE_URL=sqlite:///./ai_dashboard.db

# YouTube OAuth
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here
YOUTUBE_REDIRECT_URI=http://localhost:8000/api/youtube/callback

# Scraping
NEWS_SOURCES=https://feed1.xml,https://feed2.xml
YOUTUBE_CHANNELS=https://www.youtube.com/@channel1,https://www.youtube.com/@channel2

# API Keys (if needed)
GITHUB_TOKEN=your_github_token_here
```

**When to modify**:
- Adding new environment variables
- Changing default values
- Documenting new integrations

---

## Frontend Structure

### `/frontend/app/`

**Purpose**: App Router pages and layouts

#### `page.tsx` (Dashboard)
**Purpose**: Main dashboard page

```typescript
export default function DashboardPage() {
  return (
    <DashboardClient />
  )
}
```

**When to modify**:
- Changing dashboard layout
- Adding dashboard widgets
- Modifying dashboard data

#### `news/page.tsx`
**Purpose**: News listing page

```typescript
export default function NewsPage() {
  return (
    <NewsClient />
  )
}
```

**When to modify**:
- Adding news filters
- Changing news display
- Adding pagination

#### `videos/page.tsx`
**Purpose**: Videos listing page

```typescript
export default function VideosPage() {
  return (
    <VideosClient />
  )
}
```

**When to modify**:
- Adding video filters
- Changing video display
- Adding video player

#### `youtube-bot/page.tsx`
**Purpose**: YouTube automation page

```typescript
export default function YouTubeBotPage() {
  return (
    <YouTubeBotClient />
  )
}
```

**When to modify**:
- Adding automation features
- Changing upload UI
- Adding progress tracking

#### `layout.tsx`
**Purpose**: Root layout component

```typescript
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AppShell>
          {children}
        </AppShell>
      </body>
    </html>
  )
}
```

**When to modify**:
- Changing global layout
- Adding global providers
- Modifying HTML structure

---

### `/frontend/components/`

**Purpose**: Shared React components

#### `AppShell.tsx`
**Purpose**: Main app layout with navigation

```typescript
export function AppShell({ children }) {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}
```

**When to modify**:
- Changing app layout
- Adding header/footer
- Modifying navigation

#### `Sidebar.tsx`
**Purpose**: Navigation sidebar

```typescript
export function Sidebar() {
  const navItems = [
    { href: '/', label: 'Dashboard', icon: Home },
    { href: '/news', label: 'News', icon: Newspaper },
    { href: '/videos', label: 'Videos', icon: Video },
    { href: '/projects', label: 'Projects', icon: Folder },
    { href: '/youtube-bot', label: 'YouTube Bot', icon: Bot },
  ]

  return (
    <aside className="w-64 bg-white border-r">
      {/* Navigation items */}
    </aside>
  )
}
```

**When to modify**:
- Adding navigation items
- Changing sidebar layout
- Modifying navigation behavior

---

### `/frontend/lib/`

**Purpose**: Utility libraries

#### `api.ts`
**Purpose**: API utility functions

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function fetchNews(): Promise<NewsItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/news`)
  if (!response.ok) throw new Error('Failed to fetch news')
  return response.json()
}

export async function fetchVideos(): Promise<VideoItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/videos`)
  if (!response.ok) throw new Error('Failed to fetch videos')
  return response.json()
}
```

**When to modify**:
- Adding new API functions
- Modifying error handling
- Adding request/response interceptors

---

## Configuration Files

### `/frontend/next.config.js`

**Purpose**: Next.js configuration

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['img.youtube.com', 'localhost'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
}

module.exports = nextConfig
```

**When to modify**:
- Adding image domains
- Configuring environment variables
- Adding webpack config
- Modifying build settings

### `/frontend/tailwind.config.js`

**Purpose**: Tailwind CSS configuration

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**When to modify**:
- Adding custom theme
- Extending colors/fonts
- Adding plugins
- Modifying content paths

---

## Start Scripts

### `/start.sh`

**Purpose**: Start backend and frontend (Mac/Linux)

```bash
#!/bin/bash

# Start backend
cd backend
python3 main.py &
BACKEND_PID=$!

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
```

**When to modify**:
- Adding pre-start checks
- Adding environment setup
- Modifying startup order

### `/start.bat`

**Purpose**: Start backend and frontend (Windows)

```batch
@echo off

REM Start backend
cd backend
start python main.py

REM Start frontend
cd ..\frontend
start npm run dev
```

**When to modify**:
- Adding pre-start checks
- Adding environment setup
- Modifying startup order

---

## Testing Structure

### `/backend/tests/`

**Purpose**: Backend test files

```
tests/
├── test_scrapers.py      # Test scraper functions
├── test_api.py           # Test API endpoints
├── test_database.py      # Test database operations
└── conftest.py           # Test fixtures
```

**When to add tests**:
- Testing new scraper logic
- Testing new API endpoints
- Testing database models

---

## File Naming Conventions

### Backend
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`

### Frontend
- **Files**: `PascalCase.tsx` (components), `lowercase.ts` (utilities)
- **Components**: `PascalCase`
- **Functions**: `camelCase`
- **Constants**: `UPPER_SNAKE_CASE` or `PascalCase`

---

## Import Patterns

### Backend Imports

```python
# Standard library
import os
from datetime import datetime

# Third-party
from fastapi import FastAPI
from sqlalchemy.orm import Session

# Local
from database.db import get_db
from scrapers.news import NewsAggregator
```

### Frontend Imports

```typescript
// Third-party
import { useState, useEffect } from 'react'
import { Home } from 'lucide-react'

// Local
import { fetchNews } from '@/lib/api'
import { DashboardClient } from './DashboardClient'
```

---

## Component Organization

### Server Components (App Router)
- Location: `frontend/app/`
- File extension: `.tsx`
- Default export: Page component
- Can be async for data fetching

### Client Components
- Location: `frontend/app/` and `frontend/components/`
- File extension: `.tsx`
- Directive: `'use client'` at top
- Can use hooks and interactivity

### Shared Components
- Location: `frontend/components/`
- File extension: `.tsx`
- Reusable across pages
- Should be client components if interactive

---

## API Route Patterns

### Backend Routes
```python
@app.get("/api/news")              # List all news
@app.get("/api/news/{id}")         # Get specific news item
@app.post("/api/news")             # Create news item (if needed)
```

### Frontend API Calls
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL
fetch(`${API_BASE_URL}/api/news`)
```

---

## Environment Variables

### Backend `.env`
```bash
DATABASE_URL=sqlite:///./ai_dashboard.db
YOUTUBE_CLIENT_ID=xxx
YOUTUBE_CLIENT_SECRET=xxx
```

### Frontend `.env.local`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Summary

The AI Dashboard follows a clean, organized structure:

- **Backend**: FastAPI with clear separation (database, scrapers, services)
- **Frontend**: Next.js 14 App Router with client/server components
- **Testing**: Separate test directories for backend/frontend
- **Configuration**: Clear separation of config files
- **Documentation**: README.md and inline comments

**Key principles**:
1. Separate concerns (database, scrapers, API, UI)
2. Clear naming conventions (snake_case for Python, PascalCase for React)
3. Organize by feature (news, videos, projects, youtube-bot)
4. Keep configuration separate from code
5. Document complex logic with comments

This structure makes the codebase easy to navigate, understand, and maintain.

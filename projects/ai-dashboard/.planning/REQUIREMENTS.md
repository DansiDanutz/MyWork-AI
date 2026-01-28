# AI Dashboard - Requirements

> Traceability matrix for all features

---

## v1 Requirements

### REQ-1: YouTube Video Scraper

| ID | Requirement | Priority | Status |
| ---- | ------------- | ---------- | -------- |
| REQ-1.1 | Scrape AI/ML videos from YouTube | P0 | Done |
| REQ-1.2 | Calculate quality score (views, likes, engagement) | P0 | Done |
| REQ-1.3 | Store videos in database | P0 | Done |
| REQ-1.4 | Schedule scraping every 8 hours | P0 | Done |
| REQ-1.5 | Filter by minimum views (10K) | P1 | Done |
| REQ-1.6 | Filter by engagement rate (>2%) | P1 | Done |
| REQ-1.7 | API endpoint: GET /api/videos | P0 | Done |
| REQ-1.8 | API endpoint: POST /api/videos/scrape | P1 | Done |

### REQ-2: AI News Aggregator

| ID | Requirement | Priority | Status |
| ---- | ------------- | ---------- | -------- |
| REQ-2.1 | Aggregate from TechCrunch | P0 | Done |
| REQ-2.2 | Aggregate from The Verge | P0 | Done |
| REQ-2.3 | Aggregate from Hacker News | P0 | Done |
| REQ-2.4 | Store news in database | P0 | Done |
| REQ-2.5 | Schedule aggregation every 4 hours | P0 | Done |
| REQ-2.6 | Calculate trending score | P1 | Done |
| REQ-2.7 | API endpoint: GET /api/news | P0 | Done |
| REQ-2.8 | API endpoint: GET /api/news/trending | P1 | Done |
| REQ-2.9 | API endpoint: POST /api/news/scrape | P1 | Done |

### REQ-3: GitHub Trending Projects

| ID | Requirement | Priority | Status |
| ---- | ------------- | ---------- | -------- |
| REQ-3.1 | Fetch trending AI repositories | P0 | Done |
| REQ-3.2 | Track star count and weekly growth | P0 | Done |
| REQ-3.3 | Store projects in database | P0 | Done |
| REQ-3.4 | Schedule scraping every 12 hours | P0 | Done |
| REQ-3.5 | Filter by minimum stars | P1 | Done |
| REQ-3.6 | Categorize by topic | P2 | Pending |
| REQ-3.7 | API endpoint: GET /api/projects | P0 | Done |
| REQ-3.8 | API endpoint: GET /api/projects/trending | P1 | Done |
| REQ-3.9 | API endpoint: POST /api/projects/scrape | P1 | Done |

### REQ-4: YouTube Automation Pipeline

| ID | Requirement | Priority | Status |
| ---- | ------------- | ---------- | -------- |
| REQ-4.1 | Accept user prompt input | P0 | Done |
| REQ-4.2 | Optimize prompt with DSPy/LangChain | P1 | Done |
| REQ-4.3 | Generate video script with Claude | P0 | Done |
| REQ-4.4 | Generate video title and description | P0 | Done |
| REQ-4.5 | Generate video tags | P1 | Done |
| REQ-4.6 | Create HeyGen video | P0 | Done |
| REQ-4.7 | Check HeyGen video status | P0 | Done |
| REQ-4.8 | Preview draft before upload | P0 | Done |
| REQ-4.9 | Edit title/description/tags | P1 | Done |
| REQ-4.10 | Approval workflow | P0 | Done |
| REQ-4.11 | Upload to YouTube | P0 | Pending |
| REQ-4.12 | API endpoint: GET /api/automation | P0 | Done |
| REQ-4.13 | API endpoint: POST /api/automation | P0 | Done |
| REQ-4.14 | API endpoint: PATCH /api/automation/{id} | P1 | Done |
| REQ-4.15 | API endpoint: POST /api/automation/{id}/approve | P0 | Done |

### REQ-5: Dashboard UI

| ID | Requirement | Priority | Status |
| ---- | ------------- | ---------- | -------- |
| REQ-5.1 | Dashboard home with stats | P0 | Done |
| REQ-5.2 | Videos page with list/grid view | P0 | Partial |
| REQ-5.3 | News page with filtering | P0 | Partial |
| REQ-5.4 | Projects page with sorting | P0 | Partial |
| REQ-5.5 | YouTube Bot page with form | P0 | Partial |
| REQ-5.6 | Draft preview and edit | P1 | Pending |
| REQ-5.7 | Approval workflow UI | P1 | Pending |
| REQ-5.8 | Scheduler status display | P2 | Pending |
| REQ-5.9 | Manual scrape trigger buttons | P2 | Pending |

### REQ-6: Infrastructure

| ID | Requirement | Priority | Status |
| ---- | ------------- | ---------- | -------- |
| REQ-6.1 | FastAPI backend setup | P0 | Done |
| REQ-6.2 | SQLite database with models | P0 | Done |
| REQ-6.3 | APScheduler integration | P0 | Done |
| REQ-6.4 | CORS middleware | P0 | Done |
| REQ-6.5 | Next.js frontend setup | P0 | Done |
| REQ-6.6 | Tailwind CSS styling | P0 | Done |
| REQ-6.7 | Start scripts (sh/bat) | P1 | Done |
| REQ-6.8 | Environment configuration | P0 | Done |

---

## v2 Requirements (Future)

| ID | Requirement | Priority |
| ---- | ------------- | ---------- |
| REQ-F1 | Email notifications for trending content | P2 |
| REQ-F2 | RSS feed generation | P2 |
| REQ-F3 | Content bookmarking | P2 |
| REQ-F4 | Video transcript display | P2 |
| REQ-F5 | Project comparison view | P3 |
| REQ-F6 | Custom scraper schedules | P3 |

---

## Out of Scope

- Multi-user authentication
- Public deployment
- Mobile native app
- Real-time WebSocket updates
- In-app video editing

---

## Summary

| Category | Total | Done | Pending |
| ---------- | ------- | ------ | --------- |
| YouTube Scraper | 8 | 8 | 0 |
| News Aggregator | 9 | 9 | 0 |
| GitHub Projects | 9 | 8 | 1 |
| YouTube Automation | 15 | 14 | 1 |
| Dashboard UI | 9 | 4 | 5 |
| Infrastructure | 8 | 8 | 0 |
| **Total** | **58** | **51** | **7** |

**Completion: 88%**

---

*Last Updated: 2026-01-25*

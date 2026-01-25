# AI Dashboard - FastAPI Backend

import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import database
from database import get_db, init_db, YouTubeVideo, AINews, GitHubProject, YouTubeAutomation, ScraperLog

# Import scrapers and services
from scrapers import YouTubeScraper, NewsAggregator, GitHubTrendingScraper
from services import SchedulerService, YouTubeAutomationService, PromptOptimizer

# Initialize services
scheduler = SchedulerService()
youtube_automation = YouTubeAutomationService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting AI Dashboard...")
    init_db()
    scheduler.start()
    yield
    # Shutdown
    logger.info("Shutting down AI Dashboard...")
    scheduler.stop()
    await youtube_automation.close()


# Create FastAPI app
app = FastAPI(
    title="AI Dashboard API",
    description="Personal AI Dashboard for YouTube videos, news, and GitHub projects",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - configured via ALLOWED_ORIGINS env var
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://*.vercel.app"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Pydantic Models ============

class VideoResponse(BaseModel):
    id: int
    video_id: str
    title: str
    channel_name: Optional[str]
    view_count: int
    like_count: int
    quality_score: float
    thumbnail_url: Optional[str]
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


class NewsResponse(BaseModel):
    id: int
    title: str
    url: str
    source: str
    author: Optional[str]
    summary: Optional[str]
    score: int
    comments_count: int
    published_at: Optional[datetime]
    thumbnail_url: Optional[str]

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    id: int
    name: str
    full_name: str
    description: Optional[str]
    url: str
    stars: int
    forks: int
    language: Optional[str]
    topics: Optional[list]
    trending_score: float
    weekly_stars: int
    pushed_at: Optional[datetime]

    class Config:
        from_attributes = True


class AutomationCreate(BaseModel):
    prompt: str
    target_audience: str = "tech enthusiasts"
    video_length: str = "5-10"


class AutomationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    script: Optional[str] = None
    tags: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None


class AutomationResponse(BaseModel):
    id: int
    user_prompt: str
    video_title: str
    video_description: Optional[str]
    video_script: Optional[str]
    video_tags: Optional[list]
    thumbnail_url: Optional[str]
    heygen_video_url: Optional[str]
    youtube_url: Optional[str]
    status: str
    created_at: datetime
    approved_at: Optional[datetime]
    uploaded_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============ API Endpoints ============

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "AI Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "videos": "/api/videos",
            "news": "/api/news",
            "projects": "/api/projects",
            "automation": "/api/automation",
            "scheduler": "/api/scheduler"
        }
    }


# ---------- YouTube Videos ----------

@app.get("/api/videos", response_model=List[VideoResponse])
async def get_videos(
    limit: int = Query(20, ge=1, le=100),
    min_views: int = Query(1000, ge=0),
    db: Session = Depends(get_db)
):
    """Get top AI videos"""
    scraper = YouTubeScraper()
    videos = scraper.get_top_videos(db, limit=limit, min_views=min_views)
    return videos


@app.post("/api/videos/scrape")
async def trigger_video_scrape(db: Session = Depends(get_db)):
    """Manually trigger YouTube scraper"""
    try:
        scraper = YouTubeScraper()
        await scraper.scrape_videos(db)
        return {"status": "success", "message": "YouTube scrape completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- AI News ----------

@app.get("/api/news", response_model=List[NewsResponse])
async def get_news(
    limit: int = Query(50, ge=1, le=200),
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get latest AI news"""
    aggregator = NewsAggregator()
    news = aggregator.get_latest_news(db, limit=limit, source=source)
    return news


@app.get("/api/news/trending", response_model=List[NewsResponse])
async def get_trending_news(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get trending AI news"""
    aggregator = NewsAggregator()
    news = aggregator.get_trending_news(db, limit=limit)
    return news


@app.post("/api/news/scrape")
async def trigger_news_scrape(db: Session = Depends(get_db)):
    """Manually trigger news aggregator"""
    try:
        aggregator = NewsAggregator()
        await aggregator.aggregate_news(db)
        return {"status": "success", "message": "News aggregation completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- GitHub Projects ----------

@app.get("/api/projects", response_model=List[ProjectResponse])
async def get_projects(
    limit: int = Query(20, ge=1, le=100),
    min_stars: int = Query(100, ge=0),
    db: Session = Depends(get_db)
):
    """Get top AI GitHub projects"""
    scraper = GitHubTrendingScraper()
    projects = scraper.get_top_projects(db, limit=limit, min_stars=min_stars)
    return projects


@app.get("/api/projects/trending", response_model=List[ProjectResponse])
async def get_trending_projects(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get trending AI GitHub projects"""
    scraper = GitHubTrendingScraper()
    projects = scraper.get_trending_projects(db, limit=limit)
    return projects


@app.post("/api/projects/scrape")
async def trigger_projects_scrape(db: Session = Depends(get_db)):
    """Manually trigger GitHub scraper"""
    try:
        scraper = GitHubTrendingScraper()
        await scraper.scrape_trending(db)
        return {"status": "success", "message": "GitHub scrape completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- YouTube Automation ----------

@app.get("/api/automation", response_model=List[AutomationResponse])
async def get_automations(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all video automations"""
    drafts = youtube_automation.get_all_drafts(db, status=status, limit=limit)
    return drafts


@app.get("/api/automation/{automation_id}", response_model=AutomationResponse)
async def get_automation(
    automation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific automation"""
    draft = youtube_automation.get_draft(db, automation_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Automation not found")
    return draft


@app.post("/api/automation", response_model=AutomationResponse)
async def create_automation(
    data: AutomationCreate,
    db: Session = Depends(get_db)
):
    """Create a new video automation from prompt"""
    try:
        draft = await youtube_automation.create_video_draft(
            db,
            user_prompt=data.prompt,
            target_audience=data.target_audience,
            video_length=data.video_length
        )
        return draft
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/automation/{automation_id}", response_model=AutomationResponse)
async def update_automation(
    automation_id: int,
    data: AutomationUpdate,
    db: Session = Depends(get_db)
):
    """Update a video automation draft"""
    try:
        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        draft = await youtube_automation.update_draft(db, automation_id, updates)
        return draft
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/automation/{automation_id}/generate-video")
async def generate_video(
    automation_id: int,
    db: Session = Depends(get_db)
):
    """Generate HeyGen video for automation"""
    try:
        draft = await youtube_automation.generate_heygen_video(db, automation_id)
        return {"status": "success", "automation_id": draft.id, "heygen_status": draft.status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/automation/{automation_id}/video-status")
async def check_video_status(
    automation_id: int,
    db: Session = Depends(get_db)
):
    """Check HeyGen video generation status"""
    status = await youtube_automation.check_heygen_status(db, automation_id)
    return status


@app.post("/api/automation/{automation_id}/approve")
async def approve_automation(
    automation_id: int,
    db: Session = Depends(get_db)
):
    """Approve and upload video to YouTube"""
    try:
        draft = await youtube_automation.approve_and_upload(db, automation_id)
        return {
            "status": "success",
            "automation_id": draft.id,
            "youtube_url": draft.youtube_url,
            "upload_status": draft.status
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Scheduler ----------

@app.get("/api/scheduler/status")
async def get_scheduler_status():
    """Get scheduler job status"""
    return scheduler.get_job_status()


@app.post("/api/scheduler/run/{job_id}")
async def run_job(job_id: str):
    """Manually trigger a scheduled job"""
    try:
        await scheduler.run_job_now(job_id)
        return {"status": "success", "message": f"Job {job_id} triggered"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Stats ----------

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    video_count = db.query(YouTubeVideo).count()
    news_count = db.query(AINews).count()
    project_count = db.query(GitHubProject).count()
    automation_count = db.query(YouTubeAutomation).count()

    # Get recent scraper logs
    recent_logs = db.query(ScraperLog).order_by(
        ScraperLog.started_at.desc()
    ).limit(10).all()

    return {
        "videos": video_count,
        "news": news_count,
        "projects": project_count,
        "automations": automation_count,
        "recent_scrapes": [
            {
                "scraper": log.scraper_name,
                "status": log.status,
                "items": log.items_scraped,
                "started_at": log.started_at.isoformat() if log.started_at else None
            }
            for log in recent_logs
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

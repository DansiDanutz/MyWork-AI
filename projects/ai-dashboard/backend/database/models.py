# AI Dashboard - Database Models

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class YouTubeVideo(Base):
    """Scraped AI-related YouTube videos"""
    __tablename__ = "youtube_videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(20), unique=True, index=True)
    title = Column(String(500))
    description = Column(Text)
    channel_name = Column(String(200))
    channel_id = Column(String(50))
    channel_subscribers = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    duration = Column(String(20))
    thumbnail_url = Column(String(500))
    published_at = Column(DateTime)
    quality_score = Column(Float, default=0.0)
    search_query = Column(String(200))
    scraped_at = Column(DateTime, default=datetime.utcnow)

    def calculate_quality_score(self):
        """Calculate video quality score based on engagement metrics"""
        views = self.view_count or 0
        likes = self.like_count or 0
        comments = self.comment_count or 0
        subs = self.channel_subscribers or 0

        # Normalize values (log scale to handle large numbers)
        import math
        norm_views = math.log10(views + 1)
        norm_likes = math.log10(likes + 1)
        norm_comments = math.log10(comments + 1)
        norm_subs = math.log10(subs + 1)

        # Weighted score
        self.quality_score = (
            norm_views * 0.3 +
            norm_likes * 0.25 +
            norm_comments * 0.25 +
            norm_subs * 0.2
        )
        return self.quality_score


class AINews(Base):
    """Aggregated AI news articles"""
    __tablename__ = "ai_news"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(1000), unique=True, index=True)
    url_hash = Column(String(64), unique=True, index=True)
    title = Column(String(500))
    summary = Column(Text)
    source = Column(String(100))  # TechCrunch, Verge, HackerNews, etc.
    author = Column(String(200))
    published_at = Column(DateTime)
    score = Column(Integer, default=0)  # Upvotes/likes if available
    comments_count = Column(Integer, default=0)
    category = Column(String(100))  # ML, LLM, Robotics, etc.
    thumbnail_url = Column(String(500))
    scraped_at = Column(DateTime, default=datetime.utcnow)


class GitHubProject(Base):
    """Top open source AI projects from GitHub"""
    __tablename__ = "github_projects"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, unique=True, index=True)
    name = Column(String(200))
    full_name = Column(String(300))  # owner/repo
    description = Column(Text)
    url = Column(String(500))
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    watchers = Column(Integer, default=0)
    open_issues = Column(Integer, default=0)
    language = Column(String(50))
    topics = Column(JSON)  # List of topics
    license = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    pushed_at = Column(DateTime)
    trending_score = Column(Float, default=0.0)
    weekly_stars = Column(Integer, default=0)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    def calculate_trending_score(self, previous_stars=0):
        """Calculate trending score based on stars growth and activity"""
        import math

        stars = self.stars or 0
        forks = self.forks or 0
        weekly_growth = stars - previous_stars

        # Weighted trending score
        self.trending_score = (
            math.log10(stars + 1) * 0.4 +
            math.log10(forks + 1) * 0.2 +
            math.log10(weekly_growth + 1) * 0.4
        )
        self.weekly_stars = weekly_growth
        return self.trending_score


class YouTubeAutomation(Base):
    """YouTube video automation pipeline records"""
    __tablename__ = "youtube_automation"

    id = Column(Integer, primary_key=True, index=True)

    # Input
    user_prompt = Column(Text)
    optimized_prompt = Column(Text)

    # Generated content
    video_title = Column(String(200))
    video_description = Column(Text)
    video_script = Column(Text)
    video_tags = Column(JSON)

    # HeyGen
    heygen_video_id = Column(String(100))
    heygen_video_url = Column(String(500))

    # Thumbnail
    thumbnail_url = Column(String(500))
    thumbnail_prompt = Column(Text)

    # Status
    status = Column(String(50), default="draft")  # draft, pending_review, approved, uploaded, failed
    youtube_video_id = Column(String(20))
    youtube_url = Column(String(200))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    uploaded_at = Column(DateTime)

    # User edits (stored as JSON for flexibility)
    user_edits = Column(JSON)


class ScraperLog(Base):
    """Log of scraper runs for monitoring"""
    __tablename__ = "scraper_logs"

    id = Column(Integer, primary_key=True, index=True)
    scraper_name = Column(String(100))  # youtube, news, github
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String(50))  # running, success, failed
    items_scraped = Column(Integer, default=0)
    error_message = Column(Text)

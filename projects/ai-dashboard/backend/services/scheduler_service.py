# AI Dashboard - Scheduler Service

import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from database import get_db_session
from scrapers import YouTubeScraper, NewsAggregator, GitHubTrendingScraper

logger = logging.getLogger(__name__)


class SchedulerService:
    """Manages scheduled scraping tasks"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.youtube_scraper = YouTubeScraper()
        self.news_aggregator = NewsAggregator()
        self.github_scraper = GitHubTrendingScraper()

    def start(self):
        """Start the scheduler with all jobs"""
        # YouTube scraper - every 8 hours
        self.scheduler.add_job(
            self._run_youtube_scraper,
            IntervalTrigger(hours=8),
            id="youtube_scraper",
            name="YouTube AI Video Scraper",
            replace_existing=True,
            next_run_time=datetime.now()  # Run immediately on start
        )

        # News aggregator - every 4 hours
        self.scheduler.add_job(
            self._run_news_aggregator,
            IntervalTrigger(hours=4),
            id="news_aggregator",
            name="AI News Aggregator",
            replace_existing=True,
            next_run_time=datetime.now()
        )

        # GitHub trending - every 12 hours
        self.scheduler.add_job(
            self._run_github_scraper,
            IntervalTrigger(hours=12),
            id="github_scraper",
            name="GitHub Trending AI Projects",
            replace_existing=True,
            next_run_time=datetime.now()
        )

        self.scheduler.start()
        logger.info("Scheduler started with all jobs")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    async def _run_youtube_scraper(self):
        """Run YouTube scraper job"""
        logger.info("Starting YouTube scraper job...")
        try:
            with get_db_session() as db:
                await self.youtube_scraper.scrape_videos(db)
            logger.info("YouTube scraper job completed")
        except Exception as e:
            logger.error(f"YouTube scraper job failed: {e}")

    async def _run_news_aggregator(self):
        """Run news aggregator job"""
        logger.info("Starting news aggregator job...")
        try:
            with get_db_session() as db:
                await self.news_aggregator.aggregate_news(db)
            logger.info("News aggregator job completed")
        except Exception as e:
            logger.error(f"News aggregator job failed: {e}")

    async def _run_github_scraper(self):
        """Run GitHub scraper job"""
        logger.info("Starting GitHub scraper job...")
        try:
            with get_db_session() as db:
                await self.github_scraper.scrape_trending(db)
            logger.info("GitHub scraper job completed")
        except Exception as e:
            logger.error(f"GitHub scraper job failed: {e}")

    def get_job_status(self) -> dict:
        """Get status of all scheduled jobs"""
        jobs = {}
        for job in self.scheduler.get_jobs():
            jobs[job.id] = {
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
        return jobs

    async def run_job_now(self, job_id: str):
        """Manually trigger a job"""
        if job_id == "youtube_scraper":
            await self._run_youtube_scraper()
        elif job_id == "news_aggregator":
            await self._run_news_aggregator()
        elif job_id == "github_scraper":
            await self._run_github_scraper()
        else:
            raise ValueError(f"Unknown job: {job_id}")

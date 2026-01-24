# AI Dashboard - YouTube AI Video Scraper

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import httpx
from apify_client import ApifyClient
from sqlalchemy.orm import Session

from database.models import YouTubeVideo, ScraperLog

logger = logging.getLogger(__name__)

# AI-related search queries
AI_SEARCH_QUERIES = [
    "AI tutorial 2025",
    "machine learning tutorial",
    "ChatGPT tutorial",
    "Claude AI",
    "LLM explained",
    "artificial intelligence news",
    "deep learning project",
    "AI coding assistant",
    "GPT-4 tutorial",
    "AI agents tutorial",
    "RAG tutorial",
    "AI automation",
]


class YouTubeScraper:
    """Scrapes top AI-related YouTube videos using Apify"""

    def __init__(self, apify_api_key: Optional[str] = None):
        self.api_key = apify_api_key or os.getenv("APIFY_API_KEY")
        if not self.api_key:
            logger.warning("APIFY_API_KEY not set - YouTube scraper will be limited")
            self.client = None
        else:
            self.client = ApifyClient(self.api_key)

        # Fallback: YouTube Data API
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")

    async def scrape_videos(
        self,
        db: Session,
        queries: List[str] = None,
        max_results_per_query: int = 20,
        published_after_days: int = 7
    ) -> List[Dict]:
        """
        Scrape AI-related videos from YouTube

        Args:
            db: Database session
            queries: List of search queries (defaults to AI_SEARCH_QUERIES)
            max_results_per_query: Max videos per query
            published_after_days: Only get videos from last N days

        Returns:
            List of scraped video data
        """
        queries = queries or AI_SEARCH_QUERIES
        all_videos = []

        # Log scraper start
        log = ScraperLog(
            scraper_name="youtube",
            status="running"
        )
        db.add(log)
        db.commit()

        try:
            if self.client:
                # Use Apify YouTube Scraper
                all_videos = await self._scrape_with_apify(
                    queries, max_results_per_query, published_after_days
                )
            elif self.youtube_api_key:
                # Fallback to YouTube Data API
                all_videos = await self._scrape_with_youtube_api(
                    queries, max_results_per_query, published_after_days
                )
            else:
                raise ValueError("No API keys configured for YouTube scraping")

            # Save videos to database
            saved_count = 0
            for video_data in all_videos:
                saved = self._save_video(db, video_data)
                if saved:
                    saved_count += 1

            # Update log
            log.completed_at = datetime.utcnow()
            log.status = "success"
            log.items_scraped = saved_count
            db.commit()

            logger.info(f"YouTube scraper completed: {saved_count} videos saved")
            return all_videos

        except Exception as e:
            log.completed_at = datetime.utcnow()
            log.status = "failed"
            log.error_message = str(e)
            db.commit()
            logger.error(f"YouTube scraper failed: {e}")
            raise

    async def _scrape_with_apify(
        self,
        queries: List[str],
        max_results: int,
        published_after_days: int
    ) -> List[Dict]:
        """Scrape using Apify YouTube Scraper actor"""
        all_videos = []

        for query in queries:
            logger.info(f"Scraping YouTube for: {query}")

            # Run the Apify actor
            run_input = {
                "searchKeywords": query,
                "maxResults": max_results,
                "sortBy": "rating",  # or "viewCount", "date"
                "type": "video",
                "uploadDate": "week" if published_after_days <= 7 else "month",
            }

            try:
                run = self.client.actor("streamers/youtube-scraper").call(run_input=run_input)

                # Fetch results
                for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                    video = self._parse_apify_video(item, query)
                    if video:
                        all_videos.append(video)

            except Exception as e:
                logger.error(f"Apify scrape failed for '{query}': {e}")
                continue

        return all_videos

    async def _scrape_with_youtube_api(
        self,
        queries: List[str],
        max_results: int,
        published_after_days: int
    ) -> List[Dict]:
        """Fallback: Scrape using YouTube Data API"""
        all_videos = []
        published_after = (datetime.utcnow() - timedelta(days=published_after_days)).isoformat() + "Z"

        async with httpx.AsyncClient() as client:
            for query in queries:
                logger.info(f"Searching YouTube API for: {query}")

                try:
                    # Search for videos
                    search_url = "https://www.googleapis.com/youtube/v3/search"
                    params = {
                        "part": "snippet",
                        "q": query,
                        "type": "video",
                        "maxResults": max_results,
                        "order": "rating",
                        "publishedAfter": published_after,
                        "key": self.youtube_api_key
                    }

                    response = await client.get(search_url, params=params)
                    response.raise_for_status()
                    data = response.json()

                    video_ids = [item["id"]["videoId"] for item in data.get("items", [])]

                    if video_ids:
                        # Get video statistics
                        stats_url = "https://www.googleapis.com/youtube/v3/videos"
                        stats_params = {
                            "part": "statistics,contentDetails,snippet",
                            "id": ",".join(video_ids),
                            "key": self.youtube_api_key
                        }

                        stats_response = await client.get(stats_url, params=stats_params)
                        stats_response.raise_for_status()
                        stats_data = stats_response.json()

                        for item in stats_data.get("items", []):
                            video = self._parse_youtube_api_video(item, query)
                            if video:
                                all_videos.append(video)

                except Exception as e:
                    logger.error(f"YouTube API search failed for '{query}': {e}")
                    continue

        return all_videos

    def _parse_apify_video(self, item: Dict, query: str) -> Optional[Dict]:
        """Parse video data from Apify response"""
        try:
            return {
                "video_id": item.get("id"),
                "title": item.get("title"),
                "description": item.get("description", ""),
                "channel_name": item.get("channelName"),
                "channel_id": item.get("channelId"),
                "channel_subscribers": item.get("subscriberCount", 0),
                "view_count": item.get("viewCount", 0),
                "like_count": item.get("likeCount", 0),
                "comment_count": item.get("commentCount", 0),
                "duration": item.get("duration"),
                "thumbnail_url": item.get("thumbnailUrl"),
                "published_at": item.get("uploadDate"),
                "search_query": query,
            }
        except Exception as e:
            logger.error(f"Failed to parse Apify video: {e}")
            return None

    def _parse_youtube_api_video(self, item: Dict, query: str) -> Optional[Dict]:
        """Parse video data from YouTube API response"""
        try:
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})

            return {
                "video_id": item.get("id"),
                "title": snippet.get("title"),
                "description": snippet.get("description", ""),
                "channel_name": snippet.get("channelTitle"),
                "channel_id": snippet.get("channelId"),
                "channel_subscribers": 0,  # Not available in this API call
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "duration": content.get("duration"),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "published_at": snippet.get("publishedAt"),
                "search_query": query,
            }
        except Exception as e:
            logger.error(f"Failed to parse YouTube API video: {e}")
            return None

    def _save_video(self, db: Session, video_data: Dict) -> bool:
        """Save video to database, skip if already exists"""
        try:
            # Check if video already exists
            existing = db.query(YouTubeVideo).filter(
                YouTubeVideo.video_id == video_data["video_id"]
            ).first()

            if existing:
                # Update stats
                existing.view_count = video_data["view_count"]
                existing.like_count = video_data["like_count"]
                existing.comment_count = video_data["comment_count"]
                existing.calculate_quality_score()
                return False

            # Parse published date
            published_at = video_data.get("published_at")
            if isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                except:
                    published_at = datetime.utcnow()

            # Create new video
            video = YouTubeVideo(
                video_id=video_data["video_id"],
                title=video_data["title"],
                description=video_data.get("description", ""),
                channel_name=video_data.get("channel_name"),
                channel_id=video_data.get("channel_id"),
                channel_subscribers=video_data.get("channel_subscribers", 0),
                view_count=video_data.get("view_count", 0),
                like_count=video_data.get("like_count", 0),
                comment_count=video_data.get("comment_count", 0),
                duration=video_data.get("duration"),
                thumbnail_url=video_data.get("thumbnail_url"),
                published_at=published_at,
                search_query=video_data.get("search_query"),
            )
            video.calculate_quality_score()

            db.add(video)
            db.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to save video: {e}")
            db.rollback()
            return False

    def get_top_videos(
        self,
        db: Session,
        limit: int = 20,
        min_views: int = 1000,
        days: int = 7
    ) -> List[YouTubeVideo]:
        """Get top rated AI videos from database"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        return db.query(YouTubeVideo).filter(
            YouTubeVideo.view_count >= min_views,
            YouTubeVideo.scraped_at >= cutoff_date
        ).order_by(
            YouTubeVideo.quality_score.desc()
        ).limit(limit).all()

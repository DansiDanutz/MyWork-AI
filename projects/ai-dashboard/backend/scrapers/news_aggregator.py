# AI Dashboard - AI News Aggregator

import os
import logging
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import httpx
import feedparser
from sqlalchemy.orm import Session

from database.models import AINews, ScraperLog

logger = logging.getLogger(__name__)

# RSS Feed sources for AI news
RSS_FEEDS = {
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "MIT Technology Review AI": "https://www.technologyreview.com/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "Towards Data Science": "https://towardsdatascience.com/feed",
    "Google AI Blog": "https://blog.google/technology/ai/rss/",
    "OpenAI Blog": "https://openai.com/blog/rss/",
    "Anthropic Research": "https://www.anthropic.com/feed.xml",
    "Hugging Face Blog": "https://huggingface.co/blog/feed.xml",
}

# Hacker News API endpoints
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HN_ALGOLIA_API = "https://hn.algolia.com/api/v1"


class NewsAggregator:
    """Aggregates AI news from multiple sources"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def aggregate_news(
        self,
        db: Session,
        include_rss: bool = True,
        include_hackernews: bool = True,
        max_items_per_source: int = 20,
    ) -> List[Dict]:
        """
        Aggregate AI news from all sources

        Args:
            db: Database session
            include_rss: Include RSS feeds
            include_hackernews: Include Hacker News
            max_items_per_source: Max items per source

        Returns:
            List of news articles
        """
        all_news = []

        # Log scraper start
        log = ScraperLog(scraper_name="news", status="running")
        db.add(log)
        db.commit()

        try:
            if include_rss:
                rss_news = await self._fetch_rss_feeds(max_items_per_source)
                all_news.extend(rss_news)

            if include_hackernews:
                hn_news = await self._fetch_hackernews(max_items_per_source)
                all_news.extend(hn_news)

            # Save to database with deduplication
            saved_count = 0
            for article in all_news:
                saved = self._save_article(db, article)
                if saved:
                    saved_count += 1

            # Update log
            log.completed_at = datetime.utcnow()
            log.status = "success"
            log.items_scraped = saved_count
            db.commit()

            logger.info(f"News aggregator completed: {saved_count} articles saved")
            return all_news

        except Exception as e:
            log.completed_at = datetime.utcnow()
            log.status = "failed"
            log.error_message = str(e)
            db.commit()
            logger.error(f"News aggregator failed: {e}")
            raise

    async def _fetch_rss_feeds(self, max_items: int) -> List[Dict]:
        """Fetch articles from RSS feeds"""
        articles = []

        for source_name, feed_url in RSS_FEEDS.items():
            logger.info(f"Fetching RSS: {source_name}")

            try:
                response = await self.client.get(feed_url)
                response.raise_for_status()

                feed = feedparser.parse(response.text)

                for entry in feed.entries[:max_items]:
                    article = self._parse_rss_entry(entry, source_name)
                    if article:
                        articles.append(article)

            except Exception as e:
                logger.error(f"Failed to fetch {source_name}: {e}")
                continue

        return articles

    async def _fetch_hackernews(self, max_items: int) -> List[Dict]:
        """Fetch AI-related stories from Hacker News using Algolia API"""
        articles = []

        # Search queries for AI content
        ai_queries = ["AI", "GPT", "LLM", "machine learning", "Claude", "OpenAI", "Anthropic"]

        for query in ai_queries[:3]:  # Limit queries to avoid rate limiting
            logger.info(f"Fetching Hacker News: {query}")

            try:
                url = f"{HN_ALGOLIA_API}/search"
                params = {
                    "query": query,
                    "tags": "story",
                    "numericFilters": f"created_at_i>{int((datetime.utcnow() - timedelta(days=7)).timestamp())}",
                    "hitsPerPage": max_items,
                }

                response = await self.client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                for hit in data.get("hits", []):
                    article = self._parse_hn_story(hit)
                    if article:
                        articles.append(article)

            except Exception as e:
                logger.error(f"Failed to fetch HN for '{query}': {e}")
                continue

        return articles

    def _parse_rss_entry(self, entry: Dict, source: str) -> Optional[Dict]:
        """Parse RSS feed entry into article format"""
        try:
            # Get URL
            url = entry.get("link", "")
            if not url:
                return None

            # Parse published date
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if published:
                published_at = datetime(*published[:6])
            else:
                published_at = datetime.utcnow()

            # Get thumbnail
            thumbnail = None
            if "media_thumbnail" in entry:
                thumbnail = entry["media_thumbnail"][0].get("url")
            elif "media_content" in entry:
                thumbnail = entry["media_content"][0].get("url")

            # Get author
            author = entry.get("author", "")
            if not author and "authors" in entry:
                author = entry["authors"][0].get("name", "") if entry["authors"] else ""

            return {
                "url": url,
                "title": entry.get("title", ""),
                "summary": entry.get("summary", entry.get("description", ""))[:500],
                "source": source,
                "author": author,
                "published_at": published_at,
                "thumbnail_url": thumbnail,
                "category": "AI",
            }

        except Exception as e:
            logger.error(f"Failed to parse RSS entry: {e}")
            return None

    def _parse_hn_story(self, hit: Dict) -> Optional[Dict]:
        """Parse Hacker News story into article format"""
        try:
            url = hit.get("url", "")
            if not url:
                # HN self-post, link to HN comments
                url = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"

            # Parse created date
            created_at = hit.get("created_at")
            if created_at:
                try:
                    published_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                except:
                    published_at = datetime.utcnow()
            else:
                published_at = datetime.utcnow()

            return {
                "url": url,
                "title": hit.get("title", ""),
                "summary": "",  # HN doesn't have summaries
                "source": "Hacker News",
                "author": hit.get("author", ""),
                "published_at": published_at,
                "score": hit.get("points", 0),
                "comments_count": hit.get("num_comments", 0),
                "category": "AI",
            }

        except Exception as e:
            logger.error(f"Failed to parse HN story: {e}")
            return None

    def _save_article(self, db: Session, article_data: Dict) -> bool:
        """Save article to database with deduplication"""
        try:
            # Generate URL hash for deduplication
            url_hash = hashlib.sha256(article_data["url"].encode()).hexdigest()

            # Check if article already exists
            existing = db.query(AINews).filter(AINews.url_hash == url_hash).first()

            if existing:
                # Update score if applicable
                if article_data.get("score"):
                    existing.score = article_data["score"]
                if article_data.get("comments_count"):
                    existing.comments_count = article_data["comments_count"]
                return False

            # Create new article
            article = AINews(
                url=article_data["url"],
                url_hash=url_hash,
                title=article_data["title"],
                summary=article_data.get("summary", ""),
                source=article_data["source"],
                author=article_data.get("author", ""),
                published_at=article_data.get("published_at", datetime.utcnow()),
                score=article_data.get("score", 0),
                comments_count=article_data.get("comments_count", 0),
                category=article_data.get("category", "AI"),
                thumbnail_url=article_data.get("thumbnail_url"),
            )

            db.add(article)
            db.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to save article: {e}")
            db.rollback()
            return False

    def get_latest_news(
        self, db: Session, limit: int = 50, source: Optional[str] = None, days: int = 7
    ) -> List[AINews]:
        """Get latest AI news from database"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = db.query(AINews).filter(AINews.scraped_at >= cutoff_date)

        if source:
            query = query.filter(AINews.source == source)

        return query.order_by(AINews.published_at.desc()).limit(limit).all()

    def get_trending_news(self, db: Session, limit: int = 20, days: int = 3) -> List[AINews]:
        """Get trending AI news (by score/comments)"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        return (
            db.query(AINews)
            .filter(AINews.scraped_at >= cutoff_date)
            .order_by((AINews.score + AINews.comments_count).desc())
            .limit(limit)
            .all()
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

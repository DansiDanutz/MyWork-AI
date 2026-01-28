# AI Dashboard - GitHub Trending AI Projects Scraper

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import httpx
from sqlalchemy.orm import Session

from database.models import GitHubProject, ScraperLog

logger = logging.getLogger(__name__)

# GitHub API base URL
GITHUB_API = "https://api.github.com"

# AI/ML related topics to search
AI_TOPICS = [
    "machine-learning",
    "deep-learning",
    "artificial-intelligence",
    "llm",
    "gpt",
    "transformer",
    "neural-network",
    "nlp",
    "computer-vision",
    "reinforcement-learning",
]

# Popular AI-related search queries
AI_SEARCH_QUERIES = [
    "language:python topic:machine-learning stars:>1000",
    "language:python topic:deep-learning stars:>500",
    "topic:llm stars:>500",
    "topic:gpt stars:>1000",
    "topic:transformer stars:>500",
    "topic:rag stars:>100",
    "topic:ai-agents stars:>100",
]


class GitHubTrendingScraper:
    """Scrapes trending AI/ML projects from GitHub"""

    def __init__(self, github_token: Optional[str] = None):
        self.token = github_token or os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    async def scrape_trending(
        self,
        db: Session,
        queries: List[str] = None,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Scrape trending AI projects from GitHub

        Args:
            db: Database session
            queries: Search queries (defaults to AI_SEARCH_QUERIES)
            max_results: Maximum total results

        Returns:
            List of repository data
        """
        queries = queries or AI_SEARCH_QUERIES
        all_repos = []
        seen_ids = set()

        # Log scraper start
        log = ScraperLog(
            scraper_name="github",
            status="running"
        )
        db.add(log)
        db.commit()

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                for query in queries:
                    if len(all_repos) >= max_results:
                        break

                    logger.info(f"Searching GitHub: {query}")

                    try:
                        repos = await self._search_repositories(client, query)

                        for repo in repos:
                            if repo["id"] not in seen_ids:
                                seen_ids.add(repo["id"])
                                all_repos.append(repo)

                                if len(all_repos) >= max_results:
                                    break

                    except Exception as e:
                        logger.error(f"GitHub search failed for '{query}': {e}")
                        continue

            # Save repositories to database
            saved_count = 0
            for repo_data in all_repos:
                saved = self._save_repository(db, repo_data)
                if saved:
                    saved_count += 1

            # Update log
            log.completed_at = datetime.utcnow()
            log.status = "success"
            log.items_scraped = saved_count
            db.commit()

            logger.info(f"GitHub scraper completed: {saved_count} repositories saved")
            return all_repos

        except Exception as e:
            log.completed_at = datetime.utcnow()
            log.status = "failed"
            log.error_message = str(e)
            db.commit()
            logger.error(f"GitHub scraper failed: {e}")
            raise

    async def _search_repositories(
        self,
        client: httpx.AsyncClient,
        query: str,
        per_page: int = 30
    ) -> List[Dict]:
        """Search GitHub repositories with rate limit handling"""
        url = f"{GITHUB_API}/search/repositories"

        # Add date filter for recent activity
        pushed_after = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        full_query = f"{query} pushed:>{pushed_after}"

        params = {
            "q": full_query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page
        }

        response = await client.get(url, params=params)

        # Check rate limit
        remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
        if remaining == 0:
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            wait_seconds = max(0, reset_time - int(datetime.utcnow().timestamp()))
            logger.warning(f"GitHub rate limit exceeded. Resets in {wait_seconds}s")
            raise Exception(f"GitHub rate limit exceeded. Try again in {wait_seconds} seconds.")

        response.raise_for_status()
        data = response.json()

        repos = []
        for item in data.get("items", []):
            repo = self._parse_repository(item)
            if repo:
                repos.append(repo)

        return repos

    def _parse_repository(self, item: Dict) -> Optional[Dict]:
        """Parse repository data from GitHub API response"""
        try:
            # Parse dates
            created_at = item.get("created_at")
            if created_at:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

            updated_at = item.get("updated_at")
            if updated_at:
                updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

            pushed_at = item.get("pushed_at")
            if pushed_at:
                pushed_at = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))

            return {
                "repo_id": item["id"],
                "name": item["name"],
                "full_name": item["full_name"],
                "description": item.get("description", ""),
                "url": item["html_url"],
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "watchers": item.get("watchers_count", 0),
                "open_issues": item.get("open_issues_count", 0),
                "language": item.get("language"),
                "topics": item.get("topics", []),
                "license": item.get("license", {}).get("name") if item.get("license") else None,
                "created_at": created_at,
                "updated_at": updated_at,
                "pushed_at": pushed_at,
            }

        except Exception as e:
            logger.error(f"Failed to parse repository: {e}")
            return None

    def _save_repository(self, db: Session, repo_data: Dict) -> bool:
        """Save repository to database"""
        try:
            # Check if repository already exists
            existing = db.query(GitHubProject).filter(
                GitHubProject.repo_id == repo_data["repo_id"]
            ).first()

            if existing:
                # Update stats and calculate trending score
                previous_stars = existing.stars
                existing.stars = repo_data["stars"]
                existing.forks = repo_data["forks"]
                existing.watchers = repo_data["watchers"]
                existing.open_issues = repo_data["open_issues"]
                existing.pushed_at = repo_data["pushed_at"]
                existing.topics = repo_data["topics"]
                existing.calculate_trending_score(previous_stars)
                return False

            # Create new repository
            repo = GitHubProject(
                repo_id=repo_data["repo_id"],
                name=repo_data["name"],
                full_name=repo_data["full_name"],
                description=repo_data.get("description", ""),
                url=repo_data["url"],
                stars=repo_data["stars"],
                forks=repo_data["forks"],
                watchers=repo_data["watchers"],
                open_issues=repo_data["open_issues"],
                language=repo_data.get("language"),
                topics=repo_data.get("topics", []),
                license=repo_data.get("license"),
                created_at=repo_data.get("created_at"),
                updated_at=repo_data.get("updated_at"),
                pushed_at=repo_data.get("pushed_at"),
            )
            repo.calculate_trending_score()

            db.add(repo)
            db.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to save repository: {e}")
            db.rollback()
            return False

    def get_top_projects(
        self,
        db: Session,
        limit: int = 20,
        min_stars: int = 100
    ) -> List[GitHubProject]:
        """Get top AI projects by stars"""
        return db.query(GitHubProject).filter(
            GitHubProject.stars >= min_stars
        ).order_by(
            GitHubProject.stars.desc()
        ).limit(limit).all()

    def get_trending_projects(
        self,
        db: Session,
        limit: int = 20
    ) -> List[GitHubProject]:
        """Get trending AI projects by weekly growth"""
        return db.query(GitHubProject).order_by(
            GitHubProject.trending_score.desc()
        ).limit(limit).all()

    def get_recently_updated(
        self,
        db: Session,
        limit: int = 20,
        days: int = 7
    ) -> List[GitHubProject]:
        """Get recently updated AI projects"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        return db.query(GitHubProject).filter(
            GitHubProject.pushed_at >= cutoff_date
        ).order_by(
            GitHubProject.pushed_at.desc()
        ).limit(limit).all()

# AI Dashboard - YouTube Automation Service

import asyncio
import logging
import mimetypes
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
import httpx
from sqlalchemy.orm import Session

from database.models import YouTubeAutomation
from .prompt_optimizer import PromptOptimizer

logger = logging.getLogger(__name__)


class YouTubeAutomationService:
    """
    Complete YouTube video automation pipeline:
    1. Prompt optimization (DSPy)
    2. Script generation (Claude)
    3. Video creation (HeyGen)
    4. Preview & Edit (User)
    5. Upload (YouTube API)
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        heygen_api_key: Optional[str] = None,
        youtube_api_key: Optional[str] = None,
    ):
        self.anthropic_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.heygen_key = heygen_api_key or os.getenv("HEYGEN_API_KEY")
        self.youtube_key = youtube_api_key or os.getenv("YOUTUBE_API_KEY")
        self.youtube_client_id = os.getenv("YOUTUBE_OAUTH_CLIENT_ID")
        self.youtube_client_secret = os.getenv("YOUTUBE_OAUTH_CLIENT_SECRET")
        self.youtube_refresh_token = os.getenv("YOUTUBE_OAUTH_REFRESH_TOKEN")
        self.youtube_token_uri = os.getenv(
            "YOUTUBE_OAUTH_TOKEN_URI", "https://oauth2.googleapis.com/token"
        )
        self.youtube_privacy_status = os.getenv("YOUTUBE_UPLOAD_PRIVACY_STATUS", "unlisted")
        self.youtube_category_id = os.getenv("YOUTUBE_UPLOAD_CATEGORY_ID", "28")
        self.youtube_upload_dir = os.getenv("YOUTUBE_UPLOAD_DIR")
        self.simulate_upload = os.getenv("SIMULATE_YOUTUBE_UPLOAD", "").strip().lower() in {
            "1",
            "true",
            "yes",
        }

        self.prompt_optimizer = PromptOptimizer(self.anthropic_key)
        self.client = httpx.AsyncClient(timeout=60.0)

    def _has_upload_credentials(self) -> bool:
        return bool(self.youtube_client_id and self.youtube_client_secret and self.youtube_refresh_token)

    def _normalize_tags(self, tags: Optional[object]) -> list[str] | None:
        if not tags:
            return None
        if isinstance(tags, str):
            parsed = [item.strip() for item in tags.split(",") if item.strip()]
            return parsed or None
        if isinstance(tags, list):
            parsed = [str(item).strip() for item in tags if str(item).strip()]
            return parsed or None
        return None

    def _build_video_metadata(self, automation: YouTubeAutomation) -> dict:
        tags = self._normalize_tags(automation.video_tags)
        snippet = {
            "title": (automation.video_title or "Untitled Video")[:100],
            "description": automation.video_description or "",
            "categoryId": str(self.youtube_category_id),
        }
        if tags:
            snippet["tags"] = tags

        return {
            "snippet": snippet,
            "status": {"privacyStatus": self.youtube_privacy_status},
        }

    async def _download_asset(self, url: str, label: str, fallback_suffix: str) -> tuple[Path, str]:
        async with self.client.stream("GET", url, follow_redirects=True) as response:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            extension = (
                mimetypes.guess_extension(content_type.split(";")[0].strip())
                or Path(url).suffix
                or fallback_suffix
            )

            upload_dir = self.youtube_upload_dir or None
            if upload_dir:
                Path(upload_dir).mkdir(parents=True, exist_ok=True)

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension, dir=upload_dir)
            try:
                async for chunk in response.aiter_bytes(chunk_size=1024 * 1024):
                    temp_file.write(chunk)
            finally:
                temp_file.close()

        logger.info("Downloaded %s asset to %s", label, temp_file.name)
        return Path(temp_file.name), content_type

    def _build_youtube_client(self):
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        credentials = Credentials(
            token=None,
            refresh_token=self.youtube_refresh_token,
            token_uri=self.youtube_token_uri,
            client_id=self.youtube_client_id,
            client_secret=self.youtube_client_secret,
            scopes=["https://www.googleapis.com/auth/youtube.upload"],
        )
        credentials.refresh(Request())
        return build("youtube", "v3", credentials=credentials, cache_discovery=False)

    def _upload_video_and_thumbnail(
        self,
        video_path: Path,
        metadata: dict,
        thumbnail_path: Optional[Path],
        thumbnail_mime: Optional[str],
    ) -> str:
        from googleapiclient.http import MediaFileUpload

        youtube = self._build_youtube_client()
        media = MediaFileUpload(str(video_path), mimetype="video/*", resumable=True)
        response = (
            youtube.videos()
            .insert(part="snippet,status", body=metadata, media_body=media)
            .execute()
        )
        video_id = response.get("id")
        if not video_id:
            raise ValueError("YouTube upload succeeded but no video ID returned")

        if thumbnail_path:
            thumb_media = MediaFileUpload(
                str(thumbnail_path), mimetype=thumbnail_mime or "image/png", resumable=False
            )
            youtube.thumbnails().set(videoId=video_id, media_body=thumb_media).execute()

        return video_id

    async def create_video_draft(
        self,
        db: Session,
        user_prompt: str,
        target_audience: str = "tech enthusiasts",
        video_length: str = "5-10",
    ) -> YouTubeAutomation:
        """
        Create a video draft from user prompt

        Args:
            db: Database session
            user_prompt: User's video idea
            target_audience: Target audience
            video_length: Target length in minutes

        Returns:
            YouTubeAutomation record in draft status
        """
        # Step 1: Optimize prompt
        optimized_prompt = self.prompt_optimizer.optimize_prompt(user_prompt)

        # Step 2: Generate video content
        content = self.prompt_optimizer.generate_video_content(
            topic=user_prompt, target_audience=target_audience, video_length=video_length
        )

        # Step 3: Create database record
        automation = YouTubeAutomation(
            user_prompt=user_prompt,
            optimized_prompt=optimized_prompt,
            video_title=content["title"],
            video_description=content["description"],
            video_script=content["script"],
            video_tags=content["tags"],
            thumbnail_prompt=content.get("thumbnail_prompt"),
            status="draft",
        )

        db.add(automation)
        db.commit()
        db.refresh(automation)

        logger.info(f"Created video draft: {automation.id}")
        return automation

    async def generate_heygen_video(
        self,
        db: Session,
        automation_id: int,
        avatar_id: str = "Kristin_public_3_20240108",
        voice_id: str = "1bd001e7e50f421d891986aad5158bc8",
    ) -> YouTubeAutomation:
        """
        Generate video using HeyGen API

        Args:
            db: Database session
            automation_id: YouTubeAutomation record ID
            avatar_id: HeyGen avatar ID
            voice_id: HeyGen voice ID

        Returns:
            Updated YouTubeAutomation record
        """
        automation = (
            db.query(YouTubeAutomation).filter(YouTubeAutomation.id == automation_id).first()
        )

        if not automation:
            raise ValueError(f"Automation {automation_id} not found")

        if not self.heygen_key:
            logger.warning("HeyGen API key not configured")
            automation.status = "pending_review"
            automation.heygen_video_url = "https://example.com/placeholder-video.mp4"
            db.commit()
            return automation

        try:
            # Create HeyGen video
            url = "https://api.heygen.com/v2/video/generate"
            headers = {"X-Api-Key": self.heygen_key, "Content-Type": "application/json"}

            payload = {
                "video_inputs": [
                    {
                        "character": {
                            "type": "avatar",
                            "avatar_id": avatar_id,
                            "avatar_style": "normal",
                        },
                        "voice": {
                            "type": "text",
                            "input_text": automation.video_script,
                            "voice_id": voice_id,
                        },
                    }
                ],
                "dimension": {"width": 1920, "height": 1080},
            }

            response = await self.client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            automation.heygen_video_id = data.get("data", {}).get("video_id")
            automation.status = "generating"
            db.commit()

            logger.info(f"HeyGen video generation started: {automation.heygen_video_id}")
            return automation

        except httpx.HTTPStatusError as e:
            error_detail = f"HeyGen API error: {e.response.status_code}"
            try:
                error_body = e.response.json()
                error_detail = f"HeyGen API error: {error_body.get('message', e.response.text)}"
            except:
                pass
            logger.error(f"HeyGen video generation failed: {error_detail}")
            automation.status = "failed"
            automation.user_edits = automation.user_edits or {}
            automation.user_edits["heygen_error"] = error_detail
            db.commit()
            raise ValueError(error_detail)
        except Exception as e:
            error_detail = f"HeyGen video generation failed: {type(e).__name__}: {str(e)}"
            logger.error(error_detail)
            automation.status = "failed"
            automation.user_edits = automation.user_edits or {}
            automation.user_edits["heygen_error"] = error_detail
            db.commit()
            raise

    async def check_heygen_status(self, db: Session, automation_id: int) -> Dict:
        """Check HeyGen video generation status"""
        automation = (
            db.query(YouTubeAutomation).filter(YouTubeAutomation.id == automation_id).first()
        )

        if not automation or not automation.heygen_video_id:
            return {"status": "not_found"}

        if not self.heygen_key:
            return {"status": "no_api_key"}

        try:
            url = f"https://api.heygen.com/v1/video_status.get"
            headers = {"X-Api-Key": self.heygen_key}
            params = {"video_id": automation.heygen_video_id}

            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            status = data.get("data", {}).get("status")

            if status == "completed":
                automation.heygen_video_url = data.get("data", {}).get("video_url")
                automation.status = "pending_review"
                db.commit()

            return {"status": status, "video_url": automation.heygen_video_url}

        except Exception as e:
            logger.error(f"HeyGen status check failed: {e}")
            return {"status": "error", "error": str(e)}

    async def update_draft(
        self, db: Session, automation_id: int, updates: Dict
    ) -> YouTubeAutomation:
        """
        Update video draft with user edits

        Args:
            db: Database session
            automation_id: YouTubeAutomation record ID
            updates: Dict with fields to update (title, description, script, tags)

        Returns:
            Updated YouTubeAutomation record
        """
        automation = (
            db.query(YouTubeAutomation).filter(YouTubeAutomation.id == automation_id).first()
        )

        if not automation:
            raise ValueError(f"Automation {automation_id} not found")

        # Track user edits
        if not automation.user_edits:
            automation.user_edits = {}

        for field, value in updates.items():
            if field == "title":
                automation.user_edits["original_title"] = automation.video_title
                automation.video_title = value
            elif field == "description":
                automation.user_edits["original_description"] = automation.video_description
                automation.video_description = value
            elif field == "script":
                automation.user_edits["original_script"] = automation.video_script
                automation.video_script = value
            elif field == "tags":
                automation.user_edits["original_tags"] = automation.video_tags
                automation.video_tags = value
            elif field == "thumbnail_url":
                automation.thumbnail_url = value

        db.commit()
        db.refresh(automation)

        logger.info(f"Updated video draft: {automation.id}")
        return automation

    async def approve_and_upload(self, db: Session, automation_id: int) -> YouTubeAutomation:
        """
        Approve draft and upload to YouTube

        Args:
            db: Database session
            automation_id: YouTubeAutomation record ID

        Returns:
            Updated YouTubeAutomation record with YouTube URL
        """
        automation = (
            db.query(YouTubeAutomation).filter(YouTubeAutomation.id == automation_id).first()
        )

        if not automation:
            raise ValueError(f"Automation {automation_id} not found")

        if automation.status not in ["pending_review", "draft"]:
            raise ValueError(f"Cannot upload video in status: {automation.status}")

        automation.approved_at = datetime.utcnow()
        automation.status = "approved"

        if not self._has_upload_credentials():
            if self.simulate_upload:
                logger.warning("YouTube upload not configured - simulating upload")
                automation.youtube_video_id = "simulated_" + str(automation.id)
                automation.youtube_url = f"https://youtube.com/watch?v={automation.youtube_video_id}"
                automation.uploaded_at = datetime.utcnow()
                automation.status = "uploaded"
                db.commit()
                return automation

            logger.warning("YouTube OAuth credentials not configured - marking ready for upload")
            automation.status = "ready_for_upload"
            db.commit()
            return automation

        if not automation.heygen_video_url:
            raise ValueError("No generated video URL found for upload")

        metadata = self._build_video_metadata(automation)
        video_path = None
        thumbnail_path = None
        thumbnail_mime = None

        try:
            video_path, _ = await self._download_asset(
                automation.heygen_video_url, "video", ".mp4"
            )

            if automation.thumbnail_url:
                thumbnail_path, thumbnail_mime = await self._download_asset(
                    automation.thumbnail_url, "thumbnail", ".png"
                )

            video_id = await asyncio.to_thread(
                self._upload_video_and_thumbnail,
                video_path,
                metadata,
                thumbnail_path,
                thumbnail_mime,
            )

            automation.youtube_video_id = video_id
            automation.youtube_url = f"https://youtube.com/watch?v={video_id}"
            automation.uploaded_at = datetime.utcnow()
            automation.status = "uploaded"
            db.commit()
            return automation
        except Exception as e:
            error_detail = f"YouTube upload failed: {type(e).__name__}: {str(e)}"
            logger.error(error_detail)
            automation.status = "failed"
            automation.user_edits = automation.user_edits or {}
            automation.user_edits["youtube_error"] = error_detail
            db.commit()
            raise
        finally:
            for path in (video_path, thumbnail_path):
                if path and path.exists():
                    try:
                        path.unlink()
                    except Exception:
                        logger.warning("Failed to delete temp file: %s", path)

    def get_draft(self, db: Session, automation_id: int) -> Optional[YouTubeAutomation]:
        """Get a video draft by ID"""
        return db.query(YouTubeAutomation).filter(YouTubeAutomation.id == automation_id).first()

    def get_all_drafts(self, db: Session, status: Optional[str] = None, limit: int = 50) -> list:
        """Get all video drafts, optionally filtered by status"""
        query = db.query(YouTubeAutomation)

        if status:
            query = query.filter(YouTubeAutomation.status == status)

        return query.order_by(YouTubeAutomation.created_at.desc()).limit(limit).all()

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

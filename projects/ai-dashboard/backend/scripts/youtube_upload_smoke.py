#!/usr/bin/env python3
"""
YouTube Upload Smoke Test

Safely validate OAuth credentials and optionally upload a local video file.

Usage:
  python3 scripts/youtube_upload_smoke.py --dry-run
  python3 scripts/youtube_upload_smoke.py --video /path/to/video.mp4 --confirm
  python3 scripts/youtube_upload_smoke.py --video /path/to/video.mp4 --thumbnail /path/to/thumb.png --confirm
"""

from __future__ import annotations

import argparse
import mimetypes
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    load_dotenv = None

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _require_env() -> list[str]:
    missing = []
    if not os.getenv("YOUTUBE_OAUTH_CLIENT_ID"):
        missing.append("YOUTUBE_OAUTH_CLIENT_ID")
    if not os.getenv("YOUTUBE_OAUTH_CLIENT_SECRET"):
        missing.append("YOUTUBE_OAUTH_CLIENT_SECRET")
    if not os.getenv("YOUTUBE_OAUTH_REFRESH_TOKEN"):
        missing.append("YOUTUBE_OAUTH_REFRESH_TOKEN")
    return missing


def _build_metadata(title: str, description: str, tags: list[str] | None, privacy: str, category: str) -> dict:
    snippet: dict[str, object] = {
        "title": title[:100],
        "description": description,
        "categoryId": category,
    }
    if tags:
        snippet["tags"] = tags

    return {"snippet": snippet, "status": {"privacyStatus": privacy}}


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Dashboard YouTube upload smoke test.")
    parser.add_argument("--video", help="Path to a local video file (mp4 recommended).")
    parser.add_argument("--thumbnail", help="Path to a thumbnail image (optional).")
    parser.add_argument("--title", default="AI Dashboard Upload Smoke Test")
    parser.add_argument("--description", default="Smoke test upload from AI Dashboard.")
    parser.add_argument("--tags", default="ai,dashboard,smoke-test")
    parser.add_argument("--privacy", default="unlisted")
    parser.add_argument("--category", default="28")
    parser.add_argument("--dry-run", action="store_true", help="Validate credentials only.")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually perform the upload (required to proceed).",
    )
    args = parser.parse_args()

    if load_dotenv:
        load_dotenv()
    else:
        print("⚠️  python-dotenv not installed; skipping .env loading")
    missing = _require_env()
    if missing:
        print("❌ Missing OAuth credentials:")
        for key in missing:
            print(f"   - {key}")
        return 1

    if args.dry_run:
        print("✅ OAuth credentials are present.")
        return 0

    if not args.confirm:
        print("🛑 Upload not executed. Pass --confirm to perform a real upload.")
        return 1

    if not args.video:
        print("❌ --video is required when running an upload.")
        return 1

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        return 1

    thumbnail_path = None
    thumbnail_mime = None
    if args.thumbnail:
        thumbnail_path = Path(args.thumbnail)
        if not thumbnail_path.exists():
            print(f"❌ Thumbnail file not found: {thumbnail_path}")
            return 1
        thumbnail_mime, _ = mimetypes.guess_type(str(thumbnail_path))

    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    metadata = _build_metadata(
        args.title,
        args.description,
        tags or None,
        args.privacy,
        args.category,
    )

    try:
        from services.youtube_automation import YouTubeAutomationService

        service = YouTubeAutomationService()
        video_id = service._upload_video_and_thumbnail(
            video_path=video_path,
            metadata=metadata,
            thumbnail_path=thumbnail_path,
            thumbnail_mime=thumbnail_mime,
        )
    except ModuleNotFoundError as exc:
        print("❌ Backend dependencies missing. Install backend requirements first.")
        print(f"   Missing module: {exc.name}")
        return 1
    except Exception as exc:
        print(f"❌ Upload failed: {exc}")
        return 1

    print("✅ Upload complete")
    print(f"   Video ID: {video_id}")
    print(f"   URL: https://youtube.com/watch?v={video_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

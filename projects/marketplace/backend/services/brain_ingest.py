"""
Brain ingestion helpers for approved submissions.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import zipfile
from datetime import datetime, timezone
from typing import Iterable, Optional
from urllib.request import urlopen

from sqlalchemy import select

from database import async_session_maker
from models.submission import ProjectSubmission
from models.brain import BrainEntry
from models.audit import RepoSnapshot
from services.storage import extract_key_from_url, generate_presigned_get


MAX_FILES = 30
MAX_FILE_BYTES = 120_000
MAX_CONTENT_CHARS = 4000

IGNORED_SEGMENTS = (
    "/.git/",
    "/node_modules/",
    "/venv/",
    "/dist/",
    "/build/",
    "/__pycache__/",
    "/.next/",
)

SKIP_PREFIXES = (
    ".env",
    ".env.",
)

TEXT_EXTENSIONS = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".py",
    ".go",
    ".java",
    ".rb",
    ".php",
    ".rs",
    ".swift",
    ".kt",
    ".cs",
    ".md",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".sql",
    ".env.example",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _is_text_candidate(path: str) -> bool:
    lowered = path.lower()
    if any(segment in lowered for segment in IGNORED_SEGMENTS):
        return False
    basename = os.path.basename(lowered)
    if any(basename.startswith(prefix) for prefix in SKIP_PREFIXES):
        return False
    if "/tests/" in lowered or "/test/" in lowered or "/__tests__/" in lowered:
        return False
    ext = os.path.splitext(lowered)[1]
    if ext in TEXT_EXTENSIONS:
        return True
    return basename in ("readme", "readme.md")


def _infer_language(path: str) -> Optional[str]:
    ext = os.path.splitext(path.lower())[1]
    return {
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".py": "python",
        ".go": "go",
        ".java": "java",
        ".rb": "ruby",
        ".php": "php",
        ".rs": "rust",
        ".swift": "swift",
        ".kt": "kotlin",
        ".cs": "csharp",
    }.get(ext)


def _prioritize_files(paths: Iterable[str]) -> list[str]:
    priority = []
    secondary = []
    for path in paths:
        lowered = path.lower()
        if "readme" in lowered or lowered.endswith((".md", ".mdx")):
            priority.append(path)
        elif "/src/" in lowered or "/app/" in lowered or "/backend/" in lowered or "/frontend/" in lowered:
            priority.append(path)
        else:
            secondary.append(path)
    return priority + secondary


def _resolve_snapshot_url(archive_url: str) -> str:
    if archive_url.startswith(("http://", "https://")):
        key = extract_key_from_url(archive_url)
        if key != archive_url:
            return generate_presigned_get(key, expires_in=600)
        return archive_url
    return generate_presigned_get(archive_url, expires_in=600)


async def _load_snapshot_archive(snapshot: RepoSnapshot) -> Optional[str]:
    if not snapshot.archive_url:
        return None
    download_url = _resolve_snapshot_url(snapshot.archive_url)
    temp_dir = tempfile.mkdtemp(prefix="brain_ingest_")
    archive_path = os.path.join(temp_dir, "snapshot.zip")
    with urlopen(download_url, timeout=60) as response, open(archive_path, "wb") as out:
        out.write(response.read())
    return archive_path


def _extract_entries(archive_path: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    with zipfile.ZipFile(archive_path) as zf:
        candidates = []
        for info in zf.infolist():
            if info.is_dir():
                continue
            if info.file_size > MAX_FILE_BYTES:
                continue
            if not _is_text_candidate(info.filename):
                continue
            candidates.append(info.filename)

        for filename in _prioritize_files(candidates)[:MAX_FILES]:
            try:
                with zf.open(filename) as handle:
                    data = handle.read(MAX_FILE_BYTES)
                if b"\x00" in data:
                    continue
                text = data.decode("utf-8", errors="ignore").strip()
            except Exception:
                continue
            if not text:
                continue
            entries.append((filename, text[:MAX_CONTENT_CHARS]))
    return entries


async def ingest_submission(submission_id: str) -> None:
    temp_dir = None
    async with async_session_maker() as session:
        submission = await session.get(ProjectSubmission, submission_id)
        if not submission:
            return
        if submission.status != "approved" or not submission.brain_opt_in:
            return
        if submission.brain_ingest_status in ("processing", "ingested"):
            return

        submission.brain_ingest_status = "processing"
        await session.commit()

        existing = await session.scalar(
            select(BrainEntry).where(BrainEntry.source_project == submission.id)
        )
        if existing:
            submission.brain_ingest_status = "ingested"
            submission.brain_ingested_at = _now()
            await session.commit()
            return

        snapshot = await session.scalar(
            select(RepoSnapshot)
            .where(RepoSnapshot.submission_id == submission.id)
            .order_by(RepoSnapshot.created_at.desc())
        )

        if not snapshot:
            submission.brain_ingest_status = "error"
            await session.commit()
            return

        try:
            archive_path = await _load_snapshot_archive(snapshot)
            if not archive_path:
                submission.brain_ingest_status = "error"
                await session.commit()
                return
            temp_dir = os.path.dirname(archive_path)
            extracted = _extract_entries(archive_path)
        except Exception:
            submission.brain_ingest_status = "error"
            await session.commit()
            return

        if not extracted:
            submission.brain_ingest_status = "error"
            await session.commit()
            return

        created_entries = 0
        for filename, content in extracted:
            ext = os.path.splitext(filename)[1].lstrip(".")
            extra_tags = [ext] if ext else []
            entry = BrainEntry(
                contributor_id=submission.seller_id,
                title=f"{submission.title} · {os.path.basename(filename)}",
                content=content,
                context=filename,
                type="solution",
                category=submission.category,
                tags=(submission.tags or []) + extra_tags,
                language=_infer_language(filename),
                framework=submission.framework,
                status="active",
                quality_score=0.0,
                source_project=submission.id,
                source_file=filename,
            )
            session.add(entry)
            created_entries += 1

        if created_entries == 0:
            submission.brain_ingest_status = "error"
            await session.commit()
            return

        submission.brain_ingest_status = "ingested"
        submission.brain_ingested_at = _now()
        await session.commit()

    if temp_dir:
        try:
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(temp_dir)
        except OSError:
            pass


def queue_brain_ingest(submission_id: str) -> None:
    asyncio.create_task(ingest_submission(submission_id))

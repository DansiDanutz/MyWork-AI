"""
Brain ingestion helpers for approved submissions.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from database import async_session_maker
from models.submission import ProjectSubmission
from models.brain import BrainEntry


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def ingest_submission(submission_id: str) -> None:
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
            select(BrainEntry).where(BrainEntry.source_file == submission.id)
        )
        if existing:
            submission.brain_ingest_status = "ingested"
            submission.brain_ingested_at = _now()
            await session.commit()
            return

        entry = BrainEntry(
            contributor_id=submission.seller_id,
            title=submission.title,
            content=submission.description,
            context=submission.short_description,
            type="solution",
            category=submission.category,
            tags=submission.tags or [],
            language=None,
            framework=submission.framework,
            status="active",
            quality_score=0.0,
            source_project=submission.repo_url or submission.title,
            source_file=submission.id,
        )
        session.add(entry)

        submission.brain_ingest_status = "ingested"
        submission.brain_ingested_at = _now()
        await session.commit()


def queue_brain_ingest(submission_id: str) -> None:
    asyncio.create_task(ingest_submission(submission_id))

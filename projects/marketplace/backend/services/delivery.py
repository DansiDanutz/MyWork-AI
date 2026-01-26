"""
Delivery artifact helpers for audited repo snapshots.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.audit import RepoSnapshot, DeliveryArtifact
from models.order import Order
from models.submission import ProjectSubmission


async def ensure_delivery_artifact(
    db: AsyncSession,
    order: Order,
) -> DeliveryArtifact | None:
    existing = await db.scalar(
        select(DeliveryArtifact).where(DeliveryArtifact.order_id == order.id)
    )
    if existing:
        return existing

    snapshot = await db.scalar(
        select(RepoSnapshot)
        .join(ProjectSubmission, RepoSnapshot.submission_id == ProjectSubmission.id)
        .where(ProjectSubmission.product_id == order.product_id)
        .order_by(RepoSnapshot.created_at.desc())
    )
    if not snapshot or not snapshot.archive_url:
        return None

    orphan = await db.scalar(
        select(DeliveryArtifact)
        .where(DeliveryArtifact.snapshot_id == snapshot.id)
        .where(DeliveryArtifact.order_id.is_(None))
    )
    if orphan:
        orphan.order_id = order.id
        orphan.product_id = order.product_id
        orphan.submission_id = snapshot.submission_id
        return orphan

    artifact = DeliveryArtifact(
        order_id=order.id,
        submission_id=snapshot.submission_id,
        product_id=order.product_id,
        snapshot_id=snapshot.id,
        artifact_url=snapshot.archive_url,
        artifact_sha256=snapshot.archive_sha256,
        status="ready",
    )
    db.add(artifact)
    return artifact

"""
Audit, repository snapshot, and delivery artifact models.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, Text, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, generate_uuid


AUDIT_STATUSES = [
    "queued",
    "running",
    "passed",
    "failed",
]


class AuditRun(Base, TimestampMixin):
    """Represents a single audit execution for a submission."""

    __tablename__ = "audit_runs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    submission_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="queued",
        nullable=False,
        index=True,
    )

    score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    report: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    error: Mapped[Optional[str]] = mapped_column(Text)
    logs_url: Mapped[Optional[str]] = mapped_column(Text)

    gsd_run_id: Mapped[Optional[str]] = mapped_column(String(100))
    pipeline_version: Mapped[Optional[str]] = mapped_column(String(50))

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    submission: Mapped["ProjectSubmission"] = relationship(
        "ProjectSubmission",
        back_populates="audit_runs",
        foreign_keys=[submission_id],
    )

    def __repr__(self) -> str:
        return f"<AuditRun {self.id} ({self.status})>"


class RepoSnapshot(Base, TimestampMixin):
    """Immutable snapshot of the repository at audit time."""

    __tablename__ = "repo_snapshots"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    submission_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    repo_url: Mapped[str] = mapped_column(Text, nullable=False)
    repo_ref: Mapped[Optional[str]] = mapped_column(String(255))
    commit_sha: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    tag: Mapped[Optional[str]] = mapped_column(String(100))

    archive_url: Mapped[Optional[str]] = mapped_column(Text)
    archive_sha256: Mapped[Optional[str]] = mapped_column(String(64))
    sbom_url: Mapped[Optional[str]] = mapped_column(Text)

    submission: Mapped["ProjectSubmission"] = relationship(
        "ProjectSubmission",
        back_populates="repo_snapshots",
        foreign_keys=[submission_id],
    )

    def __repr__(self) -> str:
        return f"<RepoSnapshot {self.id} {self.commit_sha}>"


class DeliveryArtifact(Base, TimestampMixin):
    """Delivery artifact for an order based on an audited snapshot."""

    __tablename__ = "delivery_artifacts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    order_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("orders.id"),
        index=True,
    )

    submission_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("project_submissions.id"),
        index=True,
    )

    product_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("products.id"),
        index=True,
    )

    snapshot_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("repo_snapshots.id"),
        index=True,
    )

    artifact_url: Mapped[Optional[str]] = mapped_column(Text)
    artifact_sha256: Mapped[Optional[str]] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(
        String(20),
        default="ready",  # ready, delivered, expired, revoked
        nullable=False,
        index=True,
    )

    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    order: Mapped[Optional["Order"]] = relationship("Order")
    submission: Mapped[Optional["ProjectSubmission"]] = relationship("ProjectSubmission")
    product: Mapped[Optional["Product"]] = relationship("Product")
    snapshot: Mapped[Optional["RepoSnapshot"]] = relationship("RepoSnapshot")

    def __repr__(self) -> str:
        return f"<DeliveryArtifact {self.id} ({self.status})>"


# Import at bottom to avoid circular imports
from models.submission import ProjectSubmission
from models.order import Order
from models.product import Product

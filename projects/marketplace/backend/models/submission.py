"""
Project submission and audit models.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Text,
    Numeric,
    BigInteger,
    JSON,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, generate_uuid


SUBMISSION_STATUSES = [
    "submitted",
    "auditing",
    "approved",
    "rejected",
    "published",
]


class ProjectSubmission(Base, TimestampMixin):
    """Project submission awaiting audit and approval."""

    __tablename__ = "project_submissions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    seller_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic info
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[Optional[str]] = mapped_column(String(500))

    # Categorization
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(50))
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)

    # Pricing
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    license_type: Mapped[str] = mapped_column(
        String(20),
        default="standard",
        nullable=False,
    )

    # Technical details
    tech_stack: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    framework: Mapped[Optional[str]] = mapped_column(String(50))
    requirements: Mapped[Optional[str]] = mapped_column(Text)

    # Media
    preview_images: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    demo_url: Mapped[Optional[str]] = mapped_column(String(255))
    documentation_url: Mapped[Optional[str]] = mapped_column(String(255))

    # Package
    package_url: Mapped[Optional[str]] = mapped_column(Text)
    package_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)

    # Repository delivery (audited snapshot)
    repo_url: Mapped[Optional[str]] = mapped_column(Text)
    repo_ref: Mapped[Optional[str]] = mapped_column(String(255))
    repo_commit_sha: Mapped[Optional[str]] = mapped_column(String(64))
    repo_provider: Mapped[Optional[str]] = mapped_column(String(50))

    # Audit configuration
    audit_profile: Mapped[Optional[str]] = mapped_column(String(50))
    audit_plan_version: Mapped[Optional[str]] = mapped_column(String(50))

    # Brain ingestion
    brain_opt_in: Mapped[bool] = mapped_column(Boolean, default=True)
    brain_ingest_status: Mapped[Optional[str]] = mapped_column(String(20))
    brain_ingested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # IP consent (required for audit + brain training)
    ip_consent: Mapped[bool] = mapped_column(Boolean, default=False)

    # Audit
    status: Mapped[str] = mapped_column(
        String(20),
        default="submitted",
        nullable=False,
        index=True,
    )
    audit_report: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    audit_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    audit_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    audit_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Optional link to product if published
    product_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("products.id"),
        index=True,
    )

    # Relationships
    seller: Mapped["User"] = relationship("User", foreign_keys=[seller_id])
    product: Mapped[Optional["Product"]] = relationship("Product", foreign_keys=[product_id])
    audit_runs: Mapped[List["AuditRun"]] = relationship(
        "AuditRun",
        back_populates="submission",
        cascade="all, delete-orphan",
    )
    repo_snapshots: Mapped[List["RepoSnapshot"]] = relationship(
        "RepoSnapshot",
        back_populates="submission",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ProjectSubmission {self.title} ({self.status})>"

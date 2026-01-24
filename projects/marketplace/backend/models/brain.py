"""
BrainEntry model for collective knowledge.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, generate_uuid


class BrainEntry(Base, TimestampMixin):
    """Knowledge entry in the collective Brain."""

    __tablename__ = "brain_entries"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    # Contributor
    contributor_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        index=True
    )

    # Content
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True  # pattern, solution, lesson, tip, antipattern
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text)

    # Categorization
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    language: Mapped[Optional[str]] = mapped_column(String(50))  # python, javascript, etc.
    framework: Mapped[Optional[str]] = mapped_column(String(50))  # fastapi, nextjs, etc.

    # Vector embedding
    embedding_id: Mapped[Optional[str]] = mapped_column(String(255))  # Pinecone ID

    # Stats
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    helpful_votes: Mapped[int] = mapped_column(Integer, default=0)
    unhelpful_votes: Mapped[int] = mapped_column(Integer, default=0)

    # Quality
    quality_score: Mapped[float] = mapped_column(default=0.0)  # Calculated score
    verified: Mapped[bool] = mapped_column(default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    verified_by: Mapped[Optional[str]] = mapped_column(String(36))

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",  # active, deprecated, merged, deleted
        nullable=False,
        index=True
    )

    # Source (if from existing project)
    source_project: Mapped[Optional[str]] = mapped_column(String(255))
    source_file: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships
    contributor: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        return f"<BrainEntry {self.title}>"

    @property
    def helpfulness_ratio(self) -> float:
        """Calculate helpfulness ratio."""
        total = self.helpful_votes + self.unhelpful_votes
        if total == 0:
            return 0.0
        return self.helpful_votes / total

    def calculate_quality_score(self) -> float:
        """Calculate overall quality score."""
        # Factors:
        # - Usage count (logarithmic)
        # - Helpfulness ratio
        # - Verified bonus
        import math

        usage_score = math.log10(self.usage_count + 1) * 10
        helpfulness_score = self.helpfulness_ratio * 50
        verified_bonus = 20 if self.verified else 0

        return min(100, usage_score + helpfulness_score + verified_bonus)


# Brain entry types
BRAIN_ENTRY_TYPES = {
    "pattern": {
        "name": "Pattern",
        "description": "A proven approach that works",
        "icon": "pattern",
    },
    "solution": {
        "name": "Solution",
        "description": "Answer to a specific problem",
        "icon": "lightbulb",
    },
    "lesson": {
        "name": "Lesson",
        "description": "Something learned from experience",
        "icon": "book",
    },
    "tip": {
        "name": "Tip",
        "description": "Quick useful advice",
        "icon": "star",
    },
    "antipattern": {
        "name": "Anti-Pattern",
        "description": "Something to avoid",
        "icon": "warning",
    },
}


# Import at bottom
from models.user import User

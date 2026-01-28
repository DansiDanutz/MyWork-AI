"""
Task data models for the CLI Task Manager.

This module defines the core data structures used throughout the application,
following the patterns established by the MyWork framework.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import json


class Priority(Enum):
    """Task priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """Create Priority from string value."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.NORMAL


class Status(Enum):
    """Task completion status."""

    PENDING = "pending"
    COMPLETED = "completed"

    def __str__(self) -> str:
        return self.value


@dataclass
class Task:
    """
    A task represents a single todo item with metadata.

    This class follows the dataclass pattern for clean serialization
    and includes validation and helper methods.
    """

    id: int
    title: str
    priority: Priority = Priority.NORMAL
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate task data after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")

        if self.due_date and self.due_date < datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ):
            # Allow due dates to be today or in the future
            pass

        # Ensure title is cleaned
        self.title = self.title.strip()

    @property
    def status(self) -> Status:
        """Get the current status of the task."""
        return Status.COMPLETED if self.completed else Status.PENDING

    @property
    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        if not self.due_date or self.completed:
            return False
        return self.due_date < datetime.now()

    @property
    def days_until_due(self) -> Optional[int]:
        """Calculate days until due date. Negative if overdue."""
        if not self.due_date:
            return None
        delta = (self.due_date.date() - datetime.now().date()).days
        return delta

    def complete(self) -> None:
        """Mark the task as completed."""
        if not self.completed:
            self.completed = True
            self.completed_at = datetime.now()

    def uncomplete(self) -> None:
        """Mark the task as not completed."""
        if self.completed:
            self.completed = False
            self.completed_at = None

    def update_title(self, new_title: str) -> None:
        """Update the task title with validation."""
        if not new_title or not new_title.strip():
            raise ValueError("Task title cannot be empty")
        self.title = new_title.strip()

    def update_priority(self, new_priority: Priority) -> None:
        """Update the task priority."""
        self.priority = new_priority

    def update_due_date(self, new_due_date: Optional[datetime]) -> None:
        """Update the task due date."""
        self.due_date = new_due_date

    def matches_query(self, query: str, case_sensitive: bool = False) -> bool:
        """Check if task title matches the search query."""
        search_title = self.title if case_sensitive else self.title.lower()
        search_query = query if case_sensitive else query.lower()
        return search_query in search_title

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        data = asdict(self)

        # Convert enums to strings
        data["priority"] = self.priority.value

        # Convert datetime objects to ISO strings
        for field_name in ["created_at", "due_date", "completed_at"]:
            if data[field_name]:
                data[field_name] = data[field_name].isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create task from dictionary (deserialization)."""
        # Convert string priority back to enum
        if "priority" in data:
            data["priority"] = Priority.from_string(data["priority"])

        # Convert ISO strings back to datetime objects
        for field_name in ["created_at", "due_date", "completed_at"]:
            if data.get(field_name):
                data[field_name] = datetime.fromisoformat(data[field_name])

        return cls(**data)

    def __str__(self) -> str:
        """Human-readable string representation."""
        status_icon = "✅" if self.completed else "⏳"
        priority_indicator = {Priority.HIGH: "🔴", Priority.NORMAL: "🔵", Priority.LOW: "🟡"}[
            self.priority
        ]

        result = f"{status_icon} {priority_indicator} {self.title}"

        if self.due_date:
            if self.is_overdue:
                result += f" (⚠️ OVERDUE: {self.due_date.strftime('%Y-%m-%d')})"
            elif self.days_until_due == 0:
                result += f" (📅 DUE TODAY)"
            elif self.days_until_due and self.days_until_due <= 3:
                result += f" (📅 Due in {self.days_until_due} days)"
            else:
                result += f" (📅 Due: {self.due_date.strftime('%Y-%m-%d')})"

        return result

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return (
            f"Task(id={self.id}, title='{self.title}', "
            f"priority={self.priority.value}, completed={self.completed}, "
            f"due_date={self.due_date})"
        )


@dataclass
class TaskStats:
    """Statistics about a collection of tasks."""

    total: int = 0
    completed: int = 0
    pending: int = 0
    overdue: int = 0
    high_priority: int = 0
    normal_priority: int = 0
    low_priority: int = 0

    @property
    def completion_rate(self) -> float:
        """Calculate completion percentage."""
        if self.total == 0:
            return 0.0
        return (self.completed / self.total) * 100

    @property
    def overdue_rate(self) -> float:
        """Calculate overdue percentage."""
        if self.pending == 0:
            return 0.0
        return (self.overdue / self.pending) * 100

    @classmethod
    def from_tasks(cls, tasks: list[Task]) -> "TaskStats":
        """Calculate statistics from a list of tasks."""
        stats = cls()
        stats.total = len(tasks)

        for task in tasks:
            if task.completed:
                stats.completed += 1
            else:
                stats.pending += 1
                if task.is_overdue:
                    stats.overdue += 1

            # Count by priority
            if task.priority == Priority.HIGH:
                stats.high_priority += 1
            elif task.priority == Priority.NORMAL:
                stats.normal_priority += 1
            else:  # LOW
                stats.low_priority += 1

        return stats

    def __str__(self) -> str:
        """Human-readable statistics summary."""
        return (
            f"📊 {self.total} total | "
            f"✅ {self.completed} completed ({self.completion_rate:.1f}%) | "
            f"⏳ {self.pending} pending"
            + (f" | ⚠️ {self.overdue} overdue" if self.overdue > 0 else "")
        )


def validate_task_data(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate task data and return any validation errors.

    Returns:
        Dict mapping field names to error messages (empty if valid)
    """
    errors = {}

    # Required fields
    if not data.get("title", "").strip():
        errors["title"] = "Title is required and cannot be empty"

    if "id" not in data or not isinstance(data["id"], int) or data["id"] <= 0:
        errors["id"] = "ID must be a positive integer"

    # Priority validation
    if "priority" in data:
        try:
            Priority.from_string(data["priority"])
        except (ValueError, AttributeError):
            errors["priority"] = "Priority must be 'low', 'normal', or 'high'"

    # Due date validation
    if "due_date" in data and data["due_date"] is not None:
        if not isinstance(data["due_date"], datetime):
            try:
                # Try to parse if it's a string
                datetime.fromisoformat(str(data["due_date"]))
            except (ValueError, TypeError):
                errors["due_date"] = "Due date must be a valid datetime"

    return errors

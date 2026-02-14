"""
Tests for brain.py
==================
Tests for the Brain/Knowledge Vault functionality.
"""

import json
from datetime import datetime

import pytest


class TestBrainManager:
    """Tests for BrainManager class."""

    def test_load_empty_brain(self, temp_mywork_root):
        """Should handle empty/missing brain file gracefully."""
        import importlib
        import sys

        # Remove cached module to force reload with new env
        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()

        assert len(manager.entries) == 0

    def test_load_existing_brain(self, temp_mywork_root, sample_brain_data):
        """Should load existing brain data correctly."""
        import importlib
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()

        assert len(manager.entries) == 2
        assert "test-001" in manager.entries
        assert "test-002" in manager.entries

    def test_add_entry(self, temp_mywork_root):
        """Should add new entries correctly."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        entry = manager.add(
            entry_type="pattern",
            content="New test pattern",
            context="Unit testing",
            status="EXPERIMENTAL",
            tags=["test"],
        )

        assert entry.id in manager.entries
        assert entry.content == "New test pattern"
        assert entry.type == "pattern"
        assert entry.status == "EXPERIMENTAL"

    def test_search_entries(self, temp_mywork_root, sample_brain_data):
        """Should search entries by query."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        results = manager.search("test")

        # Both entries have "test" in them
        assert len(results) >= 1

    def test_search_no_results(self, temp_mywork_root, sample_brain_data):
        """Should return empty list when no matches."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        results = manager.search("nonexistent_xyz_123")

        assert len(results) == 0

    def test_get_by_type(self, temp_mywork_root, sample_brain_data):
        """Should filter entries by type."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        patterns = manager.get_by_type("pattern")

        assert len(patterns) == 1
        assert patterns[0].type == "pattern"

    def test_update_entry(self, temp_mywork_root, sample_brain_data):
        """Should update existing entries."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        manager.update("test-001", status="DEPRECATED")

        assert manager.entries["test-001"].status == "DEPRECATED"

    def test_get_stats(self, temp_mywork_root, sample_brain_data):
        """Should return correct statistics."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        stats = manager.get_stats()

        assert stats["total_entries"] == 2
        assert "pattern" in stats["by_type"]
        assert "lesson" in stats["by_type"]


class TestBrainDeprecateAndCleanup:
    """Tests for deprecate, delete, and cleanup operations."""

    def test_deprecate_entry(self, temp_mywork_root, sample_brain_data):
        """Should mark an entry as deprecated."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        result = manager.deprecate("test-001")

        assert result is not None
        assert manager.entries["test-001"].status == "DEPRECATED"

    def test_deprecate_nonexistent(self, temp_mywork_root):
        """Should return None for nonexistent entry."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        result = manager.deprecate("nonexistent-999")

        assert result is None

    def test_delete_entry(self, temp_mywork_root, sample_brain_data):
        """Should permanently delete an entry."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        result = manager.delete("test-001")

        assert result is True
        assert "test-001" not in manager.entries
        assert len(manager.entries) == 1

    def test_delete_nonexistent(self, temp_mywork_root):
        """Should return False for nonexistent entry."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        result = manager.delete("nonexistent-999")

        assert result is False

    def test_cleanup_removes_deprecated(self, temp_mywork_root, sample_brain_data):
        """Should remove all deprecated entries."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        manager.deprecate("test-001")
        removed = manager.cleanup()

        assert removed == 1
        assert "test-001" not in manager.entries
        assert len(manager.entries) == 1

    def test_cleanup_nothing_to_remove(self, temp_mywork_root, sample_brain_data):
        """Should return 0 when no deprecated entries."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        removed = manager.cleanup()

        assert removed == 0

    def test_get_deprecated(self, temp_mywork_root, sample_brain_data):
        """Should return only deprecated entries."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        manager.deprecate("test-001")
        deprecated = manager.get_deprecated()

        assert len(deprecated) == 1
        assert deprecated[0].id == "test-001"

    def test_get_experimental(self, temp_mywork_root):
        """Should return only experimental entries."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        manager.add("tip", "Experimental tip", status="EXPERIMENTAL")
        manager.add("lesson", "Tested lesson", status="TESTED")
        experimental = manager.get_experimental()

        assert len(experimental) == 1
        assert experimental[0].status == "EXPERIMENTAL"

    def test_add_invalid_type(self, temp_mywork_root):
        """Should raise ValueError for invalid entry type."""
        import sys

        if "brain" in sys.modules:
            del sys.modules["brain"]

        from brain import BrainManager

        manager = BrainManager()
        with pytest.raises(ValueError, match="Unknown type"):
            manager.add("invalid_type", "content")


class TestBrainEntry:
    """Tests for BrainEntry dataclass."""

    def test_create_entry(self):
        """Should create entry with all fields."""
        from brain import BrainEntry

        entry = BrainEntry(
            id="test-123",
            type="pattern",
            content="Test content",
            context="Test context",
            status="TESTED",
            tags=["test"],
            date_added="2024-01-01",
            references=5,
        )

        assert entry.id == "test-123"
        assert entry.type == "pattern"
        assert entry.references == 5

    def test_to_dict(self):
        """Should convert to dictionary correctly."""
        from brain import BrainEntry

        entry = BrainEntry(
            id="test-123",
            type="pattern",
            content="Test content",
            context="Test context",
            status="TESTED",
            tags=["test"],
            date_added="2024-01-01",
            references=0,
        )

        result = entry.to_dict()

        assert isinstance(result, dict)
        assert result["id"] == "test-123"
        assert result["type"] == "pattern"

"""
Tests for brain.py
==================
Unit tests for the BrainManager and BrainEntry classes.
"""

import json
from datetime import datetime
from pathlib import Path

import pytest


class TestBrainEntry:
    """Tests for BrainEntry dataclass."""

    def test_create_entry_minimal(self):
        """Should create entry with minimal fields."""
        from brain import BrainEntry

        entry = BrainEntry(id="test-001", type="pattern", content="Test pattern")

        assert entry.id == "test-001"
        assert entry.type == "pattern"
        assert entry.content == "Test pattern"
        assert entry.context == ""
        assert entry.status == "TESTED"
        assert entry.tags == []
        assert entry.references == 0

    def test_create_entry_full(self):
        """Should create entry with all fields."""
        from brain import BrainEntry

        entry = BrainEntry(
            id="test-002",
            type="lesson",
            content="Test lesson",
            context="Testing context",
            status="EXPERIMENTAL",
            tags=["test", "lesson"],
            references=5,
            date_added="2025-01-01",
            date_updated="2025-01-02",
        )

        assert entry.id == "test-002"
        assert entry.type == "lesson"
        assert entry.content == "Test lesson"
        assert entry.context == "Testing context"
        assert entry.status == "EXPERIMENTAL"
        assert entry.tags == ["test", "lesson"]
        assert entry.references == 5
        assert entry.date_added == "2025-01-01"
        assert entry.date_updated == "2025-01-02"

    def test_post_init_dates(self):
        """Should auto-generate dates when not provided."""
        from brain import BrainEntry

        entry = BrainEntry(id="test-003", type="tip", content="Test tip")

        today = datetime.now().strftime("%Y-%m-%d")
        assert entry.date_added == today
        assert entry.date_updated == today

    def test_post_init_date_updated_uses_added(self):
        """Should use date_added for date_updated when not provided."""
        from brain import BrainEntry

        entry = BrainEntry(
            id="test-004",
            type="insight",
            content="Test insight",
            date_added="2025-01-15",
        )

        assert entry.date_added == "2025-01-15"
        assert entry.date_updated == "2025-01-15"

    def test_to_dict(self):
        """Should convert entry to dictionary."""
        from brain import BrainEntry

        entry = BrainEntry(
            id="test-005",
            type="antipattern",
            content="Don't do this",
            tags=["bad"],
        )

        result = entry.to_dict()

        assert isinstance(result, dict)
        assert result["id"] == "test-005"
        assert result["type"] == "antipattern"
        assert result["content"] == "Don't do this"
        assert result["tags"] == ["bad"]

    def test_from_dict(self):
        """Should create entry from dictionary."""
        from brain import BrainEntry

        data = {
            "id": "test-006",
            "type": "experiment",
            "content": "Try this",
            "context": "Testing",
            "status": "TESTED",
            "tags": ["test"],
            "references": 3,
            "date_added": "2025-01-01",
            "date_updated": "2025-01-02",
        }

        entry = BrainEntry.from_dict(data)

        assert entry.id == "test-006"
        assert entry.type == "experiment"
        assert entry.content == "Try this"
        assert entry.context == "Testing"
        assert entry.status == "TESTED"
        assert entry.tags == ["test"]
        assert entry.references == 3
        assert entry.date_added == "2025-01-01"
        assert entry.date_updated == "2025-01-02"

    def test_from_dict_filters_unknown_fields(self):
        """Should ignore unknown fields when creating from dict."""
        from brain import BrainEntry

        data = {
            "id": "test-007",
            "type": "pattern",
            "content": "Test",
            "unknown_field": "should be ignored",
            "another_unknown": 123,
        }

        entry = BrainEntry.from_dict(data)

        assert entry.id == "test-007"
        assert not hasattr(entry, "unknown_field")
        assert not hasattr(entry, "another_unknown")


class TestBrainManager:
    """Tests for BrainManager class."""

    def test_init_with_temp_root(self, temp_mywork_root):
        """Should initialize with custom root."""
        import importlib
        import brain

        importlib.reload(brain)

        manager = brain.BrainManager(root=temp_mywork_root)

        assert manager.root == temp_mywork_root
        assert manager.brain_file == temp_mywork_root / ".planning" / "BRAIN.md"
        assert manager.brain_json == temp_mywork_root / ".planning" / "brain_data.json"

    def test_load_from_json(self, temp_mywork_root):
        """Should load entries from JSON file."""
        import importlib
        import brain

        importlib.reload(brain)

        # Create sample brain data
        brain_data = {
            "version": "1.0",
            "entries": [
                {
                    "id": "test-001",
                    "type": "pattern",
                    "content": "Test pattern",
                    "status": "TESTED",
                    "tags": [],
                    "references": 0,
                    "date_added": "2025-01-01",
                    "date_updated": "2025-01-01",
                }
            ],
        }

        brain_file = temp_mywork_root / ".planning" / "brain_data.json"
        brain_file.write_text(json.dumps(brain_data, indent=2))

        manager = brain.BrainManager(root=temp_mywork_root)

        assert len(manager.entries) == 1
        assert "test-001" in manager.entries
        assert manager.entries["test-001"].content == "Test pattern"

    def test_save_to_json(self, temp_mywork_root):
        """Should save entries to JSON file."""
        import importlib
        import brain

        importlib.reload(brain)

        manager = brain.BrainManager(root=temp_mywork_root)
        entry = brain.BrainEntry(id="test-001", type="tip", content="Save test")
        manager.entries["test-001"] = entry

        manager.save()

        brain_file = temp_mywork_root / ".planning" / "brain_data.json"
        assert brain_file.exists()

        with open(brain_file) as f:
            data = json.load(f)
            assert data["entry_count"] == 1
            assert len(data["entries"]) == 1
            assert data["entries"][0]["id"] == "test-001"

    def test_generate_id(self, temp_mywork_root):
        """Should generate unique IDs for entries."""
        import importlib
        import brain

        importlib.reload(brain)

        manager = brain.BrainManager(root=temp_mywork_root)

        # First entry
        id1 = manager.generate_id("pattern")
        assert id1 == "pattern-001"

        # Add entry and test second ID
        entry = brain.BrainEntry(id=id1, type="pattern", content="Test")
        manager.entries[id1] = entry

        id2 = manager.generate_id("pattern")
        assert id2 == "pattern-002"

    def test_add_entry(self, temp_mywork_root):
        """Should add new entry to brain."""
        import importlib
        import brain

        importlib.reload(brain)

        manager = brain.BrainManager(root=temp_mywork_root)
        entry = manager.add(
            "pattern",
            "Always validate inputs",
            context="API development",
            tags=["api", "validation"],
        )

        assert entry.id == "pattern-001"
        assert entry.type == "pattern"
        assert entry.content == "Always validate inputs"
        assert entry.context == "API development"
        assert entry.tags == ["api", "validation"]
        assert entry.status == "TESTED"
        assert "pattern-001" in manager.entries

    def test_add_invalid_type(self, temp_mywork_root):
        """Should raise error for invalid entry type."""
        import importlib
        import brain

        importlib.reload(brain)

        manager = brain.BrainManager(root=temp_mywork_root)

        with pytest.raises(ValueError, match="Unknown type"):
            manager.add("invalid_type", "Test content")

    def test_update_entry(self, temp_mywork_root):
        """Should update existing entry."""
        import importlib
        import brain

        importlib.reload(brain)

        manager = brain.BrainManager(root=temp_mywork_root)
        entry = manager.add("lesson", "Original content")

        updated = manager.update(
            entry.id,
            content="Updated content",
            context="New context",
            tags=["updated"],
        )

        assert updated is not None
        assert updated.content == "Updated content"
        assert updated.context == "New context"
        assert updated.tags == ["updated"]

    def test_update_nonexistent_entry(self, temp_mywork_root):
        """Should return None for nonexistent entry."""
        import importlib
        import brain

        importlib.reload(brain)

        manager = brain.BrainManager(root=temp_mywork_root)

        result = manager.update("nonexistent-001", content="Test")

        assert result is None

    def test_deprecate_entry(self, temp_mywork_root):
        """Should deprecate an entry."""
        import importlib
        import brain

        importlib.reload(brain)

        manager = brain.BrainManager(root=temp_mywork_root)
        entry = manager.add("pattern", "Test pattern")

        deprecated = manager.deprecate(entry.id)

        assert deprecated is not None
        assert deprecated.status == "DEPRECATED"

    def test_search_entries(self, temp_mywork_root):
        """Should search entries by query."""
        import importlib
        import brain

        importlib.reload(brain)

        manager = brain.BrainManager(root=temp_mywork_root)
        manager.add("pattern", "Always validate API inputs")
        manager.add("lesson", "Use TypeScript for APIs")
        manager.add("tip", "Run tests before deployment")

        results = manager.search("API")

        assert len(results) == 2

    def test_get_stats(self, temp_mywork_root):
        """Should return brain statistics."""
        import importlib
        import brain

        importlib.reload(brain)

        manager = brain.BrainManager(root=temp_mywork_root)
        manager.add("pattern", "Test pattern")
        manager.add("lesson", "Test lesson")
        manager.add("tip", "Test tip")

        stats = manager.get_stats()

        assert "total_entries" in stats
        assert stats["total_entries"] == 3
        assert "by_type" in stats
        assert stats["by_type"]["pattern"] == 1
        assert stats["by_type"]["lesson"] == 1
        assert stats["by_type"]["tip"] == 1

    def test_get_experimental(self, temp_mywork_root):
        """Should filter entries by experimental status."""
        import importlib
        import brain

        importlib.reload(brain)

        manager = brain.BrainManager(root=temp_mywork_root)
        manager.add("pattern", "Test 1", status="TESTED")
        manager.add("lesson", "Test 2", status="EXPERIMENTAL")
        manager.add("tip", "Test 3", status="TESTED")

        experimental = manager.get_experimental()

        assert len(experimental) == 1
        assert all(e.status == "EXPERIMENTAL" for e in experimental)

    def test_get_deprecated(self, temp_mywork_root):
        """Should filter entries by deprecated status."""
        import importlib
        import brain

        importlib.reload(brain)

        manager = brain.BrainManager(root=temp_mywork_root)
        entry1 = manager.add("pattern", "Test 1")
        entry2 = manager.add("lesson", "Test 2")

        # Deprecate one entry
        manager.deprecate(entry1.id)

        deprecated = manager.get_deprecated()

        assert len(deprecated) == 1
        assert deprecated[0].id == entry1.id
        assert all(e.status == "DEPRECATED" for e in deprecated)


class TestEntryTypes:
    """Tests for ENTRY_TYPES constant."""

    def test_entry_types_defined(self):
        """Should have all expected entry types defined."""
        from brain import ENTRY_TYPES

        expected_types = ["lesson", "pattern", "antipattern", "tip", "insight", "experiment"]

        for entry_type in expected_types:
            assert entry_type in ENTRY_TYPES
            assert ENTRY_TYPES[entry_type]  # Should have a non-empty section name

    def test_entry_type_section_names(self):
        """Should have meaningful section names for each type."""
        from brain import ENTRY_TYPES

        assert "Patterns" in ENTRY_TYPES["pattern"]
        assert "Lessons" in ENTRY_TYPES["lesson"]
        assert "Anti-Patterns" in ENTRY_TYPES["antipattern"]
        assert "Tool" in ENTRY_TYPES["tip"]
        assert "Insight" in ENTRY_TYPES["insight"]
        assert "Experiment" in ENTRY_TYPES["experiment"]


class TestResolveBrainPaths:
    """Tests for _resolve_brain_paths function."""

    def test_resolve_paths_with_custom_root(self, temp_mywork_root):
        """Should resolve paths with custom root."""
        import importlib
        import brain

        importlib.reload(brain)

        root, brain_file, brain_json = brain._resolve_brain_paths(temp_mywork_root)

        assert root == temp_mywork_root
        assert brain_file == temp_mywork_root / ".planning" / "BRAIN.md"
        assert brain_json == temp_mywork_root / ".planning" / "brain_data.json"

    def test_resolve_paths_without_root(self):
        """Should resolve paths using default detection."""
        import importlib
        import brain

        importlib.reload(brain)

        root, brain_file, brain_json = brain._resolve_brain_paths()

        assert isinstance(root, Path)
        assert isinstance(brain_file, Path)
        assert isinstance(brain_json, Path)
        assert "BRAIN.md" in str(brain_file)
        assert "brain_data.json" in str(brain_json)

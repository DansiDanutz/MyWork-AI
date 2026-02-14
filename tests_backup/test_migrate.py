"""Tests for mw migrate command."""
import os
import sys
import sqlite3
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.migrate import (
    cmd_migrate,
    cmd_migrate_init,
    cmd_migrate_create,
    cmd_migrate_up,
    cmd_migrate_down,
    cmd_migrate_status,
    cmd_migrate_history,
    cmd_migrate_reset,
    _connect_sqlite,
    _ensure_migration_table,
    _get_applied_migrations,
    _get_pending_migrations,
    _file_checksum,
    MIGRATION_TABLE,
)


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory."""
    # Create a git repo marker
    (tmp_path / ".git").mkdir()
    # Create migrations dir
    (tmp_path / "migrations").mkdir()
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_dir)


@pytest.fixture
def db_conn(temp_project):
    """Create a SQLite connection."""
    db_path = str(temp_project / "db.sqlite3")
    conn = _connect_sqlite(f"sqlite:///{db_path}")
    yield conn
    conn.close()


class TestMigrateInit:
    def test_init_creates_directory(self, tmp_path):
        os.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        result = cmd_migrate_init([])
        assert result == 0
        assert (tmp_path / "migrations").exists()
        assert (tmp_path / "migrations" / "README.md").exists()

    def test_init_already_exists(self, temp_project):
        result = cmd_migrate_init([])
        assert result == 0  # Should not fail


class TestMigrateCreate:
    def test_create_migration(self, temp_project):
        result = cmd_migrate_create(["add_users"])
        assert result == 0
        
        migrations = list((temp_project / "migrations").glob("*.sql"))
        assert len(migrations) == 2  # up + down
        
        up_files = [f for f in migrations if not f.name.endswith(".down.sql")]
        down_files = [f for f in migrations if f.name.endswith(".down.sql")]
        assert len(up_files) == 1
        assert len(down_files) == 1
        assert "add_users" in up_files[0].name

    def test_create_no_name(self, temp_project):
        result = cmd_migrate_create([])
        assert result == 1

    def test_create_multi_word_name(self, temp_project):
        result = cmd_migrate_create(["add", "user", "roles"])
        assert result == 0
        up_files = [f for f in (temp_project / "migrations").glob("*.sql") if not f.name.endswith(".down.sql")]
        assert any("add_user_roles" in f.name for f in up_files)


class TestMigrateUp:
    def test_up_no_pending(self, temp_project):
        result = cmd_migrate_up([])
        assert result == 0

    def test_up_applies_migration(self, temp_project):
        # Create a migration
        mig_dir = temp_project / "migrations"
        up_file = mig_dir / "20260101000000_create_items.sql"
        up_file.write_text("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT);")
        down_file = mig_dir / "20260101000000_create_items.down.sql"
        down_file.write_text("DROP TABLE IF EXISTS items;")
        
        result = cmd_migrate_up([])
        assert result == 0
        
        # Verify table was created
        conn = _connect_sqlite(f"sqlite:///{temp_project / 'db.sqlite3'}")
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
        assert cursor.fetchone() is not None
        
        # Verify migration recorded
        applied = _get_applied_migrations(conn)
        assert len(applied) == 1
        assert applied[0]["version"] == "20260101000000"
        conn.close()

    def test_up_multiple_migrations(self, temp_project):
        mig_dir = temp_project / "migrations"
        
        (mig_dir / "20260101000000_first.sql").write_text("CREATE TABLE t1 (id INTEGER);")
        (mig_dir / "20260101000000_first.down.sql").write_text("DROP TABLE t1;")
        (mig_dir / "20260102000000_second.sql").write_text("CREATE TABLE t2 (id INTEGER);")
        (mig_dir / "20260102000000_second.down.sql").write_text("DROP TABLE t2;")
        
        result = cmd_migrate_up([])
        assert result == 0
        
        conn = _connect_sqlite(f"sqlite:///{temp_project / 'db.sqlite3'}")
        applied = _get_applied_migrations(conn)
        assert len(applied) == 2
        conn.close()

    def test_up_with_limit(self, temp_project):
        mig_dir = temp_project / "migrations"
        (mig_dir / "20260101000000_first.sql").write_text("CREATE TABLE t1 (id INTEGER);")
        (mig_dir / "20260102000000_second.sql").write_text("CREATE TABLE t2 (id INTEGER);")
        
        result = cmd_migrate_up(["1"])
        assert result == 0
        
        conn = _connect_sqlite(f"sqlite:///{temp_project / 'db.sqlite3'}")
        applied = _get_applied_migrations(conn)
        assert len(applied) == 1
        conn.close()

    def test_up_bad_sql_fails(self, temp_project):
        mig_dir = temp_project / "migrations"
        (mig_dir / "20260101000000_bad.sql").write_text("INVALID SQL SYNTAX HERE;")
        
        result = cmd_migrate_up([])
        assert result == 1


class TestMigrateDown:
    def test_down_no_migrations(self, temp_project):
        result = cmd_migrate_down([])
        assert result == 0

    def test_down_rollback_one(self, temp_project):
        mig_dir = temp_project / "migrations"
        (mig_dir / "20260101000000_create.sql").write_text("CREATE TABLE t1 (id INTEGER);")
        (mig_dir / "20260101000000_create.down.sql").write_text("DROP TABLE IF EXISTS t1;")
        
        cmd_migrate_up([])
        result = cmd_migrate_down([])
        assert result == 0
        
        conn = _connect_sqlite(f"sqlite:///{temp_project / 'db.sqlite3'}")
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='t1'")
        assert cursor.fetchone() is None
        applied = _get_applied_migrations(conn)
        assert len(applied) == 0
        conn.close()


class TestMigrateStatus:
    def test_status_empty(self, temp_project):
        result = cmd_migrate_status([])
        assert result == 0

    def test_status_with_migrations(self, temp_project):
        mig_dir = temp_project / "migrations"
        (mig_dir / "20260101000000_first.sql").write_text("CREATE TABLE t1 (id INTEGER);")
        cmd_migrate_up([])
        result = cmd_migrate_status([])
        assert result == 0


class TestMigrateHistory:
    def test_history_empty(self, temp_project):
        result = cmd_migrate_history([])
        assert result == 0

    def test_history_with_data(self, temp_project):
        mig_dir = temp_project / "migrations"
        (mig_dir / "20260101000000_first.sql").write_text("CREATE TABLE t1 (id INTEGER);")
        cmd_migrate_up([])
        result = cmd_migrate_history([])
        assert result == 0


class TestMigrateDispatcher:
    def test_default_shows_status(self, temp_project):
        result = cmd_migrate([])
        assert result == 0

    def test_unknown_command(self, temp_project):
        result = cmd_migrate(["foobar"])
        assert result == 1

    def test_help(self, temp_project):
        result = cmd_migrate(["help"])
        assert result == 0


class TestHelpers:
    def test_file_checksum(self, tmp_path):
        f = tmp_path / "test.sql"
        f.write_text("SELECT 1;")
        cs = _file_checksum(f)
        assert len(cs) == 16
        assert cs == _file_checksum(f)  # deterministic

    def test_connect_sqlite_variants(self, tmp_path):
        path = str(tmp_path / "test.db")
        conn1 = _connect_sqlite(f"sqlite:///{path}")
        conn1.close()
        assert Path(path).exists()

    def test_ensure_migration_table(self, tmp_path):
        conn = sqlite3.connect(str(tmp_path / "test.db"))
        _ensure_migration_table(conn)
        cursor = conn.execute(f"SELECT name FROM sqlite_master WHERE name='{MIGRATION_TABLE}'")
        assert cursor.fetchone() is not None
        conn.close()

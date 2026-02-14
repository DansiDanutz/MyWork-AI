"""Tests for mw db - Database Manager."""
import json
import os
import sqlite3
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.db_manager import (
    cmd_db, detect_db_config, parse_db_url, SQLiteDB,
    create_migration, get_migrations, run_migrations, rollback_migration,
    seed_database
)


@pytest.fixture
def tmp_project(tmp_path, monkeypatch):
    """Create a temp project directory and cd into it."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def sqlite_db(tmp_project):
    """Create a test SQLite database with sample data."""
    db_path = tmp_project / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@test.com')")
    conn.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@test.com')")
    conn.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT, user_id INTEGER)")
    conn.execute("INSERT INTO posts VALUES (1, 'Hello World', 1)")
    conn.commit()
    conn.close()
    
    # Write config
    mw_dir = tmp_project / ".mywork"
    mw_dir.mkdir()
    (mw_dir / "db.json").write_text(json.dumps({"type": "sqlite", "path": str(db_path), "source": "test"}))
    return db_path


# ─── Detection Tests ─────────────────────────────────────────────
class TestDetection:
    def test_detect_from_env(self, tmp_project):
        (tmp_project / ".env").write_text('DATABASE_URL=sqlite:///myapp.db\n')
        config = detect_db_config(str(tmp_project))
        assert config is not None
        assert config["type"] == "sqlite"

    def test_detect_from_mywork_config(self, tmp_project):
        mw = tmp_project / ".mywork"
        mw.mkdir()
        (mw / "db.json").write_text('{"type": "postgres", "url": "postgresql://localhost/db"}')
        config = detect_db_config(str(tmp_project))
        assert config["type"] == "postgres"

    def test_detect_sqlite_file(self, tmp_project):
        (tmp_project / "db.sqlite3").touch()
        config = detect_db_config(str(tmp_project))
        assert config is not None
        assert config["type"] == "sqlite"

    def test_detect_nothing(self, tmp_project):
        config = detect_db_config(str(tmp_project))
        assert config is None

    def test_parse_postgres_url(self):
        r = parse_db_url("postgresql://user:pass@host:5432/db")
        assert r["type"] == "postgres"

    def test_parse_mysql_url(self):
        r = parse_db_url("mysql://USER:PASSWORD@host:3306/db")
        assert r["type"] == "mysql"

    def test_parse_sqlite_url(self):
        r = parse_db_url("sqlite:///app.db")
        assert r["type"] == "sqlite"


# ─── SQLiteDB Tests ──────────────────────────────────────────────
class TestSQLiteDB:
    def test_connect(self, sqlite_db):
        db = SQLiteDB(str(sqlite_db))
        assert db.connect() is True
        db.close()

    def test_tables(self, sqlite_db):
        db = SQLiteDB(str(sqlite_db))
        db.connect()
        tables = db.tables()
        names = [t["name"] for t in tables]
        assert "users" in names
        assert "posts" in names
        user_table = next(t for t in tables if t["name"] == "users")
        assert user_table["rows"] == 2
        db.close()

    def test_schema(self, sqlite_db):
        db = SQLiteDB(str(sqlite_db))
        db.connect()
        cols = db.schema("users")
        col_names = [c["name"] for c in cols]
        assert "id" in col_names
        assert "name" in col_names
        assert "email" in col_names
        db.close()

    def test_query_select(self, sqlite_db):
        db = SQLiteDB(str(sqlite_db))
        db.connect()
        cols, rows = db.query("SELECT * FROM users WHERE id = 1")
        assert len(rows) == 1
        assert rows[0][1] == "Alice"
        db.close()

    def test_query_insert(self, sqlite_db):
        db = SQLiteDB(str(sqlite_db))
        db.connect()
        db.query("INSERT INTO users VALUES (3, 'Charlie', 'charlie@test.com')")
        _, rows = db.query("SELECT COUNT(*) FROM users")
        assert rows[0][0] == 3
        db.close()

    def test_export_csv(self, sqlite_db, tmp_project):
        db = SQLiteDB(str(sqlite_db))
        db.connect()
        path = db.export_table("users", "csv")
        assert Path(path).exists()
        content = Path(path).read_text()
        assert "Alice" in content
        db.close()

    def test_export_json(self, sqlite_db, tmp_project):
        db = SQLiteDB(str(sqlite_db))
        db.connect()
        path = db.export_table("users", "json")
        assert Path(path).exists()
        data = json.loads(Path(path).read_text())
        assert len(data) == 2
        assert data[0]["name"] == "Alice"
        db.close()


# ─── Migration Tests ─────────────────────────────────────────────
class TestMigrations:
    def test_create_migration(self, tmp_project):
        path = create_migration("add users table", str(tmp_project))
        assert Path(path).exists()
        content = Path(path).read_text()
        assert "add users table" in content
        assert "-- UP" in content
        assert "-- DOWN" in content

    def test_get_migrations(self, tmp_project):
        create_migration("first", str(tmp_project))
        create_migration("second", str(tmp_project))
        migs = get_migrations(str(tmp_project))
        assert len(migs) == 2
        assert migs[0] < migs[1]  # Sorted by timestamp

    def test_run_migrations(self, tmp_project):
        # Create migration with actual SQL
        mig_dir = tmp_project / ".mywork" / "migrations"
        mig_dir.mkdir(parents=True)
        (mig_dir / "20260101000000_create_items.sql").write_text(
            "-- Migration\n-- UP\nCREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT);\n-- DOWN\nDROP TABLE items;"
        )
        
        db_path = tmp_project / "test.db"
        db = SQLiteDB(str(db_path))
        db_path.touch()
        db.connect()
        count = run_migrations(db, str(tmp_project))
        assert count == 1
        
        # Verify table exists
        tables = db.tables()
        assert any(t["name"] == "items" for t in tables)
        db.close()

    def test_run_migrations_idempotent(self, tmp_project):
        mig_dir = tmp_project / ".mywork" / "migrations"
        mig_dir.mkdir(parents=True)
        (mig_dir / "20260101000000_test.sql").write_text("-- UP\nCREATE TABLE t (id INT);\n-- DOWN\n")
        
        db_path = tmp_project / "test.db"
        db = SQLiteDB(str(db_path))
        db_path.touch()
        db.connect()
        run_migrations(db, str(tmp_project))
        count = run_migrations(db, str(tmp_project))
        assert count == 0  # Already applied
        db.close()

    def test_rollback(self, tmp_project):
        mig_dir = tmp_project / ".mywork" / "migrations"
        mig_dir.mkdir(parents=True)
        (mig_dir / "20260101000000_test.sql").write_text(
            "-- UP\nCREATE TABLE rollme (id INT);\n-- DOWN\nDROP TABLE rollme;"
        )
        
        db_path = tmp_project / "test.db"
        db = SQLiteDB(str(db_path))
        db_path.touch()
        db.connect()
        run_migrations(db, str(tmp_project))
        assert any(t["name"] == "rollme" for t in db.tables())
        
        rollback_migration(db, str(tmp_project))
        assert not any(t["name"] == "rollme" for t in db.tables())
        db.close()


# ─── Seed Tests ──────────────────────────────────────────────────
class TestSeeding:
    def test_seed_json(self, sqlite_db, tmp_project):
        seed_dir = tmp_project / ".mywork" / "seeds"
        seed_dir.mkdir(parents=True, exist_ok=True)
        (seed_dir / "seed.json").write_text(json.dumps({
            "users": [
                {"id": 10, "name": "Seed1", "email": "s1@test.com"},
                {"id": 11, "name": "Seed2", "email": "s2@test.com"}
            ]
        }))
        
        db = SQLiteDB(str(sqlite_db))
        db.connect()
        result = seed_database(db, str(seed_dir / "seed.json"), str(tmp_project))
        assert result is True
        _, rows = db.query("SELECT COUNT(*) FROM users")
        assert rows[0][0] == 4  # 2 original + 2 seeded
        db.close()

    def test_seed_no_file(self, sqlite_db, tmp_project):
        db = SQLiteDB(str(sqlite_db))
        db.connect()
        result = seed_database(db, None, str(tmp_project))
        assert result is False
        db.close()


# ─── Command Tests ───────────────────────────────────────────────
class TestCommands:
    def test_help(self, tmp_project, capsys):
        cmd_db(["--help"])
        out = capsys.readouterr().out
        assert "Database Management" in out

    def test_status_no_db(self, tmp_project, capsys):
        cmd_db(["status"])
        out = capsys.readouterr().out
        assert "No database detected" in out

    def test_status_with_db(self, sqlite_db, capsys):
        cmd_db(["status"])
        out = capsys.readouterr().out
        assert "sqlite" in out

    def test_init_sqlite(self, tmp_project, capsys):
        cmd_db(["init", "sqlite"])
        out = capsys.readouterr().out
        assert "initialized" in out
        assert (tmp_project / ".mywork" / "db.json").exists()

    def test_tables(self, sqlite_db, capsys):
        cmd_db(["tables"])
        out = capsys.readouterr().out
        assert "users" in out
        assert "posts" in out

    def test_schema(self, sqlite_db, capsys):
        cmd_db(["schema", "users"])
        out = capsys.readouterr().out
        assert "name" in out
        assert "email" in out

    def test_query(self, sqlite_db, capsys):
        cmd_db(["query", "SELECT name FROM users WHERE id = 1"])
        out = capsys.readouterr().out
        assert "Alice" in out

    def test_migrate_create(self, sqlite_db, capsys):
        cmd_db(["migrate", "add_categories"])
        out = capsys.readouterr().out
        assert "Created" in out

    def test_migrate_list(self, sqlite_db, capsys):
        create_migration("test_mig")
        cmd_db(["migrate", "--list"])
        out = capsys.readouterr().out
        assert "test_mig" in out

    def test_export(self, sqlite_db, capsys):
        cmd_db(["export", "users", "--json"])
        out = capsys.readouterr().out
        assert "Exported" in out

    def test_backup(self, sqlite_db, capsys):
        cmd_db(["backup"])
        out = capsys.readouterr().out
        assert "Backup" in out

    def test_unknown_subcommand(self, sqlite_db, capsys):
        result = cmd_db(["foobar"])
        assert result == 1

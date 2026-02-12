#!/usr/bin/env python3
"""
MyWork-AI Database Migration Tool
==================================
Universal database migration management.
Supports: SQLite, PostgreSQL, MySQL (via connection string auto-detect).

Commands:
  mw migrate init          Create migrations directory
  mw migrate create <name> Create a new migration file
  mw migrate up            Run pending migrations
  mw migrate down [n]      Rollback last N migrations (default: 1)
  mw migrate status        Show migration status
  mw migrate history       Show migration history
  mw migrate reset         Rollback all migrations
"""

import os
import sys
import json
import sqlite3
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

# ANSI colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

MIGRATIONS_DIR = "migrations"
MIGRATION_TABLE = "_mw_migrations"


def _find_project_root() -> Path:
    """Find project root by looking for common markers."""
    cwd = Path.cwd()
    markers = ["package.json", "pyproject.toml", "setup.py", "Cargo.toml", "go.mod", ".git"]
    for parent in [cwd] + list(cwd.parents):
        if any((parent / m).exists() for m in markers):
            return parent
    return cwd


def _get_migrations_dir() -> Path:
    """Get migrations directory path."""
    root = _find_project_root()
    return root / MIGRATIONS_DIR


def _get_db_path() -> str:
    """Auto-detect database connection from environment or config."""
    # Check env vars
    for key in ["DATABASE_URL", "DB_URL", "SQLITE_PATH", "DB_PATH"]:
        val = os.environ.get(key)
        if val:
            return val
    
    # Check .env file
    env_file = _find_project_root() / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key in ("DATABASE_URL", "DB_URL", "SQLITE_PATH", "DB_PATH") and val and not val.startswith("xxx"):
                return val
    
    # Default to SQLite
    return f"sqlite:///{_find_project_root() / 'db.sqlite3'}"


def _connect_sqlite(path: str) -> sqlite3.Connection:
    """Connect to SQLite database."""
    if path.startswith("sqlite:///"):
        path = path[len("sqlite:///"):]
    elif path.startswith("sqlite://"):
        path = path[len("sqlite://"):]
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _ensure_migration_table(conn: sqlite3.Connection):
    """Create migration tracking table if it doesn't exist."""
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {MIGRATION_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            checksum TEXT NOT NULL,
            applied_at TEXT NOT NULL,
            execution_time_ms INTEGER DEFAULT 0
        )
    """)
    conn.commit()


def _get_applied_migrations(conn: sqlite3.Connection) -> List[dict]:
    """Get list of applied migrations."""
    _ensure_migration_table(conn)
    cursor = conn.execute(
        f"SELECT version, name, checksum, applied_at, execution_time_ms FROM {MIGRATION_TABLE} ORDER BY version"
    )
    return [
        {"version": r[0], "name": r[1], "checksum": r[2], "applied_at": r[3], "time_ms": r[4]}
        for r in cursor.fetchall()
    ]


def _get_pending_migrations(migrations_dir: Path, applied: List[dict]) -> List[Tuple[str, Path]]:
    """Get list of pending migration files."""
    applied_versions = {m["version"] for m in applied}
    pending = []
    
    if not migrations_dir.exists():
        return pending
    
    for f in sorted(migrations_dir.glob("*.sql")):
        # Extract version from filename: YYYYMMDDHHMMSS_name.sql
        version = f.stem.split("_")[0]
        if version not in applied_versions and not f.name.endswith(".down.sql"):
            pending.append((version, f))
    
    return pending


def _file_checksum(path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def cmd_migrate_init(args: List[str]) -> int:
    """Initialize migrations directory."""
    migrations_dir = _get_migrations_dir()
    
    if migrations_dir.exists():
        print(f"{YELLOW}⚠️  Migrations directory already exists: {migrations_dir}{RESET}")
        return 0
    
    migrations_dir.mkdir(parents=True)
    
    # Create README
    readme = migrations_dir / "README.md"
    readme.write_text("""# Database Migrations

This directory contains database migration files managed by `mw migrate`.

## Naming Convention
Files follow the pattern: `YYYYMMDDHHMMSS_description.sql`

Each migration can have an optional rollback file: `YYYYMMDDHHMMSS_description.down.sql`

## Commands
```bash
mw migrate create <name>   # Create new migration
mw migrate up              # Apply pending migrations
mw migrate down            # Rollback last migration
mw migrate status          # Show current status
mw migrate history         # Full migration history
```
""")
    
    print(f"{GREEN}✅ Migrations directory created: {migrations_dir}{RESET}")
    print(f"{DIM}   Create your first migration: mw migrate create initial_schema{RESET}")
    return 0


def cmd_migrate_create(args: List[str]) -> int:
    """Create a new migration file."""
    if not args:
        print(f"{RED}❌ Usage: mw migrate create <name>{RESET}")
        print(f"{DIM}   Example: mw migrate create add_users_table{RESET}")
        return 1
    
    name = "_".join(args).lower().replace(" ", "_").replace("-", "_")
    migrations_dir = _get_migrations_dir()
    
    if not migrations_dir.exists():
        migrations_dir.mkdir(parents=True)
        print(f"{DIM}Created migrations directory{RESET}")
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    
    # Up migration
    up_file = migrations_dir / f"{timestamp}_{name}.sql"
    up_file.write_text(f"""-- Migration: {name}
-- Created: {datetime.now(timezone.utc).isoformat()}
-- Description: TODO - describe what this migration does

-- Write your SQL here
-- Example:
-- CREATE TABLE users (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     email TEXT NOT NULL UNIQUE,
--     name TEXT NOT NULL,
--     created_at TEXT NOT NULL DEFAULT (datetime('now'))
-- );
""")
    
    # Down migration
    down_file = migrations_dir / f"{timestamp}_{name}.down.sql"
    down_file.write_text(f"""-- Rollback: {name}
-- Reverses the migration above

-- Write your rollback SQL here
-- Example:
-- DROP TABLE IF EXISTS users;
""")
    
    print(f"{GREEN}✅ Created migration:{RESET}")
    print(f"   {CYAN}Up:   {up_file.name}{RESET}")
    print(f"   {CYAN}Down: {down_file.name}{RESET}")
    print(f"\n{DIM}Edit the files, then run: mw migrate up{RESET}")
    return 0


def cmd_migrate_up(args: List[str]) -> int:
    """Run pending migrations."""
    db_path = _get_db_path()
    
    if not db_path.startswith("sqlite"):
        print(f"{YELLOW}⚠️  Only SQLite is supported in this version.{RESET}")
        print(f"{DIM}   Found: {db_path}{RESET}")
        print(f"{DIM}   PostgreSQL/MySQL support coming in v2.2{RESET}")
        return 1
    
    conn = _connect_sqlite(db_path)
    applied = _get_applied_migrations(conn)
    migrations_dir = _get_migrations_dir()
    pending = _get_pending_migrations(migrations_dir, applied)
    
    if not pending:
        print(f"{GREEN}✅ Database is up to date. No pending migrations.{RESET}")
        conn.close()
        return 0
    
    # Limit if specified
    limit = None
    if args and args[0].isdigit():
        limit = int(args[0])
        pending = pending[:limit]
    
    print(f"{BLUE}🔄 Running {len(pending)} migration(s)...{RESET}\n")
    
    success_count = 0
    for version, path in pending:
        name = path.stem.split("_", 1)[1] if "_" in path.stem else path.stem
        sql = path.read_text()
        checksum = _file_checksum(path)
        
        print(f"  {CYAN}▶ {version}{RESET} {name}...", end=" ", flush=True)
        
        start = datetime.now()
        try:
            conn.executescript(sql)
            elapsed = int((datetime.now() - start).total_seconds() * 1000)
            
            conn.execute(
                f"INSERT INTO {MIGRATION_TABLE} (version, name, checksum, applied_at, execution_time_ms) VALUES (?, ?, ?, ?, ?)",
                (version, name, checksum, datetime.now(timezone.utc).isoformat(), elapsed)
            )
            conn.commit()
            
            print(f"{GREEN}✅{RESET} {DIM}({elapsed}ms){RESET}")
            success_count += 1
        except Exception as e:
            print(f"{RED}❌ FAILED{RESET}")
            print(f"    {RED}{e}{RESET}")
            conn.rollback()
            break
    
    conn.close()
    
    total = len(pending)
    if success_count == total:
        print(f"\n{GREEN}✅ All {total} migration(s) applied successfully.{RESET}")
    else:
        print(f"\n{YELLOW}⚠️  {success_count}/{total} migration(s) applied. Fix errors and retry.{RESET}")
    
    return 0 if success_count == total else 1


def cmd_migrate_down(args: List[str]) -> int:
    """Rollback migrations."""
    count = 1
    if args and args[0].isdigit():
        count = int(args[0])
    
    db_path = _get_db_path()
    if not db_path.startswith("sqlite"):
        print(f"{YELLOW}⚠️  Only SQLite supported in this version.{RESET}")
        return 1
    
    conn = _connect_sqlite(db_path)
    applied = _get_applied_migrations(conn)
    
    if not applied:
        print(f"{GREEN}✅ No migrations to rollback.{RESET}")
        conn.close()
        return 0
    
    to_rollback = list(reversed(applied))[:count]
    migrations_dir = _get_migrations_dir()
    
    print(f"{BLUE}🔄 Rolling back {len(to_rollback)} migration(s)...{RESET}\n")
    
    success_count = 0
    for mig in to_rollback:
        version = mig["version"]
        name = mig["name"]
        
        # Find down file
        down_files = list(migrations_dir.glob(f"{version}_*.down.sql"))
        
        print(f"  {CYAN}◀ {version}{RESET} {name}...", end=" ", flush=True)
        
        if not down_files:
            print(f"{YELLOW}⚠️  No rollback file found, removing record only{RESET}")
        else:
            sql = down_files[0].read_text()
            try:
                conn.executescript(sql)
            except Exception as e:
                print(f"{RED}❌ FAILED: {e}{RESET}")
                conn.rollback()
                break
        
        conn.execute(f"DELETE FROM {MIGRATION_TABLE} WHERE version = ?", (version,))
        conn.commit()
        print(f"{GREEN}✅{RESET}")
        success_count += 1
    
    conn.close()
    print(f"\n{GREEN}✅ Rolled back {success_count} migration(s).{RESET}")
    return 0


def cmd_migrate_status(args: List[str]) -> int:
    """Show migration status."""
    db_path = _get_db_path()
    migrations_dir = _get_migrations_dir()
    
    print(f"{BOLD}📊 Migration Status{RESET}\n")
    print(f"  {DIM}Database:{RESET}   {db_path}")
    print(f"  {DIM}Directory:{RESET}  {migrations_dir}\n")
    
    if not db_path.startswith("sqlite"):
        print(f"{YELLOW}⚠️  Only SQLite supported{RESET}")
        return 1
    
    conn = _connect_sqlite(db_path)
    applied = _get_applied_migrations(conn)
    pending = _get_pending_migrations(migrations_dir, applied)
    conn.close()
    
    if applied:
        print(f"  {GREEN}✅ Applied ({len(applied)}):{RESET}")
        for m in applied:
            print(f"     {GREEN}●{RESET} {m['version']} — {m['name']}")
    
    if pending:
        print(f"  {YELLOW}⏳ Pending ({len(pending)}):{RESET}")
        for version, path in pending:
            name = path.stem.split("_", 1)[1] if "_" in path.stem else path.stem
            print(f"     {YELLOW}○{RESET} {version} — {name}")
    
    if not applied and not pending:
        print(f"  {DIM}No migrations found.{RESET}")
        print(f"  {DIM}Create one: mw migrate create initial_schema{RESET}")
    
    return 0


def cmd_migrate_history(args: List[str]) -> int:
    """Show full migration history."""
    db_path = _get_db_path()
    if not db_path.startswith("sqlite"):
        print(f"{YELLOW}⚠️  Only SQLite supported{RESET}")
        return 1
    
    conn = _connect_sqlite(db_path)
    applied = _get_applied_migrations(conn)
    conn.close()
    
    print(f"{BOLD}📜 Migration History{RESET}\n")
    
    if not applied:
        print(f"  {DIM}No migrations have been applied yet.{RESET}")
        return 0
    
    print(f"  {'Version':<16} {'Name':<30} {'Applied At':<22} {'Time':>8}")
    print(f"  {'─'*16} {'─'*30} {'─'*22} {'─':─>8}")
    
    for m in applied:
        applied_at = m["applied_at"][:19].replace("T", " ")
        time_str = f"{m['time_ms']}ms" if m['time_ms'] else "—"
        print(f"  {GREEN}{m['version']:<16}{RESET} {m['name']:<30} {DIM}{applied_at:<22}{RESET} {time_str:>8}")
    
    print(f"\n  {DIM}Total: {len(applied)} migration(s){RESET}")
    return 0


def cmd_migrate_reset(args: List[str]) -> int:
    """Reset all migrations (rollback everything)."""
    db_path = _get_db_path()
    if not db_path.startswith("sqlite"):
        return 1
    
    conn = _connect_sqlite(db_path)
    applied = _get_applied_migrations(conn)
    conn.close()
    
    if not applied:
        print(f"{GREEN}✅ Nothing to reset.{RESET}")
        return 0
    
    print(f"{YELLOW}⚠️  This will rollback ALL {len(applied)} migration(s).{RESET}")
    
    # In CLI context, proceed (non-interactive for automation)
    return cmd_migrate_down([str(len(applied))])


def cmd_migrate(args: List[str] = None) -> int:
    """Main migration command dispatcher."""
    args = args or []
    
    if not args:
        # Default to status
        return cmd_migrate_status([])
    
    subcmd = args[0].lower()
    sub_args = args[1:]
    
    commands = {
        "init": cmd_migrate_init,
        "create": cmd_migrate_create,
        "new": cmd_migrate_create,
        "up": cmd_migrate_up,
        "apply": cmd_migrate_up,
        "down": cmd_migrate_down,
        "rollback": cmd_migrate_down,
        "status": cmd_migrate_status,
        "history": cmd_migrate_history,
        "log": cmd_migrate_history,
        "reset": cmd_migrate_reset,
        "help": lambda _: _print_help(),
        "-h": lambda _: _print_help(),
        "--help": lambda _: _print_help(),
    }
    
    if subcmd in commands:
        return commands[subcmd](sub_args)
    
    print(f"{RED}❌ Unknown migrate command: {subcmd}{RESET}")
    _print_help()
    return 1


def _print_help() -> int:
    """Print help for migrate command."""
    print(f"""{BOLD}🔄 mw migrate — Database Migration Manager{RESET}

{BOLD}Usage:{RESET}
    mw migrate                     Show migration status
    mw migrate init                Initialize migrations directory
    mw migrate create <name>       Create new migration
    mw migrate up [n]              Apply pending migrations (optionally limit to n)
    mw migrate down [n]            Rollback last n migrations (default: 1)
    mw migrate status              Show current migration status
    mw migrate history             Show full migration history
    mw migrate reset               Rollback all migrations

{BOLD}Database Detection:{RESET}
    Auto-detects from: DATABASE_URL, DB_URL, SQLITE_PATH, DB_PATH
    Falls back to: sqlite:///db.sqlite3

{BOLD}Migration Files:{RESET}
    Up:   migrations/YYYYMMDDHHMMSS_name.sql
    Down: migrations/YYYYMMDDHHMMSS_name.down.sql
""")
    return 0


if __name__ == "__main__":
    sys.exit(cmd_migrate(sys.argv[1:]))

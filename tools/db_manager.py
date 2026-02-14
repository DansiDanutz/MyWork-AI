#!/usr/bin/env python3
"""
MyWork DB Manager (mw db)
=========================
Universal database management for projects.

Usage:
    mw db status              Show database connection status
    mw db init [type]         Initialize database config (sqlite/postgres/mysql)
    mw db migrate [name]      Create or run migrations
    mw db migrate --run       Apply pending migrations
    mw db migrate --rollback  Rollback last migration
    mw db seed [file]         Seed database with sample data
    mw db query "SQL"         Run an ad-hoc SQL query
    mw db tables              List all tables with row counts
    mw db schema [table]      Show table schema/columns
    mw db export [table]      Export table(s) to CSV/JSON
    mw db backup [path]       Backup database
    mw db restore [path]      Restore from backup
    mw db reset               Drop all tables and re-migrate (with confirmation)
"""

import json
import os
import sys
import time
import sqlite3
import csv
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any


# ─── Colors ──────────────────────────────────────────────────────────
def green(t): return f"\033[92m{t}\033[0m"
def red(t): return f"\033[91m{t}\033[0m"
def yellow(t): return f"\033[93m{t}\033[0m"
def cyan(t): return f"\033[96m{t}\033[0m"
def bold(t): return f"\033[1m{t}\033[0m"
def dim(t): return f"\033[2m{t}\033[0m"


# ─── DB Detection ────────────────────────────────────────────────────
def detect_db_config(project_path: str = ".") -> Optional[Dict]:
    """Auto-detect database configuration from project files."""
    p = Path(project_path)
    
    # Check .env for DATABASE_URL
    env_file = p / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key in ("DATABASE_URL", "DB_URL", "DB_CONNECTION"):
                return parse_db_url(val)
    
    # Check for prisma schema
    prisma_paths = [p / "prisma/schema.prisma", p / "schema.prisma"]
    for pp in prisma_paths:
        if pp.exists():
            content = pp.read_text()
            if "sqlite" in content.lower():
                # Find the sqlite file
                for line in content.splitlines():
                    if "url" in line and "file:" in line:
                        db_path = line.split("file:")[1].strip().rstrip('"').rstrip(")")
                        return {"type": "sqlite", "path": str(p / "prisma" / db_path), "source": "prisma"}
                return {"type": "sqlite", "path": str(p / "prisma/dev.db"), "source": "prisma"}
            elif "postgresql" in content.lower():
                return {"type": "postgres", "source": "prisma", "note": "Set DATABASE_URL in .env"}
    
    # Check for common SQLite files
    for name in ["db.sqlite3", "database.db", "app.db", "dev.db", "data.db", "main.db"]:
        if (p / name).exists():
            return {"type": "sqlite", "path": str(p / name), "source": "auto-detected"}
    
    # Check for knexfile
    for name in ["knexfile.js", "knexfile.ts"]:
        if (p / name).exists():
            return {"type": "unknown", "source": "knex", "note": "Check knexfile for connection details"}
    
    # Check for alembic (Python SQLAlchemy)
    if (p / "alembic.ini").exists() or (p / "alembic").is_dir():
        return {"type": "unknown", "source": "alembic", "note": "Check alembic.ini for connection"}
    
    # Check mywork db config
    mw_config = p / ".mywork" / "db.json"
    if mw_config.exists():
        return json.loads(mw_config.read_text())
    
    return None


def parse_db_url(url: str) -> Dict:
    """Parse a DATABASE_URL into components."""
    if url.startswith("sqlite"):
        path = url.replace("sqlite:///", "").replace("sqlite://", "")
        return {"type": "sqlite", "path": path, "source": "env"}
    elif url.startswith("postgres"):
        return {"type": "postgres", "url": url, "source": "env"}
    elif url.startswith("mysql"):
        return {"type": "mysql", "url": url, "source": "env"}
    else:
        return {"type": "unknown", "url": url, "source": "env"}


# ─── SQLite Operations ──────────────────────────────────────────────
class SQLiteDB:
    def __init__(self, path: str):
        self.path = path
        self.conn = None
    
    def connect(self) -> bool:
        try:
            self.conn = sqlite3.connect(self.path)
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"  {red('✗')} Connection failed: {e}")
            return False
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def tables(self) -> List[Dict]:
        cur = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        tables = []
        for row in cur.fetchall():
            name = row[0]
            count = self.conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            tables.append({"name": name, "rows": count})
        return tables
    
    def schema(self, table: str) -> List[Dict]:
        cur = self.conn.execute(f'PRAGMA table_info("{table}")')
        cols = []
        for row in cur.fetchall():
            cols.append({
                "cid": row[0], "name": row[1], "type": row[2],
                "notnull": bool(row[3]), "default": row[4], "pk": bool(row[5])
            })
        return cols
    
    def query(self, sql: str) -> Tuple[List[str], List[tuple]]:
        cur = self.conn.execute(sql)
        if cur.description:
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            return cols, [tuple(r) for r in rows]
        self.conn.commit()
        return [], []
    
    def export_table(self, table: str, fmt: str = "csv") -> str:
        cols, rows = self.query(f'SELECT * FROM "{table}"')
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if fmt == "json":
            out_path = f"{table}_{ts}.json"
            data = [dict(zip(cols, row)) for row in rows]
            Path(out_path).write_text(json.dumps(data, indent=2, default=str))
        else:
            out_path = f"{table}_{ts}.csv"
            with open(out_path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(cols)
                w.writerows(rows)
        return out_path


# ─── Migration System ───────────────────────────────────────────────
MIGRATIONS_DIR = ".mywork/migrations"


def ensure_migrations_dir(project_path: str = "."):
    Path(project_path, MIGRATIONS_DIR).mkdir(parents=True, exist_ok=True)


def create_migration(name: str, project_path: str = ".") -> str:
    ensure_migrations_dir(project_path)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_name = name.replace(" ", "_").lower()
    filename = f"{ts}_{safe_name}.sql"
    filepath = Path(project_path, MIGRATIONS_DIR, filename)
    filepath.write_text(f"""-- Migration: {name}
-- Created: {datetime.now().isoformat()}

-- UP
-- Write your forward migration SQL here


-- DOWN
-- Write your rollback SQL here (after the DOWN marker)

""")
    return str(filepath)


def get_migrations(project_path: str = ".") -> List[str]:
    mdir = Path(project_path, MIGRATIONS_DIR)
    if not mdir.exists():
        return []
    return sorted(f.name for f in mdir.glob("*.sql"))


def run_migrations(db: SQLiteDB, project_path: str = ".") -> int:
    """Run pending migrations. Returns count of applied."""
    # Create migrations tracking table
    db.conn.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            applied_at TEXT NOT NULL
        )
    """)
    db.conn.commit()
    
    applied = {r[0] for r in db.conn.execute("SELECT name FROM _migrations").fetchall()}
    migrations = get_migrations(project_path)
    pending = [m for m in migrations if m not in applied]
    
    if not pending:
        return 0
    
    count = 0
    for mig in pending:
        content = Path(project_path, MIGRATIONS_DIR, mig).read_text()
        # Extract UP portion (before -- DOWN)
        up_sql = content.split("-- DOWN")[0]
        # Remove comment lines for execution
        sql_lines = [l for l in up_sql.splitlines() if not l.strip().startswith("--") and l.strip()]
        if sql_lines:
            for stmt in "\n".join(sql_lines).split(";"):
                stmt = stmt.strip()
                if stmt:
                    db.conn.execute(stmt)
        db.conn.execute("INSERT INTO _migrations (name, applied_at) VALUES (?, ?)",
                       (mig, datetime.now().isoformat()))
        db.conn.commit()
        print(f"  {green('✓')} Applied: {mig}")
        count += 1
    return count


def rollback_migration(db: SQLiteDB, project_path: str = ".") -> bool:
    """Rollback the last migration."""
    row = db.conn.execute("SELECT name FROM _migrations ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        print(f"  {yellow('!')} No migrations to rollback")
        return False
    
    mig_name = row[0]
    content = Path(project_path, MIGRATIONS_DIR, mig_name).read_text()
    
    if "-- DOWN" in content:
        down_sql = content.split("-- DOWN")[1]
        sql_lines = [l for l in down_sql.splitlines() if not l.strip().startswith("--") and l.strip()]
        if sql_lines:
            for stmt in "\n".join(sql_lines).split(";"):
                stmt = stmt.strip()
                if stmt:
                    db.conn.execute(stmt)
    
    db.conn.execute("DELETE FROM _migrations WHERE name = ?", (mig_name,))
    db.conn.commit()
    print(f"  {green('✓')} Rolled back: {mig_name}")
    return True


# ─── Seed System ────────────────────────────────────────────────────
def seed_database(db: SQLiteDB, seed_file: str = None, project_path: str = "."):
    """Seed database from JSON or SQL file."""
    if seed_file is None:
        # Look for default seed files
        for name in [".mywork/seeds/seed.json", ".mywork/seeds/seed.sql", "seed.json", "seed.sql"]:
            if Path(project_path, name).exists():
                seed_file = str(Path(project_path, name))
                break
    
    if not seed_file or not Path(seed_file).exists():
        print(f"  {red('✗')} No seed file found. Create one at .mywork/seeds/seed.json")
        fmt_example = '{"table_name": [{"col": "val", ...}, ...]}'
        print(f"  {dim('Format: ' + fmt_example)}") 
        return False
    
    if seed_file.endswith(".json"):
        data = json.loads(Path(seed_file).read_text())
        total = 0
        for table, rows in data.items():
            for row in rows:
                cols = ", ".join(f'"{k}"' for k in row.keys())
                placeholders = ", ".join("?" * len(row))
                db.conn.execute(f'INSERT OR REPLACE INTO "{table}" ({cols}) VALUES ({placeholders})',
                              list(row.values()))
                total += 1
            print(f"  {green('✓')} Seeded {table}: {len(rows)} rows")
        db.conn.commit()
        print(f"\n  Total: {total} rows inserted")
    elif seed_file.endswith(".sql"):
        sql = Path(seed_file).read_text()
        db.conn.executescript(sql)
        print(f"  {green('✓')} Executed seed SQL")
    
    return True


# ─── Commands ────────────────────────────────────────────────────────
def cmd_db(args: List[str] = None):
    """Universal database management."""
    args = args or []
    
    if not args or args[0] in ("-h", "--help", "help"):
        print(f"\n  {bold('📦 mw db')} — Database Management\n")
        print(f"  {cyan('Usage:')}")
        print(f"    mw db status                    Connection status & info")
        print(f"    mw db init [sqlite|postgres]     Initialize DB config")
        print(f"    mw db tables                     List tables with row counts")
        print(f"    mw db schema <table>             Show table columns")
        print(f"    mw db query \"SQL\"                Run ad-hoc SQL")
        print(f"    mw db migrate <name>             Create a new migration")
        print(f"    mw db migrate --run              Apply pending migrations")
        print(f"    mw db migrate --rollback         Rollback last migration")
        print(f"    mw db migrate --list             List all migrations")
        print(f"    mw db seed [file]                Seed with sample data")
        print(f"    mw db export <table> [--json]    Export table to CSV/JSON")
        print(f"    mw db backup [path]              Backup database")
        print(f"    mw db restore <path>             Restore from backup")
        print(f"    mw db reset                      Drop all & re-migrate")
        print()
        return 0
    
    subcmd = args[0]
    sub_args = args[1:]
    
    # ── Init ──
    if subcmd == "init":
        db_type = sub_args[0] if sub_args else "sqlite"
        mw_dir = Path(".mywork")
        mw_dir.mkdir(exist_ok=True)
        
        if db_type == "sqlite":
            config = {"type": "sqlite", "path": "data.db", "source": "mywork-init"}
            Path("data.db").touch()
        elif db_type == "postgres":
            config = {"type": "postgres", "url": "postgresql://user:pass@localhost:5432/mydb", "source": "mywork-init"}
        elif db_type == "mysql":
            config = {"type": "mysql", "url": "sqlite:///mydb.sqlite", "source": "mywork-init"}
        else:
            print(f"  {red('✗')} Unknown type: {db_type}. Use sqlite, postgres, or mysql")
            return 1
        
        (mw_dir / "db.json").write_text(json.dumps(config, indent=2))
        Path(MIGRATIONS_DIR).mkdir(parents=True, exist_ok=True)
        Path(".mywork/seeds").mkdir(parents=True, exist_ok=True)
        
        print(f"\n  {green('✓')} Database initialized: {bold(db_type)}")
        print(f"  Config: .mywork/db.json")
        print(f"  Migrations: {MIGRATIONS_DIR}/")
        print(f"  Seeds: .mywork/seeds/")
        return 0
    
    # ── Detect config ──
    config = detect_db_config()
    
    # ── Status ──
    if subcmd == "status":
        print(f"\n  {bold('📦 Database Status')}\n")
        if not config:
            print(f"  {yellow('!')} No database detected")
            print(f"  {dim('Run: mw db init [sqlite|postgres|mysql]')}")
            return 0
        
        print(f"  Type:   {green(config['type'])}")
        print(f"  Source: {dim(config.get('source', 'unknown'))}")
        
        if config["type"] == "sqlite":
            path = config.get("path", "")
            if Path(path).exists():
                size = Path(path).stat().st_size
                if size < 1024:
                    sz = f"{size}B"
                elif size < 1024*1024:
                    sz = f"{size/1024:.1f}KB"
                else:
                    sz = f"{size/1024/1024:.1f}MB"
                print(f"  Path:   {path}")
                print(f"  Size:   {sz}")
                
                db = SQLiteDB(path)
                if db.connect():
                    tables = db.tables()
                    total_rows = sum(t["rows"] for t in tables)
                    print(f"  Tables: {len(tables)}")
                    print(f"  Rows:   {total_rows}")
                    db.close()
            else:
                print(f"  Path:   {red(path)} (not found)")
        elif config.get("url"):
            # Mask password in URL
            url = config["url"]
            if "@" in url:
                pre, post = url.split("@", 1)
                if ":" in pre:
                    parts = pre.rsplit(":", 1)
                    url = f"{parts[0]}:****@{post}"
            print(f"  URL:    {url}")
        
        if config.get("note"):
            print(f"  Note:   {yellow(config['note'])}")
        
        # Show migration status
        migrations = get_migrations()
        if migrations:
            print(f"\n  Migrations: {len(migrations)} total")
        
        print()
        return 0
    
    # ── For SQLite-specific commands ──
    if not config:
        print(f"  {red('✗')} No database detected. Run: mw db init")
        return 1
    
    if config["type"] != "sqlite":
        if subcmd not in ("init", "status", "migrate"):
            print(f"  {yellow('!')} Direct {subcmd} only supported for SQLite currently.")
            db_type = config["type"]
            print(f"  {dim(f'For {db_type}, use your ORM tools or set DATABASE_URL')}")
            return 1
    
    db_path = config.get("path", "")
    if not db_path or not Path(db_path).exists():
        if subcmd != "migrate":
            print(f"  {red('✗')} Database file not found: {db_path}")
            return 1
    
    db = SQLiteDB(db_path) if db_path and Path(db_path).exists() else None
    
    try:
        # ── Tables ──
        if subcmd == "tables":
            if not db or not db.connect():
                return 1
            tables = db.tables()
            if not tables:
                print(f"\n  {yellow('!')} No tables found\n")
                return 0
            print(f"\n  {bold('📋 Tables')}\n")
            max_name = max(len(t["name"]) for t in tables)
            for t in tables:
                bar = "█" * min(t["rows"] // 10 + 1, 30) if t["rows"] > 0 else dim("empty")
                name = t['name']
                rows_str = str(t['rows']).rjust(8)
                print(f"  {name:<{max_name+2}} {green(rows_str)} rows  {bar}")
            print(f"\n  Total: {sum(t['rows'] for t in tables)} rows in {len(tables)} tables\n")
            return 0
        
        # ── Schema ──
        elif subcmd == "schema":
            if not sub_args:
                print(f"  {red('✗')} Usage: mw db schema <table>")
                return 1
            if not db or not db.connect():
                return 1
            table = sub_args[0]
            cols = db.schema(table)
            if not cols:
                print(f"  {red('✗')} Table not found: {table}")
                return 1
            print(f"\n  {bold(f'📋 Schema: {table}')}\n")
            for c in cols:
                pk = " 🔑" if c["pk"] else ""
                nn = " NOT NULL" if c["notnull"] else ""
                default = f" = {c['default']}" if c["default"] is not None else ""
                print(f"  {c['name']:<30} {cyan(c['type'] or 'ANY'):<15}{pk}{nn}{default}")
            print()
            return 0
        
        # ── Query ──
        elif subcmd == "query":
            if not sub_args:
                print(f"  {red('✗')} Usage: mw db query \"SELECT * FROM table\"")
                return 1
            if not db or not db.connect():
                return 1
            sql = " ".join(sub_args)
            start = time.time()
            cols, rows = db.query(sql)
            elapsed = time.time() - start
            
            if not cols:
                print(f"  {green('✓')} Query executed ({elapsed:.3f}s)")
                return 0
            
            # Pretty print results
            print(f"\n  {dim(f'{len(rows)} rows ({elapsed:.3f}s)')}\n")
            
            # Calculate column widths
            widths = [len(c) for c in cols]
            for row in rows[:50]:  # Limit display
                for i, val in enumerate(row):
                    widths[i] = max(widths[i], min(len(str(val)), 40))
            
            # Header
            header = "  ".join(bold(c.ljust(widths[i])) for i, c in enumerate(cols))
            print(f"  {header}")
            print(f"  {'─' * sum(w + 2 for w in widths)}")
            
            # Rows
            for row in rows[:50]:
                line = "  ".join(str(v)[:40].ljust(widths[i]) for i, v in enumerate(row))
                print(f"  {line}")
            
            if len(rows) > 50:
                print(f"\n  {dim(f'... and {len(rows) - 50} more rows')}")
            print()
            return 0
        
        # ── Migrate ──
        elif subcmd == "migrate":
            if not sub_args:
                print(f"  {red('✗')} Usage: mw db migrate <name> | --run | --rollback | --list")
                return 1
            
            flag = sub_args[0]
            
            if flag == "--list":
                migrations = get_migrations()
                if not migrations:
                    print(f"  {yellow('!')} No migrations found")
                    return 0
                print(f"\n  {bold('📋 Migrations')}\n")
                
                # Check which are applied
                applied = set()
                if db and db.connect():
                    try:
                        applied = {r[0] for r in db.conn.execute("SELECT name FROM _migrations").fetchall()}
                    except:
                        pass
                
                for m in migrations:
                    status = green("✓ applied") if m in applied else yellow("○ pending")
                    print(f"  {status}  {m}")
                print()
                return 0
            
            elif flag == "--run":
                if not db:
                    # Create DB if sqlite
                    if config["type"] == "sqlite":
                        Path(db_path).touch()
                        db = SQLiteDB(db_path)
                    else:
                        print(f"  {red('✗')} Cannot connect to database")
                        return 1
                if not db.connect():
                    return 1
                count = run_migrations(db)
                if count == 0:
                    print(f"  {green('✓')} No pending migrations")
                else:
                    print(f"\n  {green('✓')} Applied {count} migration(s)")
                return 0
            
            elif flag == "--rollback":
                if not db or not db.connect():
                    return 1
                rollback_migration(db)
                return 0
            
            else:
                # Create new migration
                name = " ".join(sub_args)
                path = create_migration(name)
                print(f"  {green('✓')} Created: {path}")
                return 0
        
        # ── Export ──
        elif subcmd == "export":
            if not sub_args:
                print(f"  {red('✗')} Usage: mw db export <table> [--json]")
                return 1
            if not db or not db.connect():
                return 1
            table = sub_args[0]
            fmt = "json" if "--json" in sub_args else "csv"
            path = db.export_table(table, fmt)
            print(f"  {green('✓')} Exported to: {path}")
            return 0
        
        # ── Backup ──
        elif subcmd == "backup":
            if config["type"] != "sqlite":
                print(f"  {yellow('!')} Backup only supported for SQLite. Use pg_dump for Postgres.")
                return 1
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = sub_args[0] if sub_args else f"backup_{Path(db_path).stem}_{ts}.db"
            shutil.copy2(db_path, backup_path)
            size = Path(backup_path).stat().st_size / 1024
            print(f"  {green('✓')} Backup: {backup_path} ({size:.1f}KB)")
            return 0
        
        # ── Restore ──
        elif subcmd == "restore":
            if not sub_args:
                print(f"  {red('✗')} Usage: mw db restore <backup-file>")
                return 1
            backup = sub_args[0]
            if not Path(backup).exists():
                print(f"  {red('✗')} File not found: {backup}")
                return 1
            # Safety backup first
            if Path(db_path).exists():
                shutil.copy2(db_path, f"{db_path}.before_restore")
            shutil.copy2(backup, db_path)
            print(f"  {green('✓')} Restored from: {backup}")
            return 0
        
        # ── Reset ──
        elif subcmd == "reset":
            print(f"  {red('⚠  WARNING: This will DELETE all data!')}")
            confirm = input(f"  Type 'yes' to confirm: ")
            if confirm.lower() != "yes":
                print(f"  {yellow('!')} Cancelled")
                return 0
            if Path(db_path).exists():
                # Backup first
                shutil.copy2(db_path, f"{db_path}.before_reset")
                Path(db_path).unlink()
                Path(db_path).touch()
                print(f"  {green('✓')} Database reset (backup saved as {db_path}.before_reset)")
                # Re-run migrations
                db = SQLiteDB(db_path)
                if db.connect():
                    count = run_migrations(db)
                    if count:
                        print(f"  {green('✓')} Re-applied {count} migration(s)")
            return 0
        
        else:
            print(f"  {red('✗')} Unknown subcommand: {subcmd}")
            print(f"  {dim('Run: mw db --help')}")
            return 1
    
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    cmd_db(sys.argv[1:])

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "queuectl.db"

def init_db(path: str | None = None):
    db = path or str(DB_PATH)
    conn = sqlite3.connect(db, isolation_level=None)
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        command TEXT NOT NULL,
        state TEXT NOT NULL,
        attempts INTEGER NOT NULL DEFAULT 0,
        max_retries INTEGER NOT NULL DEFAULT 3,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        next_run_at INTEGER DEFAULT 0,
        last_error TEXT DEFAULT NULL,
        output TEXT DEFAULT NULL,
        timeout INTEGER DEFAULT NULL
    );
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)
    # ensure new columns exist for older DBs
    try:
        cols = [r[1] for r in cur.execute("PRAGMA table_info(jobs);").fetchall()]
        if 'output' not in cols:
            cur.execute("ALTER TABLE jobs ADD COLUMN output TEXT DEFAULT NULL;")
        if 'timeout' not in cols:
            cur.execute("ALTER TABLE jobs ADD COLUMN timeout INTEGER DEFAULT NULL;")
    except Exception:
        # best-effort; ignore if PRAGMA/ALTER fails on very old SQLite
        pass
    # default config
    cur.execute("INSERT OR IGNORE INTO config(key, value) VALUES (?,?)", ("backoff_base", "2"))
    cur.execute("INSERT OR IGNORE INTO config(key, value) VALUES (?,?)", ("max_retries", "3"))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("DB initialized.")

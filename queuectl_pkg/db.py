import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "queuectl.db"

def get_conn(path=None):
    conn = sqlite3.connect(str(path or DB_PATH), timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn

def query_all(sql: str, params: tuple = ()): 
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def query_one(sql: str, params: tuple = ()): 
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def execute(sql: str, params: tuple = ()): 
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()

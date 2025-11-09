from .db import query_one, execute
from typing import Optional

def get_config(key: str) -> Optional[str]:
    row = query_one("SELECT value FROM config WHERE key=?", (key,))
    return row["value"] if row else None

def set_config(key: str, value: str):
    execute("INSERT OR REPLACE INTO config(key, value) VALUES (?,?);", (key, value))

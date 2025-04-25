import sqlite3
from pathlib import Path

_DB_PATH = Path(__file__).parent.parent / "database" / "frota.db"

def get_connection(db_path: str | Path = _DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row          # pra devolver dict-like
    return conn

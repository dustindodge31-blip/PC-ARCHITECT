"""Persists saved builds to a local SQLite database."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "builds.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS builds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                parts_json TEXT NOT NULL
            )
        """)


def save_build(name: str, parts: dict, build_id: int | None = None) -> int:
    now = datetime.now(timezone.utc).isoformat()
    selection = {cat: (p["id"] if p else None) for cat, p in parts.items()}
    parts_json = json.dumps(selection)
    with _connect() as conn:
        if build_id is None:
            cur = conn.execute(
                "INSERT INTO builds (name, created_at, updated_at, parts_json) VALUES (?, ?, ?, ?)",
                (name, now, now, parts_json),
            )
            return cur.lastrowid
        else:
            conn.execute(
                "UPDATE builds SET name = ?, updated_at = ?, parts_json = ? WHERE id = ?",
                (name, now, parts_json, build_id),
            )
            return build_id


def list_builds() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM builds ORDER BY updated_at DESC").fetchall()
        return [dict(row) for row in rows]


def get_build(build_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM builds WHERE id = ?", (build_id,)).fetchone()
        return dict(row) if row else None


def delete_build(build_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM builds WHERE id = ?", (build_id,))

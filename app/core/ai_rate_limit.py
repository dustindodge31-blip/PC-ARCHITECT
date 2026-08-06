"""Caps AI Architect calls per device per day.

This is a client-side guard against accidental overuse through the app's own
UI (e.g. mashing "Generate"), not a real security boundary -- the Gemini key
ships inside the app bundle and could be extracted and used directly,
bypassing this entirely. A proper fix would proxy Gemini calls through a
server that holds the key and enforces limits per authenticated user; this
is the practical stopgap until that exists.
"""
import json
import os
from datetime import date
from pathlib import Path

USAGE_PATH = Path(__file__).resolve().parent.parent / "data" / "ai_usage.json"
DAILY_LIMIT = int(os.getenv("AI_ARCHITECT_DAILY_LIMIT", "15"))


def _load() -> dict:
    if not USAGE_PATH.exists():
        return {}
    try:
        return json.loads(USAGE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    USAGE_PATH.write_text(json.dumps(data), encoding="utf-8")


def calls_remaining_today() -> int:
    data = _load()
    used = data.get(str(date.today()), 0)
    return max(0, DAILY_LIMIT - used)


def record_call() -> None:
    today = str(date.today())
    data = {today: _load().get(today, 0) + 1}
    _save(data)

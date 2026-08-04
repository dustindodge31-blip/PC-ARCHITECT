"""Persists the Supabase auth session locally so login survives app restarts."""
import json
from pathlib import Path

SESSION_PATH = Path(__file__).resolve().parent.parent / "data" / "community_session.json"


def load_tokens() -> tuple[str, str] | None:
    if not SESSION_PATH.exists():
        return None
    try:
        data = json.loads(SESSION_PATH.read_text(encoding="utf-8"))
        return data["access_token"], data["refresh_token"]
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def save_tokens(access_token: str, refresh_token: str) -> None:
    SESSION_PATH.write_text(
        json.dumps({"access_token": access_token, "refresh_token": refresh_token}),
        encoding="utf-8",
    )


def clear_tokens() -> None:
    if SESSION_PATH.exists():
        SESSION_PATH.unlink()

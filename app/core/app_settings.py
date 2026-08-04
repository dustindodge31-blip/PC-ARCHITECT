"""Persists small local app preferences (currently: chosen accent theme)."""
import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).resolve().parent.parent / "data" / "app_settings.json"


def _load() -> dict:
    if not SETTINGS_PATH.exists():
        return {}
    try:
        return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    SETTINGS_PATH.write_text(json.dumps(data), encoding="utf-8")


def get_accent_id() -> str | None:
    return _load().get("accent_id")


def set_accent_id(accent_id: str) -> None:
    data = _load()
    data["accent_id"] = accent_id
    _save(data)


def get_display_name() -> str | None:
    return _load().get("display_name")


def set_display_name(name: str) -> None:
    data = _load()
    data["display_name"] = name
    _save(data)

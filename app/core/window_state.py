"""Persists the desktop test window's last screen position between runs."""
import json
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "window_state.json"


def load_position() -> tuple[float, float] | None:
    if not STATE_PATH.exists():
        return None
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return float(data["left"]), float(data["top"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


def save_position(left: float, top: float) -> None:
    STATE_PATH.write_text(json.dumps({"left": left, "top": top}), encoding="utf-8")

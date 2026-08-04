"""Local user profile (currently just a display name) persisted via app_settings."""
from core import app_settings

DEFAULT_NAME = "Builder"


def get_display_name() -> str:
    return app_settings.get_display_name() or DEFAULT_NAME


def set_display_name(name: str) -> None:
    app_settings.set_display_name(name.strip() or DEFAULT_NAME)


def greeting() -> str:
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 12:
        part = "morning"
    elif hour < 18:
        part = "afternoon"
    else:
        part = "evening"
    return f"Good {part}, {get_display_name()}"

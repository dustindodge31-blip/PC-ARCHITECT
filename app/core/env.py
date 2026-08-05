"""Locates and loads the project's .env file.

In dev, this file lives at app/core/env.py and .env sits at the project
root (three parents up). `flet build apk` packages everything under app/
as the root of the bundle, though, so once installed on a device this same
file is at core/env.py with .env needing to be alongside it (two parents
up) -- a copy is kept at app/.env (gitignored, must be kept in sync
manually) specifically so it gets bundled into the package.
"""
from pathlib import Path

from dotenv import load_dotenv

_HERE = Path(__file__).resolve()
_CANDIDATES = [
    _HERE.parent.parent.parent / ".env",  # dev: app/core/env.py -> project root
    _HERE.parent.parent / ".env",  # packaged: core/env.py -> bundle root
]
ENV_PATH = next((p for p in _CANDIDATES if p.exists()), _CANDIDATES[0])

load_dotenv(ENV_PATH)

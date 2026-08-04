"""Named accent-color palettes users can switch between (base dark theme stays fixed)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AccentTheme:
    id: str
    label: str
    primary: str
    secondary: str


RED_BLACK = AccentTheme(id="red_black", label="Red & Black", primary="#FF3B3B", secondary="#8C1A1A")
GREEN_BLACK = AccentTheme(id="green_black", label="Black & Green", primary="#3DDC64", secondary="#1F8A3C")
CYAN_PURPLE = AccentTheme(id="cyan_purple", label="Cyan & Purple", primary="#7C5CFF", secondary="#22D3EE")

ACCENT_THEMES = [RED_BLACK, GREEN_BLACK, CYAN_PURPLE]
DEFAULT_ACCENT = CYAN_PURPLE


def find_accent(accent_id: str) -> AccentTheme:
    for accent in ACCENT_THEMES:
        if accent.id == accent_id:
            return accent
    return DEFAULT_ACCENT

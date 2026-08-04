"""Dark, Material 3 theme for PC Architect. Base surface/text colors are fixed;
the accent color pair is swappable via core.accent_themes / core.app_settings."""
import flet as ft

from core import accent_themes, app_settings

BG = "#0E0E12"
SURFACE = "#17171E"
SURFACE_ALT = "#1F1F29"
BORDER = "#2A2A36"
TEXT_PRIMARY = "#F2F2F7"
TEXT_MUTED = "#9A9AA6"
SUCCESS = "#3DDC97"
WARNING = "#FFB454"
ERROR = "#FF5C5C"

# Mutable module-level accent state — read by other UI modules as theme.ACCENT /
# theme.ACCENT_SOFT at call time, so init_accent() must run before any screens build.
current_accent: accent_themes.AccentTheme = accent_themes.DEFAULT_ACCENT
ACCENT = current_accent.primary
ACCENT_SOFT = ft.Colors.with_opacity(0.16, current_accent.primary)


def init_accent() -> None:
    """Loads the persisted accent choice (if any) and applies it. Call once at startup."""
    saved_id = app_settings.get_accent_id()
    accent = accent_themes.find_accent(saved_id) if saved_id else accent_themes.DEFAULT_ACCENT
    set_accent(accent)


def set_accent(accent: accent_themes.AccentTheme) -> None:
    global current_accent, ACCENT, ACCENT_SOFT
    current_accent = accent
    ACCENT = accent.primary
    ACCENT_SOFT = ft.Colors.with_opacity(0.16, accent.primary)
    app_settings.set_accent_id(accent.id)


def build_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=ACCENT,
        color_scheme=ft.ColorScheme(
            primary=ACCENT,
            surface=SURFACE,
            on_surface=TEXT_PRIMARY,
        ),
        use_material3=True,
    )


def card(content: ft.Control, padding: int = 20) -> ft.Container:
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=16,
    )

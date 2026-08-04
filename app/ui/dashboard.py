"""Home dashboard: greeting, AI Architect entry, category filters, recent builds."""
import json
import flet as ft

from core import storage, catalog, compatibility, profile, scoring
from ui import theme
from ui.score_widgets import score_badge

CATEGORY_FILTERS = [
    ("Gaming", ft.Icons.SPORTS_ESPORTS_ROUNDED),
    ("Creator", ft.Icons.MOVIE_CREATION_ROUNDED),
    ("AI / Workstation", ft.Icons.PSYCHOLOGY_ROUNDED),
    ("Office", ft.Icons.WORK_ROUNDED),
    ("Custom", ft.Icons.TUNE_ROUNDED),
]


def _build_card(row: dict, on_open_build) -> ft.Control:
    selection_ids = json.loads(row["parts_json"])
    parts = {cat: (catalog.find_part(cat, pid) if pid else None) for cat, pid in selection_ids.items()}

    spec_bits = []
    for cat in ("cpu", "gpu", "ram"):
        part = parts.get(cat)
        if part:
            spec_bits.append(part["name"])
    spec_line = "  ·  ".join(spec_bits) if spec_bits else "No parts selected yet"

    thumbnail = ft.Container(
        width=52,
        height=52,
        border_radius=12,
        bgcolor=theme.SURFACE_ALT,
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.DEVELOPER_BOARD_ROUNDED, color=theme.TEXT_MUTED, size=26),
    )

    return ft.Container(
        content=ft.Row(
            [
                thumbnail,
                ft.Column(
                    [
                        ft.Text(row["name"], size=15, weight=ft.FontWeight.W_600),
                        ft.Text(spec_line, size=11, color=theme.TEXT_MUTED, max_lines=1),
                    ],
                    spacing=2,
                    expand=True,
                ),
                score_badge(scoring.overall_score(scoring.score_build(parts, compatibility.total_price(parts)))),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=12,
        bgcolor=theme.SURFACE,
        border=ft.Border.all(1, theme.BORDER),
        border_radius=14,
        on_click=lambda e: on_open_build(row) if on_open_build else None,
        ink=True,
    )


def build_dashboard(
    page: ft.Page,
    on_go_build_creator=None,
    on_go_ai=None,
    on_view_all_builds=None,
    on_open_build=None,
) -> ft.Control:
    builds = storage.list_builds()
    recent_builds = builds[:3]

    header_row = ft.Stack(
        [
            ft.Container(
                margin=ft.Margin.only(top=-22, left=0),
                alignment=ft.Alignment.CENTER_LEFT,
                content=ft.Image(src="header.png", fit=ft.BoxFit.CONTAIN, height=50),
            ),
            ft.Container(
                top=0,
                right=0,
                content=ft.Icon(ft.Icons.NOTIFICATIONS_NONE_ROUNDED, color=theme.TEXT_MUTED, size=20),
            ),
        ],
        height=68,
    )

    greeting_text = ft.Text(
        profile.greeting() + " \U0001F44B", size=14, color=theme.TEXT_MUTED, text_align=ft.TextAlign.CENTER
    )

    headline = ft.Text(
        spans=[
            ft.TextSpan("Let's build something ", ft.TextStyle(size=24, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY)),
            ft.TextSpan("amazing.", ft.TextStyle(size=24, weight=ft.FontWeight.BOLD, color=theme.ACCENT)),
        ],
        text_align=ft.TextAlign.CENTER,
    )

    ai_card = ft.Container(
        padding=16,
        bgcolor=theme.ACCENT_SOFT,
        border=ft.Border.all(1, theme.ACCENT),
        border_radius=20,
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("AI Architect", size=14, weight=ft.FontWeight.BOLD, color=theme.ACCENT),
                        ft.Text("Describe your dream PC...", size=12, color=theme.TEXT_MUTED),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Container(
                    width=36,
                    height=36,
                    border_radius=18,
                    bgcolor=theme.ACCENT,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color="#0E0E12", size=18),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        on_click=lambda e: on_go_ai() if on_go_ai else None,
        ink=True,
    )

    filter_row = ft.Row(
        [
            ft.Column(
                [
                    ft.Container(
                        width=48,
                        height=48,
                        border_radius=14,
                        bgcolor=theme.SURFACE,
                        border=ft.Border.all(1, theme.BORDER),
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(icon, size=20, color=theme.TEXT_PRIMARY),
                        on_click=lambda e: on_go_build_creator() if on_go_build_creator else None,
                        ink=True,
                    ),
                    ft.Text(label, size=10, color=theme.TEXT_MUTED),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            )
            for label, icon in CATEGORY_FILTERS
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    builds_header = ft.Row(
        [
            ft.Text("My Builds", size=16, weight=ft.FontWeight.W_600),
            ft.TextButton(
                "View all",
                on_click=lambda e: on_view_all_builds() if on_view_all_builds else None,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    if recent_builds:
        builds_list = ft.Column(
            [_build_card(row, on_open_build) for row in recent_builds],
            spacing=10,
        )
    else:
        builds_list = theme.card(
            ft.Row(
                [ft.Text("No saved builds yet. Start one below.", color=theme.TEXT_MUTED, text_align=ft.TextAlign.CENTER)],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    return ft.Column(
        [
            ft.Container(height=16),
            ft.Column(
                [header_row, greeting_text, headline],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            ft.Container(height=12),
            ai_card,
            ft.Container(height=8),
            filter_row,
            ft.Container(height=8),
            builds_header,
            builds_list,
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

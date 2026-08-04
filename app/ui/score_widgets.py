"""Reusable score-display widgets shared by the dashboard and Build Creator."""
import flet as ft

from ui import theme


def score_color(score: int) -> str:
    if score >= 85:
        return theme.SUCCESS
    if score >= 70:
        return theme.ACCENT
    if score >= 50:
        return theme.WARNING
    return theme.ACCENT


def score_badge(score: int, size: int = 44) -> ft.Control:
    color = score_color(score)
    return ft.Container(
        width=size,
        height=size,
        border_radius=size / 2,
        border=ft.Border.all(max(2, size // 15), color),
        alignment=ft.Alignment.CENTER,
        content=ft.Text(str(score), size=size * 0.32, weight=ft.FontWeight.BOLD, color=color),
    )


def score_bar(label: str, value: int) -> ft.Control:
    """A labeled horizontal meter. Filled portion is a flex-weighted Container
    (percent width isn't directly supported), so both segments share a Row."""
    color = score_color(value)
    filled = max(0, min(100, value))
    track_row = ft.Row(spacing=0, height=6)
    if filled > 0:
        track_row.controls.append(
            ft.Container(bgcolor=color, border_radius=3, height=6, expand=filled)
        )
    if filled < 100:
        track_row.controls.append(
            ft.Container(bgcolor=theme.SURFACE_ALT, border_radius=3, height=6, expand=100 - filled)
        )

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Text(label, size=12, color=theme.TEXT_MUTED),
                    ft.Text(str(value), size=12, weight=ft.FontWeight.W_600, color=color),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            track_row,
        ],
        spacing=4,
    )


def star_row(count: int, max_stars: int = 5, size: int = 14) -> ft.Control:
    return ft.Row(
        [
            ft.Icon(
                ft.Icons.STAR_ROUNDED if i < count else ft.Icons.STAR_BORDER_ROUNDED,
                size=size,
                color=theme.WARNING if i < count else theme.TEXT_MUTED,
            )
            for i in range(max_stars)
        ],
        spacing=2,
    )

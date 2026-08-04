"""Reusable 'coming soon' placeholder for features not built yet (see EPICS.md)."""
import flet as ft

from ui import theme


def build_stub_view(title: str, subtitle: str, icon: str) -> ft.Control:
    return ft.Column(
        [
            ft.Container(expand=True),
            ft.Icon(icon, size=48, color=theme.ACCENT),
            ft.Container(height=12),
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(subtitle, size=13, color=theme.TEXT_MUTED, text_align=ft.TextAlign.CENTER),
            ft.Container(expand=True),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

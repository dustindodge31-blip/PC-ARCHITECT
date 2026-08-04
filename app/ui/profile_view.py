"""Profile screen: local display name (used in the dashboard greeting)."""
import flet as ft

from core import profile
from ui import theme


def build_profile_view(page: ft.Page, on_name_saved=None) -> ft.Control:
    name_field = ft.TextField(
        label="Display name",
        value=profile.get_display_name(),
        width=280,
    )

    def save_name(e):
        profile.set_display_name(name_field.value or "")
        name_field.value = profile.get_display_name()
        page.update()
        if on_name_saved:
            on_name_saved()

    return ft.Column(
        [
            ft.Text("Profile", size=26, weight=ft.FontWeight.BOLD),
            theme.card(
                ft.Column(
                    [
                        ft.Text("How PC Architect greets you", color=theme.TEXT_MUTED, size=12),
                        name_field,
                        ft.ElevatedButton("Save", icon=ft.Icons.CHECK_ROUNDED, on_click=save_name),
                    ],
                    spacing=12,
                )
            ),
        ],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

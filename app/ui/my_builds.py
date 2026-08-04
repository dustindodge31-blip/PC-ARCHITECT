"""My Builds screen: list saved builds, open or delete them."""
import json
import flet as ft

from core import storage, catalog
from ui import theme


class MyBuildsView(ft.Column):
    def __init__(self, page: ft.Page, on_open_build=None):
        super().__init__(expand=True, spacing=16, scroll=ft.ScrollMode.AUTO)
        self.app_page = page
        self.on_open_build = on_open_build
        self.list_column = ft.Column(spacing=10)
        self.controls = [
            ft.Text("My Builds", size=26, weight=ft.FontWeight.BOLD),
            self.list_column,
        ]
        self.refresh()

    def refresh(self):
        builds = storage.list_builds()
        self.list_column.controls.clear()

        if not builds:
            self.list_column.controls.append(
                theme.card(
                    ft.Text("No saved builds yet. Create one in Build Creator.", color=theme.TEXT_MUTED)
                )
            )
        else:
            for row in builds:
                selection_ids = json.loads(row["parts_json"])
                total = 0.0
                for cat, part_id in selection_ids.items():
                    part = catalog.find_part(cat, part_id) if part_id else None
                    if part:
                        total += part["price"]

                self.list_column.controls.append(
                    theme.card(
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(row["name"], size=16, weight=ft.FontWeight.W_600),
                                        ft.Text(f"${total:,.2f}  ·  updated {row['updated_at'][:10]}",
                                                color=theme.TEXT_MUTED, size=12),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
                                    tooltip="Open in Build Creator",
                                    on_click=lambda e, r=row: self._open(r),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                    icon_color=theme.ERROR,
                                    tooltip="Delete",
                                    on_click=lambda e, r=row: self._delete(r),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=16,
                    )
                )

        try:
            self.update()
        except RuntimeError:
            pass  # not mounted yet (e.g. still in __init__)

    def _open(self, row: dict):
        if self.on_open_build:
            self.on_open_build(row)

    def _delete(self, row: dict):
        storage.delete_build(row["id"])
        self.refresh()

"""Prices screen: wishlist parts and browse the catalog with simulated price stats."""
import flet as ft

from core import catalog, price_history, storage
from ui import theme


class PricesView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=16, scroll=ft.ScrollMode.AUTO)
        self.app_page = page
        self.tab_index = 0  # 0 = wishlist, 1 = browse all

        self.wishlist_toggle: ft.Container | None = None
        self.browse_toggle: ft.Container | None = None
        self.list_column = ft.Column(spacing=10)

        self.controls = [
            ft.Text("Prices", size=26, weight=ft.FontWeight.BOLD),
            self._segmented_toggle(),
            self.list_column,
        ]
        self.refresh()

    # ---------- layout ----------

    def _segmented_toggle(self) -> ft.Control:
        def make_option(label: str, index: int) -> ft.Container:
            def on_click(e):
                self.tab_index = index
                self._style_toggle()
                self.refresh()

            return ft.Container(
                content=ft.Text(label, size=13, weight=ft.FontWeight.W_600),
                padding=ft.Padding.symmetric(vertical=8, horizontal=0),
                alignment=ft.Alignment.CENTER,
                expand=True,
                border_radius=12,
                on_click=on_click,
                ink=True,
            )

        self.wishlist_toggle = make_option("Wishlist", 0)
        self.browse_toggle = make_option("Browse All", 1)
        self._style_toggle()

        return ft.Container(
            padding=4,
            bgcolor=theme.SURFACE,
            border=ft.Border.all(1, theme.BORDER),
            border_radius=16,
            content=ft.Row([self.wishlist_toggle, self.browse_toggle], spacing=4),
        )

    def _style_toggle(self):
        for index, container in ((0, self.wishlist_toggle), (1, self.browse_toggle)):
            active = index == self.tab_index
            container.bgcolor = theme.ACCENT_SOFT if active else None
            container.content.color = theme.ACCENT if active else theme.TEXT_MUTED

    def _part_row(self, category: str, part: dict, wishlisted: bool) -> ft.Control:
        stats = price_history.price_stats(part["id"], part["price"])
        good_deal = price_history.is_good_time_to_buy(stats)

        def toggle_wishlist(e):
            if wishlisted:
                storage.remove_from_wishlist(category, part["id"])
            else:
                storage.add_to_wishlist(category, part["id"])
            self.refresh()

        info_column = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(part["name"], size=14, weight=ft.FontWeight.W_600, expand=True),
                        ft.Text(f"${stats['current']:,.2f}", size=14, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    f"Low ${stats['lowest']:,.2f}  ·  High ${stats['highest']:,.2f}  ·  Avg ${stats['average']:,.2f}",
                    size=11,
                    color=theme.TEXT_MUTED,
                ),
                ft.Container(
                    content=ft.Text("Price Drop", size=10, weight=ft.FontWeight.BOLD, color=theme.SUCCESS),
                    padding=ft.Padding.symmetric(vertical=2, horizontal=8),
                    bgcolor=ft.Colors.with_opacity(0.16, theme.SUCCESS),
                    border_radius=10,
                    visible=good_deal,
                ) if good_deal else ft.Container(height=0),
            ],
            spacing=4,
            expand=True,
        )

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=36,
                        height=36,
                        border_radius=10,
                        bgcolor=theme.ACCENT_SOFT,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(theme.CATEGORY_ICONS[category], size=18, color=theme.ACCENT),
                    ),
                    info_column,
                    ft.IconButton(
                        icon=ft.Icons.STAR_ROUNDED if wishlisted else ft.Icons.STAR_BORDER_ROUNDED,
                        icon_color=theme.WARNING if wishlisted else theme.TEXT_MUTED,
                        on_click=toggle_wishlist,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=12,
            bgcolor=theme.SURFACE,
            border=ft.Border.all(1, theme.BORDER),
            border_radius=14,
        )

    def refresh(self):
        self.list_column.controls.clear()

        if self.tab_index == 0:
            wishlist_rows = storage.list_wishlist()
            if not wishlist_rows:
                self.list_column.controls.append(
                    theme.card(
                        ft.Text(
                            "No wishlisted parts yet. Star parts in Browse All to track their prices.",
                            color=theme.TEXT_MUTED,
                        )
                    )
                )
            else:
                for entry in wishlist_rows:
                    part = catalog.find_part(entry["category"], entry["part_id"])
                    if part:
                        self.list_column.controls.append(
                            self._part_row(entry["category"], part, wishlisted=True)
                        )
        else:
            for cat in catalog.CATEGORIES:
                self.list_column.controls.append(
                    ft.Text(catalog.CATEGORY_LABELS[cat], size=14, weight=ft.FontWeight.W_600)
                )
                for part in catalog.parts_for(cat):
                    wishlisted = storage.is_wishlisted(cat, part["id"])
                    self.list_column.controls.append(self._part_row(cat, part, wishlisted))

        self._safe_update()

    def _safe_update(self):
        try:
            self.update()
        except RuntimeError:
            pass  # not mounted yet (e.g. still in __init__)

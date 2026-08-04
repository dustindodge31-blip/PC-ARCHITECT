"""Community screen: browse published builds, favorite them, and publish
your own local builds. Reached from Profile — no dedicated nav tab."""
import flet as ft

from core import community, compatibility, profile, scoring, storage
from ui import theme
from ui.score_widgets import score_badge


class CommunityView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=16, scroll=ft.ScrollMode.AUTO)
        self.app_page = page
        self.error_text = ft.Text("", color=theme.ERROR, size=12, visible=False)
        self.feed_column = ft.Column(spacing=10)
        self.publish_column = ft.Column(spacing=10)

        self.controls = [
            ft.Text("Community", size=26, weight=ft.FontWeight.BOLD),
            self.error_text,
            ft.Text("Publish a build", size=14, weight=ft.FontWeight.W_600),
            self.publish_column,
            ft.Divider(color=theme.BORDER),
            ft.Text("Feed", size=14, weight=ft.FontWeight.W_600),
            self.feed_column,
        ]
        self.refresh()

    def refresh(self):
        self.error_text.visible = False
        self._refresh_publish_section()
        self._refresh_feed()
        self._safe_update()

    def _refresh_publish_section(self):
        self.publish_column.controls.clear()
        local_builds = storage.list_builds()
        if not local_builds:
            self.publish_column.controls.append(
                ft.Text("Save a build in Build Creator first, then publish it here.", color=theme.TEXT_MUTED, size=12)
            )
            return

        for row in local_builds:
            self.publish_column.controls.append(
                ft.Row(
                    [
                        ft.Text(row["name"], size=13, expand=True),
                        ft.TextButton(
                            "Publish",
                            icon=ft.Icons.CLOUD_UPLOAD_ROUNDED,
                            on_click=lambda e, r=row: self._publish(r),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )

    def _publish(self, row: dict):
        import json
        from core import catalog

        selection_ids = json.loads(row["parts_json"])
        parts = {cat: (catalog.find_part(cat, pid) if pid else None) for cat, pid in selection_ids.items()}
        total = compatibility.total_price(parts)
        overall = scoring.overall_score(scoring.score_build(parts, total))

        try:
            community.publish_build(row["name"], parts, total, overall, profile.get_display_name())
        except community.CommunityError as ex:
            self.error_text.value = str(ex)
            self.error_text.visible = True
            self._safe_update()
            return

        self.refresh()

    def _refresh_feed(self):
        self.feed_column.controls.clear()
        try:
            builds = community.list_community_builds()
        except community.CommunityError as ex:
            self.error_text.value = str(ex)
            self.error_text.visible = True
            return

        if not builds:
            self.feed_column.controls.append(
                theme.card(ft.Text("No builds published yet. Be the first!", color=theme.TEXT_MUTED))
            )
            return

        for build in builds:
            self.feed_column.controls.append(self._feed_card(build))

    def _feed_card(self, build) -> ft.Control:
        def toggle(e):
            try:
                community.toggle_favorite(build.id, build.favorited_by_me)
            except community.CommunityError as ex:
                self.error_text.value = str(ex)
                self.error_text.visible = True
                self._safe_update()
                return
            self.refresh()

        return ft.Container(
            content=ft.Row(
                [
                    score_badge(build.overall_score, size=44),
                    ft.Column(
                        [
                            ft.Text(build.name, size=14, weight=ft.FontWeight.W_600),
                            ft.Text(f"by {build.author_name}  ·  ${build.price:,.2f}", size=11, color=theme.TEXT_MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Column(
                        [
                            ft.IconButton(
                                icon=ft.Icons.FAVORITE_ROUNDED if build.favorited_by_me else ft.Icons.FAVORITE_BORDER_ROUNDED,
                                icon_color=theme.ERROR if build.favorited_by_me else theme.TEXT_MUTED,
                                on_click=toggle,
                            ),
                            ft.Text(str(build.favorite_count), size=11, color=theme.TEXT_MUTED),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=12,
            bgcolor=theme.SURFACE,
            border=ft.Border.all(1, theme.BORDER),
            border_radius=14,
        )

    def _safe_update(self):
        try:
            self.update()
        except RuntimeError:
            pass  # not mounted yet (e.g. still in __init__)

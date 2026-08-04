"""PC Architect — Flet desktop entry point (phone-sized window for Android preview)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import flet as ft

from core import storage, window_state
from ui import theme
from ui.dashboard import build_dashboard
from ui.build_creator import BuildCreatorView
from ui.my_builds import MyBuildsView
from ui.profile_view import ProfileView
from ui.ai_view import AIArchitectView
from ui.prices_view import PricesView
from ui.community_view import CommunityView
from ui.phone_frame import wrap_in_phone_frame

PHONE_WIDTH = 402
PHONE_HEIGHT = 874


async def main(page: ft.Page):
    storage.init_db()
    theme.init_accent()

    page.title = "PC Architect"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = theme.build_theme()
    page.bgcolor = ft.Colors.TRANSPARENT
    page.padding = 0

    # Phone-shaped, frameless, transparent window so desktop testing feels like a real device.
    page.window.width = PHONE_WIDTH
    page.window.height = PHONE_HEIGHT
    page.window.resizable = False
    page.window.maximizable = False
    page.window.frameless = True
    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.window.shadow = True
    page.update()  # flush size before positioning, so center()/left/top see the real dimensions

    # Restore last position if we have one, otherwise center on first run.
    saved_position = window_state.load_position()
    if saved_position:
        page.window.left, page.window.top = saved_position
        page.update()
    else:
        await page.window.center()

    def on_window_event(e: ft.WindowEvent):
        if e.type == ft.WindowEventType.MOVED:
            window_state.save_position(page.window.left, page.window.top)

    page.window.on_event = on_window_event

    body = ft.Container(expand=True, padding=20)

    def open_build_in_creator(row):
        show_build_creator()
        build_creator_view.load_build(row)
        page.update()

    def open_ai_build_in_creator(name, selection, reasoning):
        show_build_creator()
        build_creator_view.load_from_parts(name, selection, reasoning)
        page.update()

    def show_dashboard():
        body.content = build_dashboard(
            page,
            on_go_build_creator=lambda: set_index(1),
            on_go_ai=lambda: set_index(2),
            on_view_all_builds=show_my_builds_list,
            on_open_build=open_build_in_creator,
        )
        nav.selected_index = 0
        page.update()

    def show_build_creator():
        nonlocal build_creator_view
        if build_creator_view is None:
            build_creator_view = BuildCreatorView(page, on_saved=lambda: None)
        body.content = build_creator_view
        nav.selected_index = 1
        page.update()

    def show_my_builds_list():
        """Reached from the dashboard's 'View all' link and from build cards — not its own nav tab."""
        my_builds_view.on_open_build = open_build_in_creator
        my_builds_view.refresh()
        body.content = my_builds_view
        nav.selected_index = 1
        page.update()

    def show_ai_architect():
        body.content = ai_view
        nav.selected_index = 2
        page.update()

    def show_prices():
        prices_view.refresh()
        body.content = prices_view
        nav.selected_index = 3
        page.update()

    def show_community():
        community_view.refresh()
        body.content = community_view
        nav.selected_index = 4
        page.update()

    def show_profile():
        profile_view.refresh()
        body.content = profile_view
        nav.selected_index = 4
        page.update()

    build_creator_view: BuildCreatorView | None = None
    my_builds_view = MyBuildsView(page)
    ai_view = AIArchitectView(page, on_build_generated=open_ai_build_in_creator)
    prices_view = PricesView(page)
    community_view = CommunityView(page)
    profile_view = ProfileView(page, on_name_saved=lambda: None, on_browse_community=show_community)

    views = [show_dashboard, show_build_creator, show_ai_architect, show_prices, show_profile]

    def set_index(i: int):
        views[i]()

    def on_nav_change(e):
        set_index(e.control.selected_index)

    nav = ft.NavigationBar(
        selected_index=0,
        bgcolor=theme.SURFACE,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_ROUNDED, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.BUILD_ROUNDED, label="Builds"),
            ft.NavigationBarDestination(icon=ft.Icons.AUTO_AWESOME_ROUNDED, label="AI"),
            ft.NavigationBarDestination(icon=ft.Icons.TRENDING_DOWN_ROUNDED, label="Prices"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_ROUNDED, label="Profile"),
        ],
    )

    page.add(
        wrap_in_phone_frame(
            page,
            ft.Column([body, nav], expand=True, spacing=0),
        )
    )

    show_dashboard()


if __name__ == "__main__":
    ft.run(main)

"""Phone-like chrome for the desktop test window: bezel, notch, status bar, home indicator."""
import asyncio
from datetime import datetime

import flet as ft

from ui import theme

BEZEL_THICKNESS = 10
OUTER_RADIUS = 46
INNER_RADIUS = 36
STATUS_BAR_HEIGHT = 34
NOTCH_WIDTH = 90
NOTCH_HEIGHT = 22


def _format_time() -> str:
    now = datetime.now()
    hour = now.hour % 12 or 12
    return f"{hour}:{now.minute:02d}"


def build_status_bar(page: ft.Page) -> ft.Control:
    time_text = ft.Text(_format_time(), size=13, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY)

    async def clock_loop():
        while True:
            await asyncio.sleep(20)
            time_text.value = _format_time()
            page.update()

    page.run_task(clock_loop)

    def start_drag(e: ft.DragStartEvent):
        page.window.start_dragging()

    drag_surface = ft.GestureDetector(
        on_pan_start=start_drag,
        content=ft.Container(expand=True),
    )

    icons_row = ft.Row(
        [
            ft.Icon(ft.Icons.SIGNAL_CELLULAR_ALT_ROUNDED, size=14, color=theme.TEXT_PRIMARY),
            ft.Icon(ft.Icons.WIFI_ROUNDED, size=14, color=theme.TEXT_PRIMARY),
            ft.Icon(ft.Icons.BATTERY_FULL_ROUNDED, size=16, color=theme.TEXT_PRIMARY),
        ],
        spacing=4,
    )

    content_row = ft.Container(
        padding=ft.Padding.symmetric(vertical=0, horizontal=20),
        content=ft.Row(
            [time_text, icons_row],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        height=STATUS_BAR_HEIGHT,
        alignment=ft.Alignment.CENTER,
    )

    notch = ft.Container(
        width=NOTCH_WIDTH,
        height=NOTCH_HEIGHT,
        bgcolor="#000000",
        border_radius=14,
        top=6,
        left=0,
        right=0,
    )

    return ft.Container(
        height=STATUS_BAR_HEIGHT,
        content=ft.Stack([drag_surface, content_row, notch], expand=True),
    )


def build_home_indicator() -> ft.Control:
    return ft.Container(
        height=22,
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=120,
            height=4,
            bgcolor=theme.TEXT_MUTED,
            border_radius=2,
            opacity=0.5,
        ),
    )


def build_close_button(page: ft.Page) -> ft.Control:
    async def close_app(e):
        await page.window.close()

    return ft.Container(
        top=2,
        right=2,
        content=ft.IconButton(
            icon=ft.Icons.CLOSE_ROUNDED,
            icon_size=14,
            icon_color="#666666",
            on_click=close_app,
            style=ft.ButtonStyle(padding=4),
        ),
    )


def wrap_in_phone_frame(page: ft.Page, screen_content: ft.Control) -> ft.Control:
    """Wraps app content in a rounded bezel + status bar + home indicator, and
    makes the (frameless) window draggable and closable."""
    inner_screen = ft.Container(
        expand=True,
        bgcolor=theme.BG,
        border_radius=INNER_RADIUS,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            [build_status_bar(page), screen_content, build_home_indicator()],
            spacing=0,
            expand=True,
        ),
    )

    return ft.Stack(
        [
            ft.Container(
                expand=True,
                bgcolor="#000000",
                border_radius=OUTER_RADIUS,
                padding=BEZEL_THICKNESS,
                content=inner_screen,
            ),
            build_close_button(page),
        ],
        expand=True,
    )

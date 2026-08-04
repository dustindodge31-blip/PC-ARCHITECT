"""Build Creator screen: Overview tab (score + meters) and Parts tab (pickers),
sharing a persistent bottom bar (compatibility, price, power, save)."""
import flet as ft

from core import catalog, compatibility, storage, scoring, performance
from ui import theme
from ui.score_widgets import score_badge, score_bar, star_row

CATEGORY_ICONS = theme.CATEGORY_ICONS


class BuildCreatorView(ft.Column):
    def __init__(self, page: ft.Page, on_saved=None):
        super().__init__(expand=True, spacing=16, scroll=ft.ScrollMode.AUTO)
        self.app_page = page
        self.on_saved = on_saved
        self.build_id: int | None = None
        self.build_name = "Untitled Build"
        self.selected: dict[str, dict | None] = {c: None for c in catalog.CATEGORIES}
        self.tab_index = 0

        self.dropdowns: dict[str, ft.Dropdown] = {}
        self.name_field = ft.TextField(
            value=self.build_name,
            label="Build name",
            width=320,
            on_change=self._on_name_change,
        )
        self.price_text = ft.Text("$0.00", size=22, weight=ft.FontWeight.BOLD)
        self.power_text = ft.Text("Est. draw: 0W", color=theme.TEXT_MUTED, size=12)
        self.issues_column = ft.Column(spacing=8)
        self.status_chip = ft.Container(
            content=ft.Text("No issues", color=theme.SUCCESS, weight=ft.FontWeight.BOLD),
            padding=ft.Padding.symmetric(vertical=8, horizontal=14),
            bgcolor=theme.ACCENT_SOFT,
            border_radius=20,
        )

        # Overview tab pieces, updated in place by _recalculate().
        self.badge_slot = ft.Container()
        self.stars_slot = ft.Container()
        self.tier_text = ft.Text("", size=13, weight=ft.FontWeight.BOLD, color=theme.TEXT_MUTED)
        self.score_bars_column = ft.Column(spacing=12)
        self.reasoning_card = ft.Container(visible=False)

        # Performance tab state.
        self.perf_game_id = performance.GAMES[0]["id"]
        self.perf_resolution = "1080p"
        self.perf_settings = "High"
        self.perf_ray_tracing = False
        self.perf_upscaling = "Off"
        self.perf_frame_gen = False
        self.fps_text = ft.Text("0 FPS", size=32, weight=ft.FontWeight.BOLD)
        self.bottleneck_column = ft.Column(spacing=10)

        self.overview_tab = ft.Container(visible=True, content=self._build_overview())
        self.parts_tab = ft.Container(visible=False, content=self._build_parts())
        self.performance_tab = ft.Container(visible=False, content=self._build_performance())
        self.overview_toggle: ft.Container | None = None
        self.parts_toggle: ft.Container | None = None
        self.performance_toggle: ft.Container | None = None

        self.controls = self._build_layout()
        self._recalculate()

    # ---------- layout ----------

    def _segmented_toggle(self) -> ft.Control:
        def make_option(label: str, index: int) -> ft.Container:
            def on_click(e):
                self._set_tab(index)

            container = ft.Container(
                content=ft.Text(label, size=13, weight=ft.FontWeight.W_600),
                padding=ft.Padding.symmetric(vertical=8, horizontal=0),
                alignment=ft.Alignment.CENTER,
                expand=True,
                border_radius=12,
                on_click=on_click,
                ink=True,
            )
            return container

        self.overview_toggle = make_option("Overview", 0)
        self.parts_toggle = make_option("Parts", 1)
        self.performance_toggle = make_option("Performance", 2)
        self._style_toggle()

        return ft.Container(
            padding=4,
            bgcolor=theme.SURFACE,
            border=ft.Border.all(1, theme.BORDER),
            border_radius=16,
            content=ft.Row(
                [self.overview_toggle, self.parts_toggle, self.performance_toggle], spacing=4
            ),
        )

    def _style_toggle(self):
        toggles = ((0, self.overview_toggle), (1, self.parts_toggle), (2, self.performance_toggle))
        for index, container in toggles:
            active = index == self.tab_index
            container.bgcolor = theme.ACCENT_SOFT if active else None
            container.content.color = theme.ACCENT if active else theme.TEXT_MUTED

    def _set_tab(self, index: int):
        self.tab_index = index
        self.overview_tab.visible = index == 0
        self.parts_tab.visible = index == 1
        self.performance_tab.visible = index == 2
        self._style_toggle()
        self._safe_update()

    def _build_overview(self) -> ft.Control:
        thumbnail = ft.Container(
            height=140,
            border_radius=16,
            bgcolor=theme.SURFACE_ALT,
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(ft.Icons.DEVELOPER_BOARD_ROUNDED, color=theme.TEXT_MUTED, size=56),
        )

        score_header = ft.Row(
            [
                self.badge_slot,
                ft.Column(
                    [self.tier_text, self.stars_slot],
                    spacing=4,
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Column(
            [
                self.reasoning_card,
                thumbnail,
                score_header,
                ft.Divider(color=theme.BORDER),
                self.score_bars_column,
            ],
            spacing=16,
        )

    def _build_parts(self) -> ft.Control:
        rows = []
        for cat in catalog.CATEGORIES:
            dd = ft.Dropdown(
                label=catalog.CATEGORY_LABELS[cat],
                options=[
                    ft.dropdown.Option(key=p["id"], text=f"{p['name']}  —  ${p['price']:.0f}")
                    for p in catalog.parts_for(cat)
                ],
                expand=True,
                on_select=lambda e, c=cat: self._on_select(c, e.control.value),
            )
            self.dropdowns[cat] = dd
            rows.append(
                ft.Row(
                    [
                        ft.Container(
                            width=36,
                            height=36,
                            border_radius=10,
                            bgcolor=theme.ACCENT_SOFT,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(CATEGORY_ICONS[cat], size=18, color=theme.ACCENT),
                        ),
                        dd,
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        return ft.Column(rows, spacing=14)

    def _build_performance(self) -> ft.Control:
        game_dd = ft.Dropdown(
            label="Game",
            value=self.perf_game_id,
            options=[ft.dropdown.Option(key=g["id"], text=g["name"]) for g in performance.GAMES],
            expand=True,
            on_select=lambda e: self._on_perf_change("perf_game_id", e.control.value),
        )
        resolution_dd = ft.Dropdown(
            label="Resolution",
            value=self.perf_resolution,
            options=[ft.dropdown.Option(key=r, text=r) for r in performance.RESOLUTIONS],
            expand=True,
            on_select=lambda e: self._on_perf_change("perf_resolution", e.control.value),
        )
        settings_dd = ft.Dropdown(
            label="Settings",
            value=self.perf_settings,
            options=[ft.dropdown.Option(key=s, text=s) for s in performance.SETTINGS_PRESETS],
            expand=True,
            on_select=lambda e: self._on_perf_change("perf_settings", e.control.value),
        )
        upscaling_dd = ft.Dropdown(
            label="Upscaling",
            value=self.perf_upscaling,
            options=[ft.dropdown.Option(key=u, text=u) for u in performance.UPSCALING_MODES],
            expand=True,
            on_select=lambda e: self._on_perf_change("perf_upscaling", e.control.value),
        )
        rt_switch = ft.Row(
            [ft.Text("Ray Tracing", size=13), ft.Switch(
                value=self.perf_ray_tracing,
                on_change=lambda e: self._on_perf_change("perf_ray_tracing", e.control.value),
            )],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        fg_switch = ft.Row(
            [ft.Text("Frame Generation", size=13), ft.Switch(
                value=self.perf_frame_gen,
                on_change=lambda e: self._on_perf_change("perf_frame_gen", e.control.value),
            )],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        return ft.Column(
            [
                ft.Row([game_dd], spacing=10),
                ft.Row([resolution_dd, settings_dd], spacing=10),
                upscaling_dd,
                rt_switch,
                fg_switch,
                ft.Divider(color=theme.BORDER),
                ft.Column(
                    [ft.Text("Estimated FPS", size=12, color=theme.TEXT_MUTED), self.fps_text],
                    spacing=2,
                ),
                ft.Divider(color=theme.BORDER),
                ft.Text("Bottleneck Analysis", size=14, weight=ft.FontWeight.W_600),
                self.bottleneck_column,
            ],
            spacing=14,
        )

    def _build_layout(self) -> list[ft.Control]:
        bottom_bar = theme.card(
            ft.Column(
                [
                    ft.Row(
                        [self.price_text, self.power_text],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                    ),
                    self.status_chip,
                    self.issues_column,
                    ft.Divider(color=theme.BORDER),
                    self.name_field,
                    ft.ElevatedButton(
                        "Save Build",
                        icon=ft.Icons.SAVE_ROUNDED,
                        on_click=self._on_save_click,
                    ),
                ],
                spacing=12,
            ),
            padding=20,
        )

        return [
            ft.Text("Build Creator", size=26, weight=ft.FontWeight.BOLD),
            self._segmented_toggle(),
            theme.card(ft.Column([self.overview_tab, self.parts_tab, self.performance_tab])),
            bottom_bar,
        ]

    # ---------- state ----------

    def _on_name_change(self, e):
        self.build_name = e.control.value

    def _on_select(self, category: str, part_id: str | None):
        self.selected[category] = catalog.find_part(category, part_id) if part_id else None
        self._recalculate()

    def _on_perf_change(self, attr: str, value):
        setattr(self, attr, value)
        self._recalculate_performance()
        self._safe_update()

    def _recalculate(self):
        total = compatibility.total_price(self.selected)
        draw = compatibility.estimate_power_draw(self.selected)
        issues = compatibility.check_build(self.selected)

        self.price_text.value = f"${total:,.2f}"
        self.power_text.value = f"Est. draw: {draw:.0f}W"

        axis_scores = scoring.score_build(self.selected, total)
        overall = scoring.overall_score(axis_scores)

        self.badge_slot.content = score_badge(overall, size=64)
        self.stars_slot.content = star_row(scoring.score_stars(overall))
        tier_color = theme.SUCCESS if overall >= 75 else theme.ACCENT if overall >= 50 else theme.TEXT_MUTED
        self.tier_text.value = scoring.score_tier(overall) if overall > 0 else "No parts yet"
        self.tier_text.color = tier_color

        self.score_bars_column.controls = [
            score_bar(scoring.AXIS_LABELS[axis], axis_scores[axis]) for axis in scoring.AXES
        ]

        self.issues_column.controls.clear()
        for issue in issues:
            color = theme.ERROR if issue.level == "error" else theme.WARNING
            icon = ft.Icons.ERROR_ROUNDED if issue.level == "error" else ft.Icons.WARNING_AMBER_ROUNDED
            self.issues_column.controls.append(
                ft.Row(
                    [ft.Icon(icon, color=color, size=18), ft.Text(issue.message, color=color, size=13, expand=True)],
                    spacing=8,
                )
            )

        errors = [i for i in issues if i.level == "error"]
        warnings = [i for i in issues if i.level == "warning"]
        if errors:
            self.status_chip.content = ft.Text(
                f"{len(errors)} compatibility error(s)", color=theme.ERROR, weight=ft.FontWeight.BOLD
            )
        elif warnings:
            self.status_chip.content = ft.Text(
                f"{len(warnings)} warning(s)", color=theme.WARNING, weight=ft.FontWeight.BOLD
            )
        else:
            self.status_chip.content = ft.Text("No issues", color=theme.SUCCESS, weight=ft.FontWeight.BOLD)

        self._recalculate_performance()
        self._safe_update()

    def _recalculate_performance(self):
        fps = performance.estimate_fps(
            self.selected,
            self.perf_game_id,
            self.perf_resolution,
            self.perf_settings,
            self.perf_ray_tracing,
            self.perf_upscaling,
            self.perf_frame_gen,
        )
        self.fps_text.value = f"{fps} FPS" if fps > 0 else "— FPS"

        self.bottleneck_column.controls.clear()
        insights = performance.analyze_bottleneck(self.selected)
        if not insights:
            self.bottleneck_column.controls.append(
                ft.Text("No bottlenecks detected.", size=12, color=theme.SUCCESS)
            )
        for insight in insights:
            color = theme.ERROR if insight.severity == "error" else theme.WARNING
            icon = ft.Icons.ERROR_ROUNDED if insight.severity == "error" else ft.Icons.WARNING_AMBER_ROUNDED
            self.bottleneck_column.controls.append(
                ft.Column(
                    [
                        ft.Row(
                            [ft.Icon(icon, color=color, size=18), ft.Text(insight.title, color=color, weight=ft.FontWeight.BOLD, size=13)],
                            spacing=8,
                        ),
                        ft.Text(f"Why: {insight.why}", size=11, color=theme.TEXT_MUTED),
                        ft.Text(f"Impact: {insight.impact}", size=11, color=theme.TEXT_MUTED),
                        ft.Text(f"Fix: {insight.fix}", size=11, color=theme.TEXT_MUTED),
                    ],
                    spacing=3,
                )
            )

    def _safe_update(self):
        try:
            self.update()
        except RuntimeError:
            pass  # not mounted yet (e.g. still in __init__)

    def _on_save_click(self, e):
        name = self.build_name.strip() or "Untitled Build"
        self.build_id = storage.save_build(name, self.selected, self.build_id)
        self.app_page.open(
            ft.SnackBar(content=ft.Text(f"Saved “{name}”"), bgcolor=theme.SURFACE_ALT)
        )
        if self.on_saved:
            self.on_saved()

    def load_build(self, build_row: dict):
        import json
        self.build_id = build_row["id"]
        self.build_name = build_row["name"]
        self.name_field.value = self.build_name
        selection_ids = json.loads(build_row["parts_json"])
        for cat in catalog.CATEGORIES:
            part_id = selection_ids.get(cat)
            self.selected[cat] = catalog.find_part(cat, part_id) if part_id else None
            self.dropdowns[cat].value = part_id
        self._set_reasoning(None)
        self._recalculate()

    def load_from_parts(self, name: str, parts: dict, reasoning: str | None = None):
        """Loads an unsaved build (e.g. from AI Architect) — not yet in storage."""
        self.build_id = None
        self.build_name = name
        self.name_field.value = name
        for cat in catalog.CATEGORIES:
            part = parts.get(cat)
            self.selected[cat] = part
            self.dropdowns[cat].value = part["id"] if part else None
        self._set_reasoning(reasoning)
        self._set_tab(0)
        self._recalculate()

    def _set_reasoning(self, reasoning: str | None):
        if reasoning:
            self.reasoning_card.visible = True
            self.reasoning_card.bgcolor = theme.ACCENT_SOFT
            self.reasoning_card.border_radius = 14
            self.reasoning_card.padding = 12
            self.reasoning_card.content = ft.Row(
                [
                    ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=theme.ACCENT, size=18),
                    ft.Text(reasoning, size=12, color=theme.TEXT_MUTED, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE_ROUNDED,
                        icon_size=14,
                        on_click=lambda e: self._dismiss_reasoning(),
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        else:
            self.reasoning_card.visible = False

    def _dismiss_reasoning(self):
        self.reasoning_card.visible = False
        self._safe_update()

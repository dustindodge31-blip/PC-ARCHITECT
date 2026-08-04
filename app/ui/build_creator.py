"""Build Creator screen: pick components, see live compatibility + totals."""
import flet as ft

from core import catalog, compatibility, storage
from ui import theme


class BuildCreatorView(ft.Column):
    def __init__(self, page: ft.Page, on_saved=None):
        super().__init__(expand=True, spacing=16, scroll=ft.ScrollMode.AUTO)
        self.app_page = page
        self.on_saved = on_saved
        self.build_id: int | None = None
        self.build_name = "Untitled Build"
        self.selected: dict[str, dict | None] = {c: None for c in catalog.CATEGORIES}

        self.dropdowns: dict[str, ft.Dropdown] = {}
        self.name_field = ft.TextField(
            value=self.build_name,
            label="Build name",
            width=320,
            on_change=self._on_name_change,
        )
        self.price_text = ft.Text("$0.00", size=28, weight=ft.FontWeight.BOLD)
        self.power_text = ft.Text("Estimated draw: 0W", color=theme.TEXT_MUTED)
        self.issues_column = ft.Column(spacing=8)
        self.status_chip = ft.Container(
            content=ft.Text("No issues", color=theme.SUCCESS, weight=ft.FontWeight.BOLD),
            padding=ft.Padding.symmetric(vertical=8, horizontal=14),
            bgcolor=theme.ACCENT_SOFT,
            border_radius=20,
        )

        self.controls = self._build_layout()
        self._recalculate()

    def _build_layout(self) -> list[ft.Control]:
        picker_rows = []
        for cat in catalog.CATEGORIES:
            dd = ft.Dropdown(
                label=catalog.CATEGORY_LABELS[cat],
                options=[
                    ft.dropdown.Option(key=p["id"], text=f"{p['name']}  —  ${p['price']:.0f}")
                    for p in catalog.parts_for(cat)
                ],
                expand=True,
                on_change=lambda e, c=cat: self._on_select(c, e.control.value),
            )
            self.dropdowns[cat] = dd
            picker_rows.append(dd)

        pickers_card = theme.card(
            ft.Column(
                [
                    ft.Text("Components", size=18, weight=ft.FontWeight.W_600),
                    *picker_rows,
                ],
                spacing=14,
            )
        )

        summary_card = theme.card(
            ft.Column(
                [
                    ft.Text("Summary", size=18, weight=ft.FontWeight.W_600),
                    self.price_text,
                    self.power_text,
                    ft.Divider(color=theme.BORDER),
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
            ft.ResponsiveRow(
                [
                    ft.Container(pickers_card, col={"sm": 12, "md": 7}),
                    ft.Container(summary_card, col={"sm": 12, "md": 5}),
                ],
            ),
        ]

    def _on_name_change(self, e):
        self.build_name = e.control.value

    def _on_select(self, category: str, part_id: str | None):
        self.selected[category] = catalog.find_part(category, part_id) if part_id else None
        self._recalculate()

    def _recalculate(self):
        total = compatibility.total_price(self.selected)
        draw = compatibility.estimate_power_draw(self.selected)
        issues = compatibility.check_build(self.selected)

        self.price_text.value = f"${total:,.2f}"
        self.power_text.value = f"Estimated draw: {draw:.0f}W"

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
        self._recalculate()

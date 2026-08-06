"""AI Architect screen: describe a build in plain language, get a real one back."""
import flet as ft

from core import ai_architect, ai_rate_limit
from ui import theme


class AIArchitectView(ft.Column):
    def __init__(self, page: ft.Page, on_build_generated=None):
        super().__init__(expand=True, spacing=16, scroll=ft.ScrollMode.AUTO)
        self.app_page = page
        self.on_build_generated = on_build_generated

        self.prompt_field = ft.TextField(
            hint_text="e.g. \"$900 budget, I want to play GTA VI at 1440p\"",
            multiline=True,
            min_lines=3,
            max_lines=6,
            border_radius=14,
        )
        self.generate_button = ft.ElevatedButton(
            "Generate Build",
            icon=ft.Icons.AUTO_AWESOME_ROUNDED,
            on_click=self._on_generate,
        )
        self.loading_ring = ft.ProgressRing(width=18, height=18, stroke_width=2, visible=False)
        self.error_text = ft.Text("", color=theme.ERROR, size=13, visible=False)
        self.quota_text = ft.Text(self._quota_label(), color=theme.TEXT_MUTED, size=11)

        self.controls = [
            ft.Row(
                [ft.Text("AI Architect", size=26, weight=ft.FontWeight.BOLD)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Text(
                "Describe what you want and I'll pick real parts for it — reasoning included.",
                color=theme.TEXT_MUTED,
                size=13,
            ),
            theme.card(
                ft.Column(
                    [
                        self.prompt_field,
                        ft.Row(
                            [self.generate_button, self.loading_ring],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        self.quota_text,
                        self.error_text,
                    ],
                    spacing=14,
                )
            ),
        ]

    def _quota_label(self) -> str:
        remaining = ai_rate_limit.calls_remaining_today()
        return f"{remaining}/{ai_rate_limit.DAILY_LIMIT} AI Architect requests left today"

    async def _on_generate(self, e):
        prompt = (self.prompt_field.value or "").strip()
        if not prompt:
            return

        self.error_text.visible = False
        self.loading_ring.visible = True
        self.generate_button.disabled = True
        self._safe_update()

        try:
            result = await ai_architect.generate_build(prompt)
        except ai_architect.AIArchitectError as ex:
            self.error_text.value = str(ex)
            self.error_text.visible = True
        else:
            if self.on_build_generated:
                self.on_build_generated(result.name, result.selection, result.reasoning)
        finally:
            self.loading_ring.visible = False
            self.generate_button.disabled = False
            self.quota_text.value = self._quota_label()
            self._safe_update()

    def _safe_update(self):
        try:
            self.update()
        except RuntimeError:
            pass  # not mounted yet

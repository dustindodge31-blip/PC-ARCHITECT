"""Profile screen: local display name, community sign-in, and a link to the
Community feed (no dedicated nav tab — reached from here, like My Builds)."""
import flet as ft

from core import community, profile
from ui import theme


class ProfileView(ft.Column):
    def __init__(self, page: ft.Page, on_name_saved=None, on_browse_community=None):
        super().__init__(expand=True, spacing=16, scroll=ft.ScrollMode.AUTO)
        self.app_page = page
        self.on_name_saved = on_name_saved
        self.on_browse_community = on_browse_community

        self.name_field = ft.TextField(
            label="Display name",
            value=profile.get_display_name(),
            width=280,
        )

        self.email_field = ft.TextField(label="Email", width=280)
        self.password_field = ft.TextField(label="Password", width=280, password=True, can_reveal_password=True)
        self.auth_error_text = ft.Text("", color=theme.ERROR, size=12, visible=False)
        self.auth_section = ft.Column(spacing=12)

        self.controls = [
            ft.Text("Profile", size=26, weight=ft.FontWeight.BOLD),
            theme.card(
                ft.Column(
                    [
                        ft.Text("How PC Architect greets you", color=theme.TEXT_MUTED, size=12),
                        self.name_field,
                        ft.ElevatedButton("Save", icon=ft.Icons.CHECK_ROUNDED, on_click=self._save_name),
                    ],
                    spacing=12,
                )
            ),
            theme.card(self.auth_section),
        ]
        self._refresh_auth()

    def refresh(self):
        self._refresh_auth()

    def _save_name(self, e):
        profile.set_display_name(self.name_field.value or "")
        self.name_field.value = profile.get_display_name()
        self.app_page.update()
        if self.on_name_saved:
            self.on_name_saved()

    def _refresh_auth(self):
        self.auth_section.controls.clear()

        if not community.SUPABASE_URL or not community.SUPABASE_ANON_KEY:
            self.auth_section.controls.append(
                ft.Text("Community", size=14, weight=ft.FontWeight.W_600)
            )
            self.auth_section.controls.append(
                ft.Text(
                    "Community isn't configured yet — needs SUPABASE_URL / SUPABASE_ANON_KEY in .env.",
                    color=theme.TEXT_MUTED,
                    size=12,
                )
            )
            self._safe_update()
            return

        try:
            user = community.current_user()
        except community.CommunityError as ex:
            user = None
            self.auth_error_text.value = str(ex)
            self.auth_error_text.visible = True

        if user:
            self.auth_section.controls.extend([
                ft.Text("Community", size=14, weight=ft.FontWeight.W_600),
                ft.Text(f"Signed in as {user.email}", color=theme.TEXT_MUTED, size=12),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Browse Community",
                            icon=ft.Icons.PUBLIC_ROUNDED,
                            on_click=lambda e: self.on_browse_community() if self.on_browse_community else None,
                        ),
                        ft.TextButton("Log Out", on_click=self._log_out),
                    ],
                    spacing=10,
                ),
            ])
        else:
            self.auth_section.controls.extend([
                ft.Text("Community", size=14, weight=ft.FontWeight.W_600),
                ft.Text("Sign in to publish builds and browse the community feed.", color=theme.TEXT_MUTED, size=12),
                self.email_field,
                self.password_field,
                self.auth_error_text,
                ft.Row(
                    [
                        ft.ElevatedButton("Log In", on_click=self._log_in),
                        ft.OutlinedButton("Sign Up", on_click=self._sign_up),
                    ],
                    spacing=10,
                ),
            ])

        self._safe_update()

    def _credentials(self):
        return (self.email_field.value or "").strip(), self.password_field.value or ""

    def _sign_up(self, e):
        email, password = self._credentials()
        self.auth_error_text.visible = False
        try:
            community.sign_up(email, password)
        except community.CommunityError as ex:
            self.auth_error_text.value = str(ex)
            self.auth_error_text.visible = True
            self._safe_update()
            return
        self._refresh_auth()

    def _log_in(self, e):
        email, password = self._credentials()
        self.auth_error_text.visible = False
        try:
            community.sign_in(email, password)
        except community.CommunityError as ex:
            self.auth_error_text.value = str(ex)
            self.auth_error_text.visible = True
            self._safe_update()
            return
        self._refresh_auth()

    def _log_out(self, e):
        community.sign_out()
        self._refresh_auth()

    def _safe_update(self):
        try:
            self.update()
        except RuntimeError:
            pass  # not mounted yet (e.g. still in __init__)

import textwrap

import toml
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static

from src import consts

LOGO = textwrap.dedent(consts.logo).strip("\n")

CREDS_PATH = "./usrdata/credentials.toml"
SETTINGS_PATH = "settings.toml"


class SetupScreen(Screen):
    BINDINGS = [("q", "app.quit", "Quit"), ("ctrl+s", "submit", "Save")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with VerticalScroll(id="content"):
            yield Static(LOGO, id="logo", markup=False)
            yield Static(
                "First-time setup. Enter credentials for each platform. "
                "You'll bypass 2FA manually on first scrape.",
                classes="prompt",
            )

            yield Static("[ Instagram ]", classes="section")
            with Vertical(classes="field-group"):
                yield Label("Username")
                yield Input(placeholder="username", id="ig_user")
                yield Label("Email")
                yield Input(placeholder="you@example.com", id="ig_email")
                yield Label("Password")
                yield Input(placeholder="••••••••", password=True, id="ig_pass")

            yield Static("[ TikTok ]", classes="section")
            with Vertical(classes="field-group"):
                yield Label("Username")
                yield Input(placeholder="username", id="tt_user")
                yield Label("Email")
                yield Input(placeholder="you@example.com", id="tt_email")
                yield Label("Password")
                yield Input(placeholder="••••••••", password=True, id="tt_pass")

            yield Static("", id="error", classes="error")
            with Horizontal(id="actions-row"):
                yield Button("Save & finish", variant="success", id="save")
                yield Button("Quit", variant="error", id="quit")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#ig_user", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.action_submit()
        elif event.button.id == "quit":
            self.app.exit()

    def _collect(self) -> dict:
        q = lambda i: self.query_one(f"#{i}", Input).value.strip()
        return {
            "instagram": {
                "username": q("ig_user"),
                "email": q("ig_email"),
                "password": self.query_one("#ig_pass", Input).value,
            },
            "tiktok": {
                "username": q("tt_user"),
                "email": q("tt_email"),
                "password": self.query_one("#tt_pass", Input).value,
            },
        }

    def _validate(self, fields: dict) -> str | None:
        """
        TODO (user): decide validation policy. Return error string to block
        save, or None to allow it.

        Trade-offs:
          - Strict (require all 6 fields, basic email check) = fewer broken
            login attempts later, but blocks users who only use one platform.
          - Lenient (allow blank platform if all 3 of its fields blank) =
            flexible, but a half-filled platform silently fails on scrape.
          - None = trust user, write whatever they typed.

        Pick one. ~5–10 lines.
        """
        return None

    def action_submit(self) -> None:
        fields = self._collect()
        err = self._validate(fields)
        err_widget = self.query_one("#error", Static)
        if err:
            err_widget.update(f"[b red]{err}[/b red]")
            return
        err_widget.update("")
        try:
            self._write_credentials(fields)
            self._mark_setup_done()
        except Exception as e:
            err_widget.update(f"[b red]Write failed: {e}[/b red]")
            return
        self.app.push_screen(DoneScreen())

    def _write_credentials(self, fields: dict) -> None:
        with open(CREDS_PATH, "r") as f:
            data = toml.load(f)
        for platform in ("instagram", "tiktok"):
            data.setdefault(platform, {})
            data[platform]["username"] = fields[platform]["username"]
            data[platform]["email"] = fields[platform]["email"]
            data[platform]["password"] = fields[platform]["password"]
        with open(CREDS_PATH, "w") as f:
            toml.dump(data, f)

    def _mark_setup_done(self) -> None:
        with open(SETTINGS_PATH, "r") as f:
            config = toml.load(f)
        config.setdefault("setup", {})["fts"] = False
        with open(SETTINGS_PATH, "w") as f:
            toml.dump(config, f)


class DoneScreen(Screen):
    BINDINGS = [("q", "app.quit", "Quit"), ("enter", "app.quit", "Done")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="content"):
            yield Static(LOGO, id="logo", markup=False)
            yield Static(
                "[b green]Setup complete![/b green]\n\n"
                "Credentials saved. Re-run the app to start scraping.",
                classes="prompt",
            )
            yield Button("Quit", variant="primary", id="quit")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#quit", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.exit()


class SetupApp(App):
    CSS_PATH = "wizard.tcss"
    TITLE = "Stack Scraper"
    SUB_TITLE = "first-time setup"

    def on_mount(self) -> None:
        self.push_screen(SetupScreen())


if __name__ == "__main__":
    SetupApp().run()

import shutil
import sys
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from src import consts


def checkDependencies() -> bool:
    for dep in consts.DEPS:
        if shutil.which(dep) == None:
            sys.exit(1)
    print("dependencies installed")


class StackScrape(App):
    """
    Main application
    """

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_toggle_dark(self):
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    checkDependencies()
    app = StackScrape()
    app.run()

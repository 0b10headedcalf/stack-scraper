import typer
import shutil
import sys
import typer
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from src import consts
from src.scraping import webScraping

app = typer.Typer()


def checkDependencies() -> bool:
    for dep in consts.DEPS:
        if shutil.which(dep) == None:
            print("Dependencies not installed! Exiting...")
            sys.exit(1)
    print("dependencies installed")


class StackScrape(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_toggle_dark(self):
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-"


@app.command()
def run():
    print("running wizard")
    wizard = StackScrape()
    wizard.run()


@app.command()
def run_nogui(site: str, headless: bool):
    print(f"Running without GUI, scraping from {site}:headless={headless}")


if __name__ == "__main__":
    checkDependencies()
    app()

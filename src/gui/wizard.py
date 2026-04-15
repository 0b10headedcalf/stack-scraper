import contextlib
import io
import json
import os
import textwrap

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Header,
    LoadingIndicator,
    OptionList,
    ProgressBar,
    Static,
)
from textual.widgets.option_list import Option

from src import consts
from src.scraping import webScraping
from src.scraping import downloadLib

LOGO = textwrap.dedent(consts.logo).strip("\n")


def _silenced_call(fn, *args, **kwargs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        return fn(*args, **kwargs)


class SitePickerScreen(Screen):
    BINDINGS = [("q", "app.quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="content"):
            yield Static(LOGO, id="logo", markup=False)
            yield Static("Which site do you want to scrape?", classes="prompt")
            yield OptionList(
                *[Option(s.title(), id=s) for s in consts.PRESETS],
                id="sites",
            )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#sites", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.app.push_screen(CollectionsScreen(event.option.id))


class CollectionsScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back"), ("q", "app.quit", "Quit")]

    def __init__(self, site: str) -> None:
        super().__init__()
        self.site = site
        self.collections: list = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="content"):
            yield Static(
                f"Fetching collections for [b]{self.site.title()}[/b]…",
                id="status",
            )
            yield LoadingIndicator(id="loader")
            yield OptionList(id="collections")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#collections", OptionList).display = False
        self._fetch_collections()

    @work(thread=True, exclusive=True)
    def _fetch_collections(self) -> None:
        collections = _silenced_call(
            webScraping.scrapeCollections, platform=self.site, headless=False
        )
        os.makedirs("./out", exist_ok=True)
        with open(f"./out/{self.site}-collections.json", "w") as f:
            json.dump(collections, f)
        self.app.call_from_thread(self._render_collections, collections)

    def _render_collections(self, collections: list) -> None:
        self.collections = collections
        self.query_one("#loader", LoadingIndicator).display = False
        self.query_one("#status", Static).update(
            f"Pick a collection from [b]{self.site.title()}[/b]:"
        )
        ol = self.query_one("#collections", OptionList)
        ol.display = True
        for i, c in enumerate(collections):
            ol.add_option(Option(str(c[0]), id=str(i)))
        ol.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        idx = int(event.option.id)
        self.app.push_screen(ScrapeScreen(self.site, self.collections[idx]))


class ScrapeScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back"), ("q", "app.quit", "Quit")]

    def __init__(self, site: str, collection) -> None:
        super().__init__()
        self.site = site
        self.collection = collection

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="content"):
            yield Static(f"Scraping [b]{self.collection[0]}[/b]…", id="status")
            yield LoadingIndicator(id="loader")
            yield OptionList(
                Option("Download videos", id="videos"),
                Option("Download audio", id="audio"),
                Option("Transcribe (requires download)", id="transcribe"),
                id="actions",
            )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#actions", OptionList).display = False
        self._run_scrape()

    @work(thread=True, exclusive=True)
    def _run_scrape(self) -> None:
        _silenced_call(
            webScraping.scrape,
            site=self.site,
            headless=False,
            collection=self.collection,
        )
        self.app.call_from_thread(self._scrape_done)

    def _scrape_done(self) -> None:
        self.query_one("#loader", LoadingIndicator).display = False
        self.query_one("#status", Static).update(
            "Done! Links saved to [b]./out[/b]. What now?"
        )
        actions = self.query_one("#actions", OptionList)
        actions.display = True
        actions.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.app.push_screen(ActionScreen(event.option.id, self.site, self.collection))


class ActionScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back"), ("q", "app.quit", "Quit")]

    _LABELS = {
        "videos": "Downloading videos",
        "audio": "Downloading audio",
        "transcribe": "Transcribing",
    }

    def __init__(self, action: str, site: str, collection) -> None:
        super().__init__()
        self.action = action
        self.site = site
        self.collection = collection

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="content"):
            yield Static(self._LABELS[self.action] + "…", id="status")
            yield LoadingIndicator(id="loader")
            yield ProgressBar(id="progress", show_eta=False, show_percentage=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#progress", ProgressBar).display = False
        self._run()

    def _set_status(self, msg: str) -> None:
        self.query_one("#status", Static).update(msg)

    def _start_indeterminate(self, label: str) -> None:
        self._set_status(label + "…")
        self.query_one("#loader", LoadingIndicator).display = True
        self.query_one("#progress", ProgressBar).display = False

    def _start_progress(self, label: str, total: int) -> None:
        self._set_status(label + "…")
        self.query_one("#loader", LoadingIndicator).display = False
        bar = self.query_one("#progress", ProgressBar)
        bar.update(total=total, progress=0)
        bar.display = True

    def _advance_progress(self, current: int, total: int) -> None:
        self.query_one("#progress", ProgressBar).update(progress=current)

    def _finish(self) -> None:
        self._set_status("Done!")
        self.query_one("#loader", LoadingIndicator).display = False
        bar = self.query_one("#progress", ProgressBar)
        bar.display = False

    @work(thread=True, exclusive=True)
    def _run(self) -> None:
        cname = self.collection[0]
        call = self.app.call_from_thread

        if self.action == "videos":
            downloadLib.downloadVideos(cname, self.site)

        elif self.action == "audio":
            downloadLib.downloadAudio(cname, self.site)

        elif self.action == "transcribe":
            call(self._start_indeterminate, "Downloading audio")
            downloadLib.downloadAudio(cname, self.site)

            # count mp3s to size the progress bar before starting
            from pathlib import Path
            audioDir = Path(f"./out/downloads/{self.site}/{cname}/audio/")
            wavDir = audioDir / "wavs"
            mp3_total = len(list(audioDir.glob("*.mp3")))
            call(self._start_progress, "Converting to WAV", mp3_total or 1)
            downloadLib.convertAudio(
                cname, self.site,
                on_progress=lambda cur, tot: call(self._advance_progress, cur, tot),
            )

            wav_total = len(list(wavDir.glob("*.wav")))
            call(self._start_progress, "Transcribing", wav_total or 1)
            downloadLib.transcribeWavs(
                cname, self.site,
                on_progress=lambda cur, tot: call(self._advance_progress, cur, tot),
            )

        call(self._finish)


class WizardApp(App):
    CSS_PATH = "wizard.tcss"
    TITLE = "Stack Scraper"
    SUB_TITLE = "wizard"

    def on_mount(self) -> None:
        self.push_screen(SitePickerScreen())


if __name__ == "__main__":
    WizardApp().run()

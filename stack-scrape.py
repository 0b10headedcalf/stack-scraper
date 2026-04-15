#!/usr/bin/env python3
import json
import shutil
import sys
import subprocess
import os
import typer
from tqdm import tqdm
from src import consts
from src.scraping import webScraping
from src.scraping import downloadLib

app = typer.Typer(invoke_without_command=True)


@app.callback()
def _default(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        from src.gui.wizard import WizardApp

        WizardApp().run()


PLATFORM = consts.PLATFORM
FTS = consts.FTS
PRESETS = consts.PRESETS
TERM_W, TERM_H = shutil.get_terminal_size()


def runInstallScript():
    script_path = os.path.join(os.path.dirname(__file__), "install-deps.sh")
    try:
        subprocess.run(["bash", script_path], check=True)
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Please install manually.")
        sys.exit(1)
    except FileNotFoundError:
        print("install-deps.sh not found")
        sys.exit(1)


def checkDependencies() -> bool:
    for dep in consts.DEPENDENCIES:
        if shutil.which(dep) == None:
            print(f"You are missing {dep}! The install script will now run.")
            runInstallScript()
            break
        else:
            print(f"{dep} installed, continuing...")
    else:
        print("All dependencies installed!\n" + "-" * TERM_W)
        return True


@app.command()
def seeCollections(platform: str, intrun: bool = True):
    try:
        cols = []
        with open(f"./out/{platform.lower()}-collections.json", "r") as f:
            parsed = json.load(f)
            for i in range(len(parsed)):
                cols.append(parsed[i])
            if intrun:
                print(cols)
            return cols
    except FileNotFoundError as e:
        print("Collections list does not exist! Consider running the script first.")


def _tqdm_progress(desc: str):
    bar = tqdm(total=None, desc=desc, unit="file", dynamic_ncols=True)

    def callback(current: int, total: int):
        if bar.total != total:
            bar.reset(total=total)
        bar.n = current
        bar.refresh()
        if current >= total:
            bar.close()

    return callback


def _fetch_and_save_collections(site: str, headless: bool):
    cols = webScraping.scrapeCollections(platform=site, headless=headless)
    os.makedirs("./out", exist_ok=True)
    with open(f"./out/{site.lower()}-collections.json", "w") as f:
        json.dump(cols, f)
    return cols


@app.command()
def run_nogui(site: str, headless: bool):
    cols = seeCollections(platform=site, intrun=False)
    if not cols:
        print("No collections cached. Fetching now...")
        cols = _fetch_and_save_collections(site, headless)
        print(
            f"Cached {len(cols)} collections to ./out/{site.lower()}-collections.json"
        )
    for i, col in enumerate(cols, 1):
        print(f"{i}. {col[0]}")
    collection = cols[int(input("Choose a collection: ")) - 1]
    cname = collection[0]

    print("-" * TERM_W)
    webScraping.scrape(site=site, headless=headless, collection=collection)
    print(f"Scrape done — links saved to ./out\n{'-' * TERM_W}")

    p_further = input("Process further? (download a/v, transcription) y/n: ")
    if p_further.lower() not in ["y", "yes"]:
        sys.exit()

    opts = ["Download video", "Download audio", "Transcribe"]
    for i, o in enumerate(opts, 1):
        print(f"{i}. {o}")
    opt = int(input("Choose an option: "))

    match opt:
        case 1:
            print("Downloading videos...")
            downloadLib.downloadVideos(collection=cname, platform=site)
        case 2:
            print("Downloading audio...")
            downloadLib.downloadAudio(collection=cname, platform=site)
        case 3:
            print("Downloading audio...")
            downloadLib.downloadAudio(collection=cname, platform=site)
            downloadLib.convertAudio(
                collection=cname,
                platform=site,
                on_progress=_tqdm_progress("Converting to WAV"),
            )
            downloadLib.transcribeWavs(
                collection=cname,
                platform=site,
                on_progress=_tqdm_progress("Transcribing"),
            )
        case _:
            print("Invalid option.")
            sys.exit(1)


@app.command()
def run():
    from src.gui.wizard import WizardApp

    WizardApp().run()


@app.command()
def setup():
    from src.gui.setup import SetupApp

    SetupApp().run()


if __name__ == "__main__":
    if FTS:
        print("running setup...")
        setup()
    else:
        app()

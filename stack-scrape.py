#!/usr/bin/env python3
import json
import shutil
import typer
import shutil
import sys
import typer
import subprocess
import os
from src import consts
from src.scraping import webScraping

app = typer.Typer()


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
def seeCollections(platform: str):
    try:
        cols = []
        with open(f"./out/{platform.lower()}-collections.json", "r") as f:
            parsed = json.load(f)
            for i in range(len(parsed)):
                cols.append(parsed[i])
            return cols
    except FileNotFoundError as e:
        print("Collections list does not exist! Consider running the script first.")


@app.command()
def run_nogui(site: str, headless: bool):
    cols = seeCollections(platform=site)
    for i, col in enumerate(cols, 1):
        print(f"{i}. {col[0]}")
    _ = cols[int(input("Choose a collection...")) - 1]
    collection = _
    webScraping.scrape(site=site, headless=headless, collection=collection)
    print("completed...check /out")


@app.command()
def run():
    from src.gui.wizard import WizardApp

    WizardApp().run()


@app.command()
def setup():
    from src.gui.setup import SetupApp

    SetupApp().run()


if __name__ == "__main__":
    if not FTS:
        app()
    elif FTS == True:
        print("running setup...")
        setup()

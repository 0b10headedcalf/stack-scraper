#!/usr/bin/env python3
import json
import shutil
import typer
import shutil
import sys
import typer
import toml
import subprocess
import os
import getpass
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
    print(collection)
    webScraping.scrape(site=site, headless=headless, collection=collection)


@app.command()
def run():
    from src.gui.wizard import WizardApp

    run().split()


@app.command()
def setup():
    from src.gui.setup import SetupApp

    SetupApp().run()
    # if checkDependencies() == True:
    #     print("\nWelcome to " + consts.logo)
    #     print("-" * TERM_W)
    #     print(
    #         "In order for the application to work properly, you'll have to enter your social media credentials and manually bypass 2FA."
    #     )
    #     print("[Instagram]")
    #     insta_user = input("What is your instagram username?")
    #     insta_email = input("\nEmail?")
    #     insta_password = getpass.getpass("Password:")
    #     print("[Tiktok]")
    #     tt_user = input("What is your TikTok username?")
    #     tt_email = input("\nEmail?")
    #     tt_password = getpass.getpass("Password:")
    #     with open("./usrdata/credentials.toml", "r") as f:
    #         data = toml.load(f)
    #     (
    #         data["instagram"]["username"],
    #         data["instagram"]["password"],
    #         data["instagram"]["email"],
    #     ) = (insta_user, insta_password, insta_email)
    #     (
    #         data["tiktok"]["username"],
    #         data["tiktok"]["password"],
    #         data["tiktok"]["email"],
    #     ) = (tt_user, tt_password, tt_email)
    #     with open("./usrdata/credentials.toml", "w") as f:
    #         toml.dump(data, f)
    #     print("Credentials added!")
    #     with open("settings.toml", "r") as f:
    #         config = toml.load(f)
    #     config["setup"]["fts"] = False
    #     with open("settings.toml", "w") as f:
    #         toml.dump(config, f)
    #     print("Setup complete! Please rerun the application.")


if __name__ == "__main__":
    if not FTS:
        app()
    elif FTS == True:
        print("Looks like it's your first time using this tool! Running setup...")
        print("-" * TERM_W)
        setup()

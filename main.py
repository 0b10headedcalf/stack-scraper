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


def healthCheck():
    # print(f"os: {PLATFORM}, is FTS:{FTS}")
    if FTS == False:
        return True


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
    with open(f"./out/collections-{platform.lower()}.json", "r") as f:
        parsed = json.load(f)
        print(parsed)


@app.command()
def run_adv(site: str, headless: bool, collection: int):
    webScraping.scrape(site=site, headless=headless, collection=collection)


@app.command()
def run_wizard():
    print("\nWelcome to " + consts.logo)
    print("-" * TERM_W)
    print("Which website would you like to scrape?")
    for i, site in enumerate(PRESETS, 1):
        print(f"{i}. {site}")
    sitechoice = PRESETS[int(input("Select (1-2): ")) - 1]
    print("Checking browserstate...")
    state_path = consts.STATEPATHS[sitechoice.lower()]
    if os.path.isfile(state_path):
        print(f"State found for {sitechoice}!")
        headless = True
    else:
        print(
            f"Can't find state file for {sitechoice}, it might be misplaced, malformed, or missing. Running first time setup..."
        )
        headless = False
    print("Grabbing collections, please wait...")
    foundcollections = webScraping.scrapeCollections(
        platform=sitechoice, headless=headless
    )
    with open(f"./out/collections-{sitechoice.lower()}.json", "w") as f:
        json.dump(foundcollections, f)
    print("Which collection would you like to scrape?")
    for i, collection in enumerate(foundcollections, 1):
        print(f"{i}. {collection[0]}")
    toCollect = foundcollections[int(input("Select:")) - 1]
    webScraping.scrape(site=sitechoice, headless=headless, collection=toCollect)
    print("Finished scraping! Look in your //out// directory for a list of links")


def setup():
    if checkDependencies() == True:
        print("\nWelcome to " + consts.logo)
        print("-" * TERM_W)
        print(
            "In order for the application to work properly, you'll have to enter your social media credentials and manually bypass 2FA."
        )
        print("[Instagram]")
        insta_user = input("What is your instagram username?")
        insta_email = input("\nEmail?")
        insta_password = getpass.getpass("Password:")
        print("[Tiktok]")
        tt_user = input("What is your TikTok username?")
        tt_email = input("\nEmail?")
        tt_password = getpass.getpass("Password:")
        with open("./usrdata/credentials.toml", "r") as f:
            data = toml.load(f)
        (
            data["instagram"]["username"],
            data["instagram"]["password"],
            data["instagram"]["email"],
        ) = (insta_user, insta_password, insta_email)
        (
            data["tiktok"]["username"],
            data["tiktok"]["password"],
            data["tiktok"]["email"],
        ) = (tt_user, tt_password, tt_email)
        with open("./usrdata/credentials.toml", "w") as f:
            toml.dump(data, f)
        print("Credentials added!")
        with open("settings.toml", "r") as f:
            config = toml.load(f)
        config["setup"]["fts"] = False
        with open("settings.toml", "w") as f:
            toml.dump(config, f)
        print("Setup complete! Please rerun the application.")


if __name__ == "__main__":
    if healthCheck():
        app()
    elif FTS == True:
        print("Looks like it's your first time using this tool! Running setup...")
        print("-" * TERM_W)
        setup()

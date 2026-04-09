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
BROWSER = consts.BROWSER
FTS = consts.FTS
AVAILABLE_BROWSERS = ["chromium", "firefox", "webkit"]
PRESETS = consts.PRESETS
TERM_W, TERM_H = shutil.get_terminal_size()


def healthCheck():
    print(f"os: {PLATFORM}, browser:{BROWSER}, is FTS:{FTS}")
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
def run_adv(site: str, headless: bool):
    webScraping.scrape(site=site, headless=headless)


@app.command()
def run():
    print("\nWelcome to " + consts.logo)
    print("-" * TERM_W)
    print("Which website would you like to scrape?")
    for i, site in enumerate(PRESETS, 1):
        print(f"{i}. {site}")
    sitechoice = PRESETS[int(input("Select (1-2): ")) - 1]
    print("Grabbing collections, please wait...")


def setup():
    if checkDependencies() == True:
        print("\nWelcome to " + consts.logo)
        print("-" * TERM_W)
        print(
            "In order for the application to work properly, you'll have to enter your social media credentials and manually bypass 2FA."
        )
        print("[Instagram]")
        insta_user = input("What is your instagram username/email?")
        insta_password = getpass.getpass("Password:")
        print("[Tiktok]")
        tt_user = input("What is your TikTok username/email?")
        tt_password = getpass.getpass("Password:")
        with open("./usrdata/credentials.toml", "r") as f:
            data = toml.load(f)
        data["instagram"]["username"], data["instagram"]["password"] = (
            insta_user,
            insta_password,
        )
        data["tiktok"]["username"], data["tiktok"]["password"] = (
            tt_user,
            tt_password,
        )
        with open("./usrdata/credentials.toml", "w") as f:
            toml.dump(data, f)
        print("Credentials added!")
        print("What is your browser of choice? (Chromium is the default)")
        for i, browser in enumerate(AVAILABLE_BROWSERS, 1):
            print(f"{i}. {browser}")
        browserchoice = AVAILABLE_BROWSERS[int(input("Select (1-3): ")) - 1]
        with open("settings.toml", "r") as f:
            config = toml.load(f)
        config["setup"]["fts"] = False
        config["setup"]["browser"] = browserchoice
        with open("settings.toml", "w") as f:
            toml.dump(config, f)
        print("Setup complete! Please rerun the application.")


# TODO: ludovico the user
# @app.command()
# def watch(collection_path: str, unwatched_only: bool = True):
#     """
#     Launch the video lockdown player for a scraped collection.
#
#     Args:
#         collection_path: Path to the collection directory
#         unwatched_only: Only play videos you haven't watched yet
#     """
#     manager = VideoPlaybackManager(collection_path)
#     player = manager.launch_player(unwatched_only=unwatched_only)
#     player.play_current_video()
#     player.show()


if __name__ == "__main__":
    if healthCheck():
        app()
    elif FTS == True:
        print("Looks like it's your first time using this tool! Running setup...")
        print("-" * TERM_W)
        setup()

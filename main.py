import typer
import shutil
import sys
import typer
from src import consts
from src.scraping import webScraping

app = typer.Typer()


PLATFORM = consts.PLATFORM
BROWSER = consts.BROWSER
FTS = consts.FTS


def healthCheck():
    print(f"os: {PLATFORM}, browser:{BROWSER}, is FTS:{FTS}")
    if FTS == False:
        return True


def checkDependencies() -> bool:
    def install_dependencies(dep: str):
        prompt = input(f"{dep} not installed! Would you like to install dependencies?")
        if prompt.lower() in ("y", "yes"):
            match PLATFORM:
                case "linux":
                    print("user is running linux!")
                case "darwin":
                    print("user is on MacOS")
                case "win32":
                    print("user is on windows!")
                case _:
                    print("user is on an unsupported OS")
        elif prompt.lower() in ("n", "no"):
            print("Please install dependencies before use. Exiting...")
            sys.exit(1)
        else:
            print("Please type an answer in y,yes,n,no")
            install_dependencies(dep)

    for dep in consts.DEPENDENCIES:
        if shutil.which(dep) == None:
            install_dependencies(dep)
        else:
            print(f"{dep} installed, continuing...")
    else:
        print("All dependencies installed!")
        return True


@app.command()
def run(site: str, headless: bool, gui: bool):
    if gui:
        print("running wizard")
    elif not gui:
        print(f"Running without GUI, scraping from {site}:headless={headless}")
        webScraping.scrape(site=site, headless=headless)


def setup():
    checkDependencies()


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
        setup()

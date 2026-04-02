import subprocess
import argparse
import shutil

DEPS = ["ffmpeg","yt-dlp"]
DEBUG = True
PRESETS = ("instagram","tiktok","youtubeshorts","twitter")


def isBinaryInstalled(program_name):
    return shutil.which(program_name)

def checkDependencies():
    for dep in DEPS:
        if not isBinaryInstalled(dep):
            print(f"{dep} is not installed! Breaking now...")
            break
            sys.exit()
    if DEBUG:
        print("All dependencies have been properly installed")

def runVideoDownloader():
    pass

def setAuth():
    pass


def main():
    checkDependencies()


if __name__ == "__main__":
    main()




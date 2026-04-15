from pathlib import Path
import json
import subprocess
from .. import consts

STATEPATH = consts.STATEPATHS
OUTPATH = "./usrdata/cookies.txt"


def convertCookies(platform, statePath, outPath):
    with open(statePath[platform]) as f:
        state = json.load(f)
    lines = ["# Netscape HTTP Cookie File\n"]
    for c in state["cookies"]:
        domain = c["domain"]
        flag = "TRUE" if domain.startswith(".") else "FALSE"
        path = c.get("path", "/")
        secure = "TRUE" if c.get("secure") else "FALSE"
        expiry = int(c.get("expires", 0)) or 0
        lines.append(
            f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{c['name']}\t{c['value']}\n"
        )
    with open(outPath, "w") as f:
        f.writelines(lines)


def load_data(collection, platform):
    platform = platform.lower()
    convertCookies(platform=platform, statePath=STATEPATH, outPath=OUTPATH)
    with open(f"./out/{collection}-{platform}-links.json", "r") as f:
        data = json.load(f)
    return data


def downloadVideos(collection, platform: str):
    data = load_data(collection, platform)
    outDir = Path(f"./out/downloads/{platform}/{collection}/videos/")
    outDir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "yt-dlp",
            "--cookies",
            "./usrdata/cookies.txt",
            "-o",
            f"./out/downloads/{platform}/{collection}/videos/%(title)s.%(ext)s",
            "--ignore-errors",
            *data,
        ],
    )


def downloadAudio(collection, platform):
    load_data(collection, platform)
    data = load_data(collection, platform)
    outDir = Path(f"./out/downloads/{platform}/{collection}/audio/")
    outDir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "yt-dlp",
            "--cookies",
            "./usrdata/cookies.txt",
            "-o",
            f"./out/downloads/{platform}/{collection}/audio/%(title)-audio.%(ext)s",
            "--ignore-errors",
            "-t",
            "mp3",
            *data,
        ],
    )


#
def transcribe(collection, platform):
    downloadAudio(collection, platform)

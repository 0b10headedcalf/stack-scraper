import shutil
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
    return


def downloadAudio(collection, platform):
    data = load_data(collection, platform)
    outDir = Path(f"./out/downloads/{platform}/{collection}/audio/")
    outDir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "yt-dlp",
            "--cookies",
            "./usrdata/cookies.txt",
            "-o",
            f"./out/downloads/{platform}/{collection}/audio/%(title)s-audio.%(ext)s",
            "--ignore-errors",
            "--write-info-json",
            "-x",
            "--audio-format",
            "mp3",
            *data,
        ],
    )
    return data


def convertAudio(collection, platform, on_progress=None):
    audioDir = Path(f"./out/downloads/{platform}/{collection}/audio/")
    outDir = audioDir / "wavs"
    outDir.mkdir(parents=True, exist_ok=True)
    mp3s = [f for f in audioDir.glob("*.mp3") if not (outDir / (f.stem + ".wav")).exists()]
    total = len(mp3s)
    for i, mp3 in enumerate(mp3s, 1):
        wavOut = outDir / (mp3.stem + ".wav")
        subprocess.run(["ffmpeg", "-i", str(mp3), str(wavOut)])
        if on_progress:
            on_progress(i, total)
    return None


def _load_info(audioDir: Path, stem: str) -> dict:
    info_path = audioDir / f"{stem}.info.json"
    if info_path.exists():
        with open(info_path) as f:
            return json.load(f)
    return {}


def _format_header(info):
    duration_s = int(info.get("duration", 0))
    duration = f"{duration_s // 60}:{duration_s % 60:02d}" if duration_s else "unknown"
    return (
        f"Title:    {info.get('title', 'unknown')}\n"
        f"Author:   {info.get('uploader', info.get('channel', 'unknown'))}\n"
        f"URL:      {info.get('webpage_url', 'unknown')}\n"
        f"Duration: {duration}\n"
        f"{'─' * 60}\n\n"
    )


def transcribeWavs(collection, platform, on_progress=None):
    audioDir = Path(f"./out/downloads/{platform}/{collection}/audio/")
    wavDir = audioDir / "wavs"
    if not shutil.which("voxtype"):
        raise RuntimeError("voxtype not found — install it for local transcription")
    txtOut = Path(f"./out/transcripts/{platform}/{collection}/")
    txtOut.mkdir(parents=True, exist_ok=True)
    wavs = [w for w in wavDir.glob("*.wav") if not (txtOut / (w.stem + ".txt")).exists()]
    total = len(wavs)
    for i, wav in enumerate(wavs, 1):
        outFile = txtOut / (wav.stem + ".txt")
        result = subprocess.run(
            ["voxtype", "transcribe", str(wav)], capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"voxtype failed for {wav.name}: {result.stderr.strip()}")
            if on_progress:
                on_progress(i, total)
            continue
        transcript_lines = result.stdout.splitlines()
        transcript = "\n".join(transcript_lines[11:])
        info = _load_info(audioDir, wav.stem)
        header = _format_header(info)
        outFile.write_text(header + transcript)
        if on_progress:
            on_progress(i, total)
    return None


def transcribe(collection, platform):
    downloadAudio(collection, platform)
    convertAudio(collection, platform)
    transcribeWavs(collection, platform)
    return None

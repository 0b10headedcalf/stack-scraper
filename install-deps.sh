#!/bin/bash
set -e

echo "Installing dependencies..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux"
    sudo apt-get update
    sudo apt-get install -y ffmpeg
    sudo apt-get install -y yt-dlp
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"
    if ! command -v brew &> /dev/null; then
        echo "Error: Homebrew not found. Please install from https://brew.sh"
        exit 1
    fi
    brew install ffmpeg yt-dlp
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "Detected Windows"
    if ! command -v choco &> /dev/null; then
        echo "Error: Chocolatey not found."
        echo "Please install from https://chocolatey.org/install"
        echo "Then run this script again in an admin terminal."
        exit 1
    fi
    choco install -y ffmpeg yt-dlp
else
    echo "Unsupported OS: $OSTYPE"
    echo "Please install ffmpeg and yt-dlp manually"
    exit 1
fi

echo "Dependencies installed successfully!"

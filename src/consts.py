import os
import tomllib

# binary dependencies
DEPENDENCIES = ["ffmpeg", "yt-dlp"]

# directories & files
DIRNAME = os.getcwd()
STATEPATHS = {
    "instagram": os.path.join(DIRNAME, "usrdata/state-instagram.json"),
    "tiktok": os.path.join(DIRNAME, "usrdata/state-tiktok.json"),
}
f_SETTINGS = open("settings.toml", "rb")
f_CREDENTIALS = open("./usrdata/credentials-test.toml", "rb")

# user information
SETTINGS = tomllib.load(f_SETTINGS)
LOGIN_CREDENTIALS = tomllib.load(f_CREDENTIALS)
FTS, PLATFORM = (
    SETTINGS["setup"]["fts"],
    SETTINGS["setup"]["os"],
)
PRESETS = ("instagram", "tiktok")


# logo
logo = """
                                        ||                                                               
          ....  .||.   ....     ....    ||  ..     ....    ....  ... ..   ....   ... ...    ....  ... ..  
          ||. '   ||   '' .||  .|   ''  || .'     ||. '  .|   ''  ||' '' '' .||   ||'  || .|...||  ||' '' 
          . '|..  ||   .|' ||  ||       ||'|.     . '|.. ||       ||     .|' ||   ||    | ||       ||     
          |'..|'  '|.' '|..'|'  '|...' .||. ||.   |'..|'  '|...' .||.    '|..'|'  ||...'   '|...' .||.    
                                                                                  ||
                                                                                  ||
"""

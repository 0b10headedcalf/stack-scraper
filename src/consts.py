import os
import tomllib

# binary dependencies
DEPENDENCIES = ["ffmpeg", "yt-dlp"]

# directories & files
DIRNAME = os.getcwd()
STATEPATH = os.path.join(DIRNAME, "usrdata/state.json")
f_SETTINGS = open("settings.toml", "rb")
f_CREDENTIALS = open("./usrdata/credentials-test.toml", "rb")

# user information
SETTINGS = tomllib.load(f_SETTINGS)
LOGIN_CREDENTIALS = tomllib.load(f_CREDENTIALS)
FTS, BROWSER, PLATFORM = (
    SETTINGS["setup"]["fts"],
    SETTINGS["setup"]["browser"],
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
"""

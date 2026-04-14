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


LOGIN_FLOWS = {
    "instagram": {
        "login_url": "https://instagram.com/",
        "username_selector": "[name='email']",
        "password_selector": "[name='pass']",
        "submit_selector": "role=button[name='Log In']",
        "twofa_url_glob": "**/auth_platform/**",
        "twofa_url_fragment": "auth_platform",
    },
    "tiktok": {
        "login_url": "https://tiktok.com/login/phone-or-email/email/",
        "username_selector": "[name='username']",
        "password_selector": "[type='password']",
        "submit_selector": "[type='submit']",
        "twofa_url_glob": "**/2sv/**",
        "twofa_url_fragment": "2sv",
    },
}

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

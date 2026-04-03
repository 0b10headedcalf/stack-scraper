import tomllib
import sys
import os
import tomllib

DIRNAME = os.getcwd()
USRFILENAME_ex= os.path.join(DIRNAME,'usrdata/credentials-example.toml')
# USRFILENAME = os.path.join(DIRNAME,'usrdata/credentials.toml')


class MalformedCredentials(Exception):
    #either user credentials do not exist or they are in the wrong format
    def __init__(self,message: str):
        super().__init__(message)
        

def checkCredentialsFile():
    try:
        with open (USRFILENAME_ex,"rb") as f:
            credentials = tomllib.load(f)
            return credentials
    except MalformedCredentials as e:
        raise MalformedCredentials(e)
        sys.stderr(e)

checkCredentialsFile()

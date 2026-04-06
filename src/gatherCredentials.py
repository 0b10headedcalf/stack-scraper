import tomllib
import sys
import os
import shutil
import tomllib
import click

DIRNAME = os.getcwd()
# USRFILENAME = os.path.join(DIRNAME,'usrdata/credentials.toml')
#[DEBUG]
TESTPATH = os.path.join(DIRNAME,'usrdata/test.toml')
TERM_W,TERM_H = shutil.get_terminal_size()

# class MalformedCredentials(Exception):
#     #either user credentials do not exist or they are in the wrong format
#     def __init__(self,message: str):
#         super().__init__(message)
        
def checkCredentialsFile():
    try:
        with open (TESTPATH,"rb") as f:
            credentials = tomllib.load(f)
            return credentials
    except FileNotFoundError as e:
        writeCredentials()

def writeCredentials():
    print("Looks like its your first time running me! Let's set up your auth credentials.\n")
    print("-" * TERM_W)
    with open(TESTPATH,"x",encoding="utf-8") as f:
        f.write("[instagram]\nusername=")
        username = input("What is your instagram username?\n")
        f.write("'"+username+"'")
        f.write("\npassword=")
        password = input("Password?\n")
        f.write("'"+password+"'")
    with open (TESTPATH,"rb") as f:
        credentials = tomllib.load(f)
        print(credentials)
        return credentials


    

checkCredentialsFile()
os.remove(TESTPATH)

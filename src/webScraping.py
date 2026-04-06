import tomllib
import time
import os
import utils
from playwright.sync_api import sync_playwright

DIRNAME = os.getcwd()
STATEPATH = os.path.join(DIRNAME, "usrdata/state.json")
f_SETTINGS = open("settings.toml", "rb")
f_CREDENTIALS = open("./usrdata/credentials-test.toml", "rb")
SETTINGS = tomllib.load(f_SETTINGS)
LOGIN_CREDENTIALS = tomllib.load(f_CREDENTIALS)
FTS, BROWSER = SETTINGS["setup"]["fts"], SETTINGS["setup"]["browser"]
global AUTH
global site_arg
browser_choice = BROWSER


def checkState():
    pass


@utils.isFirstTimeSetup(initialSetup=FTS)
def scrapeInstagram():
    _username = LOGIN_CREDENTIALS["instagram"]["username"]
    email_fill = LOGIN_CREDENTIALS["instagram"]["email"]
    pass_fill = LOGIN_CREDENTIALS["instagram"]["password"]
    site_arg = "https://instagram.com/"

    def queryCollection(page):
        container = page.locator('[aria-label="Saved collections"]')
        container.wait_for(state="visible", timeout=10_000)
        links = container.locator("a[aria-label]")
        return [
            (
                "-".join(links.nth(i).get_attribute("aria-label").lower().split()),
                links.nth(i).get_attribute("href"),
            )
            for i in range(links.count())
        ]

    with sync_playwright() as p:
        browser = getattr(p, browser_choice).launch(headless=False, slow_mo=100)
        if os.path.isfile(STATEPATH):
            context = browser.new_context(storage_state=STATEPATH)
            page = context.new_page()
            site_arg += _username + "/saved/"
            page.goto(site_arg)
        else:
            context = browser.new_context()
            page = context.new_page()
            page.goto(site_arg)
            page.locator("[name='email']").fill(email_fill)
            page.locator("[name='pass']").fill(pass_fill)
            page.get_by_label("Log In").click()
            page.wait_for_url("**/auth_platform/**", timeout=60_000)
            print("Waiting for 2FA to be completed...")
            page.wait_for_url(lambda url: "auth_platform" not in url, timeout=300_000)
            print("2FA complete")
            site_arg += _username + "/saved/"
            page.goto(site_arg)
            context.storage_state(path=STATEPATH)
        collections = queryCollection(page)
        print(collections)
        page.goto("https://www.instagram.com" + collections[1][1])
        time.sleep(9999999)
        browser.close()


def scrapeTikTok():
    site_arg = "https://tiktok.com/"
    user_fill = LOGIN_CREDENTIALS["tiktok"]["username"]
    pass_fill = LOGIN_CREDENTIALS["tiktok"]["password`"]

    def scrapeCollectionNames():
        pass

    def gatherCollections(collectionName):
        pass

    if FTS == True:
        with sync_playwright() as p:
            browser = getattr(p, browser_choice).launch(headless=False)
            page = browser.new_page()
            page.goto(site_arg)
            time.sleep(999999999)
            browser.close()


scrapeInstagram()

import json
import tomllib
import time
import os
from src import utils
from playwright.sync_api import sync_playwright
from playwright.sync_api import Page

DIRNAME = os.getcwd()
STATEPATH = os.path.join(DIRNAME, "usrdata/state.json")
f_SETTINGS = open("settings.toml", "rb")
f_CREDENTIALS = open("./usrdata/credentials-test.toml", "rb")
SETTINGS = tomllib.load(f_SETTINGS)
LOGIN_CREDENTIALS = tomllib.load(f_CREDENTIALS)
FTS, BROWSER = SETTINGS["setup"]["fts"], SETTINGS["setup"]["browser"]
PRESETS = ("instagram", "tiktok")
global AUTH
global site_arg
browser_choice = BROWSER


def checkState():
    return os.path.isfile(STATEPATH)


@utils.isFirstTimeSetup(initialSetup=FTS)
def scrape_instagram(headless: bool):
    _username = LOGIN_CREDENTIALS["instagram"]["username"]
    email_fill = LOGIN_CREDENTIALS["instagram"]["email"]
    pass_fill = LOGIN_CREDENTIALS["instagram"]["password"]
    site_arg = "https://instagram.com/"

    def scrollUntilLoaded(page: Page) -> List:
        seen = set()
        while True:
            current_links = page.locator("article a").evaluate_all(
                "els=>els.map(el=>el.href)"
            )
            seen.update(current_links)
            prev = len(seen)
            page.keyboard.press("End")
            time.sleep(0.5)
            current_links = page.locator("article a").evaluate_all(
                "els=>els.map(el=>el.href)"
            )
            seen.update(current_links)
            print(prev, len(seen))
            if len(seen) == prev:
                break
        return list(seen)

    def queryCollection(page: Page) -> List[str]:
        container = page.locator('[aria-label="Saved collections"]')
        container.wait_for(state="visible")
        links = container.locator("a[aria-label]")
        return [
            (
                "-".join(links.nth(i).get_attribute("aria-label").lower().split()),
                links.nth(i).get_attribute("href"),
            )
            for i in range(links.count())
        ]

    with sync_playwright() as p:
        browser = getattr(p, browser_choice).launch(headless=headless)
        if checkState() == True:
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
            page.wait_for_url("**/auth_platform/**", timeout=120_000)
            print("Waiting for 2FA to be completed...")
            page.wait_for_url(lambda url: "auth_platform" not in url)
            print("2FA complete")
            site_arg += _username + "/saved/"
            page.goto(site_arg)
            context.storage_state(path=STATEPATH)
        collections = queryCollection(page)
        print(collections)
        target_collection = "https://www.instagram.com" + collections[1][1]
        page.goto(target_collection)
        page.wait_for_selector("article a", state="attached")
        links = scrollUntilLoaded(page)
        with open(f"./out/{collections[1][0]}-videos.json", "w") as f:
            json.dump(links, f)
            print(f"links saved to {str(f)}")
        browser.close()


def scrape_tiktok():
    site_arg = "https://tiktok.com/"
    user_fill = LOGIN_CREDENTIALS["tiktok"]["username"]
    pass_fill = LOGIN_CREDENTIALS["tiktok"]["password`"]
    return


def scrape(site: str, headless=bool):
    if site.lower() in PRESETS:
        globals()[f"scrape_{site}"](headless=headless)
    else:
        print("Invalid site preset")
        return

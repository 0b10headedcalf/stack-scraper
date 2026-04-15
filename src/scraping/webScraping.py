from playwright.sync_api import Locator
import json
import time
import os
from contextlib import contextmanager
from playwright.sync_api import Page
from camoufox.sync_api import Camoufox
from .. import consts

DIRNAME = consts.DIRNAME
STATEPATHS = consts.STATEPATHS
SETTINGS = consts.SETTINGS
LOGIN_CREDENTIALS = consts.LOGIN_CREDENTIALS
FTS = consts.FTS
PRESETS = consts.PRESETS
LOGIN_FLOWS = consts.LOGIN_FLOWS


def checkState(platform: str):
    return os.path.isfile(STATEPATHS[platform.lower()])


def _perform_login(page: Page, flow: dict, creds: dict) -> None:
    page.locator(flow["username_selector"]).fill(creds["username"])
    page.locator(flow["password_selector"]).fill(creds["password"])
    page.locator(flow["submit_selector"]).click()
    page.wait_for_url(flow["twofa_url_glob"], timeout=120_000)
    print("Waiting for 2FA to be completed...")
    page.wait_for_url(lambda url: flow["twofa_url_fragment"] not in url, timeout=0)
    print("2FA complete")


@contextmanager
def authenticated_page(platform: str, headless: bool):
    platform = platform.lower()
    state_path = STATEPATHS[platform]
    flow = LOGIN_FLOWS[platform]
    creds = LOGIN_CREDENTIALS[platform]

    with Camoufox(headless=headless) as browser:
        if checkState(platform):
            context = browser.new_context(storage_state=state_path)
            page = context.new_page()
        else:
            print("First time login")
            context = browser.new_context()
            page = context.new_page()
            page.goto(flow["login_url"])
            _perform_login(page, flow, creds)
            context.storage_state(path=state_path)
        yield page


def scrollScrape(
    page: Page, platform: str, tt_isCollection: bool, container: Locator = None
):
    def tt_scrape(container=container, tt_isCollection=tt_isCollection):
        validlinks = container.locator("[data-e2e='collection-item']")
        prev = -1
        if tt_isCollection:
            f: set = set(
                validlinks.evaluate_all(
                    "els => els.map(el => el.querySelector('a')?.href).filter(Boolean)"
                )
            )
        else:
            f: set = set(
                tuple(c)
                for c in validlinks.evaluate_all(
                    "els => els.map(el => [el.querySelector('img')?.alt, el.querySelector('a')?.href])"
                )
            )
        while True:
            current = validlinks.count()
            if current == prev:
                break
            prev = current
            validlinks.nth(current - 1).scroll_into_view_if_needed()
            time.sleep(1)
            if tt_isCollection:
                f.update(
                    validlinks.evaluate_all(
                        "els => els.map(el => el.querySelector('a')?.href).filter(Boolean)"
                    )
                )
            else:
                f.update(
                    tuple(c)
                    for c in validlinks.evaluate_all(
                        "els => els.map(el => [el.querySelector('img')?.alt, el.querySelector('a')?.href])"
                    )
                )
        if tt_isCollection:
            return list(f)
        return [c for c in f if c[0] is not None]

    if platform.lower() == "instagram":
        seen = set()
        while True:
            current_links = page.locator("article a").evaluate_all(
                "els=>els.map(el=>el.href)"
            )
            seen.update(current_links)
            prev = len(seen)
            page.keyboard.press("End")
            time.sleep(1)
            current_links = page.locator("article a").evaluate_all(
                "els=>els.map(el=>el.href)"
            )
            seen.update(current_links)
            # print(prev, len(seen))
            if len(seen) == prev:
                break
        return list(seen)
    else:
        _ = tt_scrape(container=container, tt_isCollection=tt_isCollection)
        return _
    return None


def scrapeCollections(platform: str, headless: bool):
    platform = platform.lower()
    username = LOGIN_CREDENTIALS[platform]["username"]
    with authenticated_page(platform, headless) as page:
        if platform == "instagram":
            page.goto(f"https://instagram.com/{username}/saved/")
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
        else:
            page.goto(f"https://tiktok.com/@{username}")
            page.locator("span", has_text="Favorites").first.click()
            page.locator(".TUXButton-label", has_text="Collections").click()
            container = page.locator("#collection-item-list")
            container.wait_for(state="visible")
            return scrollScrape(
                page, platform=platform, container=container, tt_isCollection=False
            )


def scrape_instagram(headless: bool, collection: tuple):
    with authenticated_page("instagram", headless) as page:
        page.goto("https://www.instagram.com" + collection[1])
        page.wait_for_selector("article a", state="attached")
        links = scrollScrape(page, platform="instagram", tt_isCollection=False)
        with open(f"./out/{collection[0]}-instagram-links.json", "w") as f:
            json.dump(links, f)


def scrape_tiktok(headless: bool, collection):
    with authenticated_page("tiktok", headless) as page:
        page.goto(collection[1])
        container = page.locator("#collection-item-list")
        links = scrollScrape(
            page, container=container, platform="tiktok", tt_isCollection=True
        )
        video_links = [l for l in links if "/video/" in l]
        with open(f"./out/{collection[0]}-tiktok-links.json", "w") as f:
            json.dump(video_links, f)


def scrape(site: str, headless: bool, collection):
    if site.lower() not in PRESETS:
        raise RuntimeError(f"Unsupported site: {site}")
    globals()[f"scrape_{site.lower()}"](headless=headless, collection=collection)
    return 0

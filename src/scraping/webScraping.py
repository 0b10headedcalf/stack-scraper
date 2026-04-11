import json
import time
import os
from typing import List
from playwright.sync_api import Page
from camoufox.sync_api import Camoufox
from .. import consts

DIRNAME = consts.DIRNAME
STATEPATHS = consts.STATEPATHS
SETTINGS = consts.SETTINGS
LOGIN_CREDENTIALS = consts.LOGIN_CREDENTIALS
FTS = consts.FTS
PRESETS = consts.PRESETS


def checkState(platform: str):
    return os.path.isfile(STATEPATHS[platform.lower()])


def _scrollAndCollect(
    page: Page, container_sel: str, card_sel: str, delay: float = 1.5
) -> List[tuple]:
    seen = {}
    container = page.locator(container_sel)
    container.wait_for(state="visible")
    while True:
        prev = len(seen)
        cards = container.locator(card_sel)
        for i in range(cards.count()):
            card = cards.nth(i)
            href = card.get_attribute("href")
            if href and href not in seen:
                img = card.locator("img")
                alt = img.get_attribute("alt") if img.count() > 0 else ""
                seen[href] = alt or ""
        page.keyboard.press("End")
        time.sleep(delay)
        cards = container.locator(card_sel)
        for i in range(cards.count()):
            card = cards.nth(i)
            href = card.get_attribute("href")
            if href and href not in seen:
                img = card.locator("img")
                alt = img.get_attribute("alt") if img.count() > 0 else ""
                seen[href] = alt or ""
        print(f"items found: {prev} -> {len(seen)}")
        if len(seen) == prev:
            break
    return [(alt, href) for href, alt in seen.items()]


def scrollUntilLoaded(page: Page, platform: str, context: str = "collection_list"):
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
            print(prev, len(seen))
            if len(seen) == prev:
                break
        return list(seen)
    else:
        if context == "collection_list":
            return _scrollAndCollect(
                page, "div#collection-item-list", "a[href*='/collection/']"
            )
        elif context == "collection_items":
            return _scrollAndCollect(
                page, "div#collection-item-list", "a[href*='/video/']"
            )


def queryCollection(page: Page, platform: str) -> List[str]:
    if platform.lower() == "instagram":
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
        page.locator("span", has_text="Favorites").first.click()
        page.locator(".TUXButton-label", has_text="Collections").click()
        container = page.locator("#collection-item-list")
        container.wait_for(state="visible")
        return scrollUntilLoaded(page, platform)


def scrapeCollections(platform: str, headless: bool):
    _username = LOGIN_CREDENTIALS[platform]["username"]
    email_fill = LOGIN_CREDENTIALS[platform]["email"]
    pass_fill = LOGIN_CREDENTIALS[platform]["password"]
    if platform.lower() == "instagram":
        site_arg = "https://instagram.com/"
        with Camoufox(headless=headless) as browser:
            state_path = STATEPATHS[platform.lower()]
            if checkState(platform):
                context = browser.new_context(storage_state=state_path)
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
                context.storage_state(path=state_path)
            collections = queryCollection(page, platform=platform)
        return collections
    else:
        site_arg = "https://tiktok.com/"
        with Camoufox(headless=headless) as browser:
            state_path = STATEPATHS[platform.lower()]
            if checkState(platform):
                context = browser.new_context(storage_state=state_path)
                page = context.new_page()
                site_arg += "@" + _username
                page.goto(site_arg)
            else:
                context = browser.new_context()
                page = context.new_page()
                page.goto(site_arg + "login/phone-or-email/email/")
                page.locator("[name='username']").fill(email_fill)
                page.locator("[type='password']").fill(pass_fill)
                page.locator("[type='submit']").click()
                page.wait_for_url("**/2sv/**", timeout=120_000)
                print("Waiting for 2FA to be completed...")
                page.wait_for_url(lambda url: "2sv" not in url)
                print("2FA complete")
                page.goto(site_arg)
                context.storage_state(path=state_path)
            collections = queryCollection(page, platform=platform)
        return collections


def scrape_instagram(headless: bool, collection: tuple):
    _username = LOGIN_CREDENTIALS["instagram"]["username"]
    email_fill = LOGIN_CREDENTIALS["instagram"]["email"]
    pass_fill = LOGIN_CREDENTIALS["instagram"]["password"]
    site_arg = "https://instagram.com/"

    with Camoufox(headless=headless) as browser:
        state_path = STATEPATHS["instagram"]
        if checkState("instagram"):
            context = browser.new_context(storage_state=state_path)
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
            context.storage_state(path=state_path)
        target_collection = "https://www.instagram.com" + collection[1]
        page.goto(target_collection)
        page.wait_for_selector("article a", state="attached")
        links = scrollUntilLoaded(page, platform="instagram")
        with open(f"./out/{collection[0]}-videos.json", "w") as f:
            json.dump(links, f)
            print(f"links saved to {str(f)}")
    return None


def scrape_tiktok(headless: bool, collection: tuple):
    site_arg = "https://tiktok.com/"
    email_fill = LOGIN_CREDENTIALS["tiktok"]["email"]
    pass_fill = LOGIN_CREDENTIALS["tiktok"]["password"]

    with Camoufox(headless=headless) as browser:
        state_path = STATEPATHS["tiktok"]
        if checkState("tiktok"):
            context = browser.new_context(storage_state=state_path)
            page = context.new_page()
            page.goto(site_arg)
        else:
            context = browser.new_context()
            page = context.new_page()
            page.goto(site_arg + "login/phone-or-email/email/")
            page.locator("[name='username']").fill(email_fill)
            page.locator("[type='password']").fill(pass_fill)
            page.locator("[type='submit']").click()
            page.wait_for_url("**/2sv/**", timeout=120_000)
            print("Waiting for 2FA to be completed...")
            page.wait_for_url(lambda url: "2sv" not in url)
            print("2FA complete")
            page.goto(site_arg)
            context.storage_state(path=state_path)
        target_collection = "https://www.tiktok.com" + collection[1]
        print(target_collection)
        page.goto(target_collection)
        links = scrollUntilLoaded(page, platform="tiktok", context="collection_items")
        print(links)
        # with open(f"./out/{collection[0]}-videos.json", "w") as f:
        #     json.dump(links, f)
        #     print(f"links saved to {str(f)}")
    return None


def scrape(site: str, headless: bool, collection):
    if site.lower() in PRESETS:
        globals()[f"scrape_{site}"](headless=headless, collection=collection)
    else:
        print("Invalid site query")
        return None

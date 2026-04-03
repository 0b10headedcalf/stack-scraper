# import sys
# print(sys.platform)
import time
from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()

URL = "https://www.instagram.com/darrell.x.cheng/saved/"

browser = playwright.chromium.launch(headless=False, slow_mo=250)

page = browser.new_page(
    java_script_enabled=True,
    viewport = {'width': 1024, 'height': 768}
)

page.goto(URL,wait_until='load')

page.close()
browser.close()
playwright.stop()

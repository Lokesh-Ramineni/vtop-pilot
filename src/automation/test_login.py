from playwright.sync_api import Playwright, expect, BrowserContext
from elements.login_elements import LoginElements
import yaml
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

CONFIG_PATH = ROOT_DIR / "config" / "config.yaml"
CREDENTIALS_PATH = ROOT_DIR / "config" / "credentials.json"
session_storage = ROOT_DIR / "config" / "session.json"

with open(CONFIG_PATH, 'r') as stream:
    config = yaml.safe_load(stream)

with open(CREDENTIALS_PATH, "r", encoding="utf-8") as json_stream:
    credentials = json.load(json_stream)


def verify_login_session(playwright: Playwright) -> BrowserContext:

    try:
        print('\U0001F36A  Validating saved session state silently in the background...')
        silent_browser = playwright.chromium.launch(headless=True)
        context = silent_browser.new_context(storage_state=session_storage)
        page = context.new_page()

        page.goto(config['urls']['content_page'])
        expect(page.locator("span.navbar-text").nth(0)).to_have_text("24MIC7146 (STUDENT)")

        print(" \u2705 Success! Session active.")
        # Return the silent browser instance along with context so it isn't destroyed
        return silent_browser, context
    
    except:
        print(' \u274C  Session expired or missing. Launching visible browser for manual login...')
        # Closing the session check browser
        silent_browser.close()

        # Launching a new browser instance
        visible_browser = playwright.chromium.launch(headless=False)
        context = visible_browser.new_context()
        page = context.new_page()
        login_element = LoginElements(page)

        page.goto(config["urls"]["login_page"])
        print('\U0001F464   Submitting portal credentials...')
        login_element.login(credentials["username"], credentials["password"])

        print('\U0001F4BE   Saving fresh session state to session.json...')
        context.storage_state(path=session_storage)

        expect(page.locator("span.navbar-text").nth(0)).to_have_text("24MIC7146 (STUDENT)")
        page.wait_for_timeout(5000)

        print(" \u2705  Success! Fresh login verified.")
        return visible_browser, context

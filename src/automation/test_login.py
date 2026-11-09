import re
import yaml
import json
import base64
from pathlib import Path
from otp_fetch.otp import OTPFetcher
from solver.cap_solver import solve_captcha
from playwright.sync_api import Playwright, expect, BrowserContext
from elements.login_elements import LoginElements

ROOT_DIR = Path(__file__).resolve().parents[2]

CONFIG_PATH = ROOT_DIR / "config" / "config.yaml"
CREDENTIALS_PATH = ROOT_DIR / "config" / "credentials.json"
session_storage = ROOT_DIR / "config" / "session.json"

with open(CONFIG_PATH, 'r') as stream:
    config = yaml.safe_load(stream)

with open(CREDENTIALS_PATH, "r", encoding="utf-8") as json_stream:
    credentials = json.load(json_stream)

def is_otp_prompt(page) -> bool:
    """True when the 'Additional verification required' alert is shown."""
    try:
        alert = page.locator("span[role='alert']").filter(
            has_text=re.compile(r"Additional verification required", re.I)
        )
        alert.first.wait_for(state="visible", timeout=5000)
        return True
    except Exception:
        return False

def verify_login_session(playwright: Playwright) -> BrowserContext:

    try:
        print('\U0001F36A  Validating saved session state silently in the background...')
        silent_browser = playwright.chromium.launch(headless=True)
        context = silent_browser.new_context(storage_state=session_storage)
        page = context.new_page()

        page.goto(config['urls']['content_page'])
        expect(page.locator("span.navbar-text").nth(0)).to_have_text("24MIC7146 (STUDENT)")

        print("\u2705 Success! Session active.")
        # Return the silent browser instance along with context so it isn't destroyed
        return silent_browser, context
    
    except:
        print('\u274C  Session expired or missing. Launching visible browser for manual login...')
        # Closing the session check browser
        silent_browser.close()

        # Launching a new browser instance
        visible_browser = playwright.chromium.launch(headless=False)
        context = visible_browser.new_context()
        page = context.new_page()
        login_element = LoginElements(page)

        page.goto(config["urls"]["login_page"])
        login_element.login_open()
        
        while True:
            try:
                captcha = page.locator(
                    ".form-control.img-fluid.bg-light.border-0"
                )

                if captcha.count() == 0:
                    print("⚠️ CAPTCHA not found.")
                    print("🔄 Reloading page...")
                    page.reload()
                    continue

                try:
                    expect(captcha).to_be_visible(timeout=5000)
                except AssertionError:
                    print("⚠️ CAPTCHA not visible.")
                    print("🔄 Reloading page...")
                    page.reload()
                    continue

                src = captcha.get_attribute("src")

                if not src:
                    print("⚠️ CAPTCHA src not found.")
                    print("🔄 Reloading page...")
                    page.reload()
                    continue

                base = src.split(",", 1)[1]
                cap = solve_captcha(base)

                print(f"🔐 CAPTCHA solved as: {cap}")
                print("👤 Filling credentials...")

                login_element.login(
                    credentials["username"],
                    credentials["password"],
                    cap
                )

                print("🖱️ Submit completed")
                print(f"🌐 Current URL: {page.url}")

                page.wait_for_timeout(3000)

                print(f"🔎 URL before OTP check: {page.url}")

                if is_otp_prompt(page):
                    print("📧 OTP required. Fetching from email...")
                    try:
                        with OTPFetcher() as otp_fetcher:
                            otp = otp_fetcher.fetch_latest_otp()
                        print(f"🔑 OTP received: {otp}")

                        page.locator("#securityOtpCode").wait_for(state="visible", timeout=5000)
                        page.locator("#securityOtpCode").fill(otp)
                        page.locator("#verifyOtpBtn").click()
                        page.wait_for_timeout(3000)
                        print(f"🌐 URL after OTP: {page.url}")
                    except Exception as e:
                        print(f"❌ OTP step failed: {type(e).__name__}: {e}")
                        raise
                else:
                    print("ℹ️ No OTP prompt detected.")
                
                print("⏳ Checking login result...")

                if "/vtop/content" in page.url:
                    print(f"✅ Login successful: {page.url}")
                    break

                if page.locator("span.navbar-text").count() > 0:
                    print("✅ Login successful")
                    break

                print("⚠️ Login page still visible.")
                print("🔄 Retrying...\n")
                continue

            except Exception as e:
                print(
                    f"❌ Login attempt failed: "
                    f"{type(e).__name__}: {e}"
                )
                
                captcha = page.locator(
                    ".form-control.img-fluid.bg-light.border-0"
                )

                if captcha.count() == 0:
                    print("⚠️ CAPTCHA is absent.")
                    print("🔄 Reloading page...")
                    page.reload()
                else:
                    print("⚠️ CAPTCHA still exists. Retrying without reload...")
                    continue

        try:
            expect(page.locator("h4[class='fw-bold']")).to_be_visible(timeout=3000)
        except:
            pass
        print('\U0001F4BE Saving fresh session state to session.json...')
        context.storage_state(path=session_storage)
        print()
        expect(page.locator("span.navbar-text").nth(0)).to_have_text("24MIC7146 (STUDENT)")
        page.wait_for_timeout(5000)

        print("\u2705  Success! Fresh login verified.")
        return visible_browser, context
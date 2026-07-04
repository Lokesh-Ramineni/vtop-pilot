from playwright.sync_api import Page
import yaml
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = ROOT_DIR / "config" / "config.yaml"
CREDENTIALS_PATH = ROOT_DIR / "config" / "credentials.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as stream:
    config = yaml.safe_load(stream)

with open(CREDENTIALS_PATH, "r", encoding="utf-8") as json_stream:
    credentials = json.load(json_stream)



class LoginElements:
    def __init__(self,page: Page):
        self.page = page
        self.login_btn=self.page.locator(".btn.btn-primary.fw-bold")
        self.username_input=self.page.locator("#username")
        self.password_input=self.page.locator("#password")
        self.submit_btn=self.page.locator("#submitBtn")


    def login(self,username,password):
        self.login_btn.click()
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.page.wait_for_timeout(10000)
        self.submit_btn.click()

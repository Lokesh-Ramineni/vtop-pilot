from playwright.sync_api import Page
from  pathlib import Path
import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = ROOT_DIR / "config" / "config.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as stream:
    config = yaml.safe_load(stream)


class OutingElements:
    def __init__(self,page:Page):
        self.page = page

        self.ham=self.page.get_by_role("button").nth(0)
        self.hostel=self.page.get_by_role("button",name="Hostels")

        self.weekend=self.page.get_by_role("link",name=" Weekend Outing")
        self.weekend_date=self.page.locator('input[name="outingDate"]')
        self.weekend_contact=self.page.locator('input[name="contactNumber"]')
        self.weekend_purpose=self.page.locator('input[name="purposeOfVisit"]')

        self.submit_btn=self.page.get_by_role("button",name="SUBMIT")

        self.general = page.get_by_role("link", name=" General Outing")
        self.general_date=self.page.locator('input[name="outDate"]')
        self.general_in_date=self.page.locator('input[name="inDate"]')

    def common(self):
        self.ham.click()
        self.hostel.click()


    def weekend_outing(self,page):
        self.common()

        self.weekend.click()
        self.weekend_purpose.fill(config['outing']['default_reason'])

        page.evaluate('document.getElementsByName("outingDate")[0].removeAttribute("readonly")')
        self.weekend_date.fill(config['outing']['default_date'])
        self.weekend_contact.fill(config['outing']['default_contact'])

        self.submit_btn.click(force=True)
        self.submit_btn.click()



    def general_outing(self,page):
        self.common()

        self.general.click()

        page.evaluate('document.getElementById("outDate").removeAttribute("readonly")')
        self.general_date.fill(config['outing']['default_from_date'])

        page.evaluate('document.getElementById("inDate").removeAttribute("readonly")')
        self.general_in_date.fill(config['outing']['default_to_date'])

        self.submit_btn.click(force=True)
        self.submit_btn.click()

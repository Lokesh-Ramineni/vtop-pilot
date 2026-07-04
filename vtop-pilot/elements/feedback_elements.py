import yaml
from playwright.sync_api import Page
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = ROOT_DIR / "config" / "config.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as stream:
    config = yaml.safe_load(stream)

class FeedbackPage:
    def __init__(self, page: Page):
        self.page = page
        self.semester_selection=self.page.locator('select[id=semesterSubId]').select_option(config['sem']['default_semester'])
        self.type=self.page.locator('select[id=type]')
        self.course_id=self.page.locator('select[id=courseId]')
        self.table=self.page.locator("table")
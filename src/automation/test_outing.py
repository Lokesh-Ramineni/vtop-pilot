import logging
import yaml
from pathlib import Path
from playwright.sync_api import Page
from elements.outing_elements import OutingElements

ROOT_DIR = Path(__file__).resolve().parents[2]
with open(ROOT_DIR / "config" / "config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)

def run_outing_workflow(page: Page):
    """Handles the user choice menu for outing requests."""
    logging.info("\U0001F6A0 Outing automated module initiated.")
    outing = OutingElements(page)

    # Direct navigation to the outing portal page
    page.goto(config['urls']['content_page'])

    print('\U0001F3D6 1. WEEKEND OUTING')
    print('\U0001F3EC 2. GENERAL OUTING')

    while True:
        try:
            num = int(input('\u2753 Choose an outing type (1-2): '))
            match num:
                case 1:
                    print('\u27A1 Executing Weekend Outing Flow...')
                    outing.weekend_outing(page)
                    break
                case 2:
                    print('\u27A1 Executing General Outing Flow...')
                    outing.general_outing(page)
                    break
                case _:
                    print('\u26A0\uFE0F Choose correct number (1 or 2)')
        except ValueError:
            print('\u274C Invalid input! Please enter an integer.\n')

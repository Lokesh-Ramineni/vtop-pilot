from playwright.sync_api import Page,expect
import base64
def test_scrape_captcha(page: Page):
    page.goto("https://vtop.vitap.ac.in/vtop/login")

    page.locator(".btn.btn-primary.fw-bold").click()
    i=1
    while i<=50:
        try:
            expect(page.locator(".form-control.img-fluid.bg-light.border-0")).to_be_visible()
            element=page.locator(".form-control.img-fluid.bg-light.border-0")
            src=element.get_attribute("src")
            if src is not None:
                with open(f"../data/captcha{i}.png","wb") as f:
                    f.write(base64.b64decode(src.split(",")[1]))
                print(f"Image{i} saved Successfully")
                i = i + 1
            else:
                print("Src not found")
            page.reload()

        except:
            print(f"Not found ")
            page.reload()
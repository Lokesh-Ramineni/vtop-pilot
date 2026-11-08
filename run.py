import sys
from src.automation import mentor_feedback
from src.automation import test_login, test_outing
from src.automation import test_login, test_outing, feedback_details

from playwright.sync_api import sync_playwright

def main():
    print("===============================================")
    print("📱  VTOP PORTAL AUTOMATION DASHBOARD")
    print("===============================================")
    print("⚙️   1. Check / Refresh Login Session Only")
    print("🧳  2. Apply for Outing (Auto-logins if needed)")
    print("📝  3. Auto-Fill Faculty Feedback Forms")
    print("📝  4. Auto-Fill Mentor Feedback Form")
    print("❌  5. Exit")
    print("===============================================")

    while True:
        try:
            choice = int(input("\n❓ Select an operation (1-5): "))
            if choice in [1,2,3,4,5]:
                break
            print("⚠️  Please choose a valid number from 1 to 5.")
        except ValueError:
            print("❌  Invalid entry. Please enter a valid number.")

    if choice == 5:
        print("\n👋 Exiting dashboard. Goodbye!")
        return

    with sync_playwright() as playwright:
        print("\n🌐  Initializing automation environment...")

        try:
            if choice == 1:
                # Runs the dynamic headless check, saves state, then tears down
                browser, context = test_login.verify_login_session(playwright)
                context.close()
                browser.close()
                print("\n🏁  Login check finalized.")

            elif choice == 2:
                # Check current login state
                browser, context = test_login.verify_login_session(playwright)

                print('\U0001F3D6 1. WEEKEND OUTING')
                print('\U0001F3EC 2. GENERAL OUTING')

                num = int(input('\u2753 Choose an outing type (1-2): '))

                while True:
                    try:
                        match num:
                            case 1:
                                print('\u27A1 Executing Weekend Outing Flow...')

                                break
                            case 2:
                                print('\u27A1 Executing General Outing Flow...')

                                break
                            case _:
                                print('\u26A0\uFE0F Choose correct number (1 or 2)')
                    except ValueError:
                        print('\u274C Invalid input! Please enter an integer.\n')

                # If session is valid but ran headlessly, relaunch a visible workspace for user viewing
                if browser.is_connected():
                    context.close()
                    browser.close()

                    print("🌐  Session confirmed. Launching visible browser workspace for Outing workflow...")
                    browser = playwright.chromium.launch(headless=False)
                    context = browser.new_context(storage_state=test_login.session_storage)

                page = context.new_page()
                # Execute the specific outing actions
                test_outing.run_outing_workflow(page,num)

                context.close()
                browser.close()
                print("\n🏁  Outing process finalized.")

            elif choice == 3:

                print("\n🍪 Loading authenticated VTOP session...")

                browser = playwright.chromium.launch(
                    headless=False
                )

                try:
                    context = browser.new_context(
                        storage_state=str(test_login.session_storage)
                    )

                    page = context.new_page()

                    print("\n🌐 Opening VTOP content page...")

                    page.goto(
                        test_login.config["urls"]["content_page"],
                        wait_until="domcontentloaded"
                    )

                    # Verify saved session
                    page.locator(
                        "span.navbar-text"
                    ).nth(0).wait_for(
                        state="visible",
                        timeout=30000
                    )

                    print("\n✅ Existing session loaded successfully.")

                    print(
                        "\n📌 Navigate to Academics → Feedback Form "
                        "in the browser."
                    )

                    # Start feedback capture after form appears
                    feedback_details.run_feedback_workflow(page)

                except Exception as e:

                    print(f"\n❌ Feedback automation failed: {e}")

                finally:

                    browser.close()

            elif choice == 4:

                browser = None
                context = None

                try:
                    browser, context = test_login.verify_login_session(playwright)

                    if context.pages:
                        page = context.pages[0]
                    else:
                        page = context.new_page()

                    mentor_feedback.run_mentor_feedback_workflow(page)

                except Exception as error:
                    print(f"\n❌ Mentor feedback automation failed: {error}")

                finally:
                    if context:
                        context.close()

                    if browser:
                        browser.close()

        except Exception as e:
            # Handle situations where the session is lost or drops mid-execution
            if "session" in str(e).lower() or "not found" in str(e).lower():
                print("\n⚠️  Session Error: The active VTOP session disappeared or timed out.")
                print("💡  Tip: Run Option 1 to establish a fresh login session and solve the Captcha.")
            else:
                print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

import sys
from playwright.sync_api import sync_playwright
# Import your core automation modules
from src.automation import test_login, test_outing
                            #test_feedback)


def main():
    print("===============================================")
    print("📱  VTOP PORTAL AUTOMATION DASHBOARD")
    print("===============================================")
    print("⚙️  1. Check / Refresh Login Session Only")
    print("🧳  2. Apply for Outing (Auto-logins if needed)")
    print("📝  3. Auto-Fill Faculty Feedback Forms")
    print(" ❌ 4. Exit")
    print("===============================================")

    while True:
        try:
            choice = int(input("\n❓ Select an operation (1-4): "))
            if choice in [1,2,3,4]:
                break
            print("⚠️  Please choose a valid number from 1 to 4.")
        except ValueError:
            print("❌  Invalid entry. Please enter a valid number.")

    if choice == 4:
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

                # If session is valid but ran headlessly, relaunch a visible workspace for user viewing
                if browser.is_connected():
                    context.close()
                    browser.close()

                    print("🌐  Session confirmed. Launching visible browser workspace for Outing workflow...")
                    browser = playwright.chromium.launch(headless=False)
                    context = browser.new_context(storage_state=test_login.session_storage)

                page = context.new_page()
                # Execute the specific outing actions
                test_outing.run_outing_workflow(page)

                context.close()
                browser.close()
                print("\n🏁  Outing process finalized.")

            # elif choice == 3:
            #     # Check current login state
            #     browser, context = test_login.verify_login_session(playwright)
            #
            #     # Feedback automation can run completely in headless mode to save time,
            #     # but if you want to watch it click, keep it headed (headless=False)
            #     if browser.is_connected():
            #         context.close()
            #         browser.close()
            #
            #         print("🌐  Session confirmed. Launching browser workspace to process Faculty Feedback...")
            #         browser = playwright.chromium.launch(headless=False)  # Set to True if you want it silent
            #         context = browser.new_context(storage_state=test_login.session_storage)
            #
            #     page = context.new_page()
            #     # Execute the specific feedback actions
            #     test_feedback.run_feedback_workflow(page)
            #
            #     context.close()
            #     browser.close()
            #     print("\n🏁  Faculty feedback submission process finalized.")

        except Exception as e:
            # Handle situations where the session is lost or drops mid-execution
            if "session" in str(e).lower() or "not found" in str(e).lower():
                print("\n⚠️  Session Error: The active VTOP session disappeared or timed out.")
                print("💡  Tip: Run Option 1 to establish a fresh login session and solve the Captcha.")
            else:
                print(f"\n❌ An unexpected error occurred: {e}")
                # Optional: uncomment the line below if you want to see raw tracebacks while debugging
                # import traceback; traceback.print_exc()


if __name__ == "__main__":
    main()

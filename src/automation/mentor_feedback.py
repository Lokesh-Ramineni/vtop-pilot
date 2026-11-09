import re
import yaml
from pathlib import Path

from elements.mentor_feedback_elements import MentorFeedbackPage
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config" / "config.yaml"

def load_mentor_config():

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_PATH}"
        )

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    settings = config.get("mentor_feedback")

    if not isinstance(settings, dict):
        raise ValueError(
            "Missing 'mentor_feedback' section in config.yaml."
        )

    rating_map = {
        "Needs Improvement": "1",
        "Satisfactory": "2",
        "Good": "3",
        "Very Good": "4",
        "Excellent": "5"
    }

    rating = settings.get("rating")

    if not isinstance(rating, str):
        raise ValueError(
            "mentor_feedback.rating must be a string."
        )

    rating = rating.strip()

    if rating not in rating_map:
        raise ValueError(
            f"Invalid mentor_feedback.rating: '{rating}'.\n"
            f"Valid values: {', '.join(rating_map.keys())}"
        )

    message = settings.get("MESSAGE")

    if not isinstance(message, str):
        raise ValueError(
            "mentor_feedback.MESSAGE must be a string."
        )

    if not re.fullmatch(r"[a-zA-Z0-9\s?@#$%^&*()]+", message):
        raise ValueError(
            "Invalid mentor_feedback.MESSAGE.\n"
            "The form only accepts letters, numbers, spaces and "
            "these characters: ? @ # $ % ^ & * ( )"
        )

    return {
        "rating": rating,
        "rating_value": rating_map[rating],
        "message": message
    }


def ask_attendance(feedback):

    options = feedback.get_attendance_options()

    print("\nHow many mentoring meetings have you attended?")

    for index, option in enumerate(options, start=1):
        print(f"{index}. {option['label']}")

    while True:

        choice = input("\nEnter your choice: ").strip()

        if not choice.isdigit():
            print("❌ Enter a valid option number.")
            continue

        choice = int(choice)

        if 1 <= choice <= len(options):
            selected = options[choice - 1]
            feedback.select_attendance(selected["value"])

            print(
                f"✅ Attendance selected: {selected['label']}"
            )

            return selected["value"]

        print("❌ Invalid choice. Try again.")


def ask_reason(feedback):

    options = feedback.get_reason_options()

    print("\nWhy were you unable to attend the prescribed meetings?")

    for index, option in enumerate(options, start=1):
        print(f"{index}. {option['label']}")

    while True:

        choice = input("\nEnter your choice: ").strip()

        if not choice.isdigit():
            print("❌ Enter a valid option number.")
            continue

        choice = int(choice)

        if 1 <= choice <= len(options):

            selected = options[choice - 1]

            feedback.select_reason(selected["value"])

            print(f"✅ Reason selected: {selected['label']}")

            if selected["value"].strip().lower().startswith("other"):

                while True:
                    other_message = input(
                        "Please specify your reason: "
                    ).strip()

                    if not other_message:
                        print("❌ Reason cannot be empty.")
                        continue

                    if len(other_message) > 200:
                        print("❌ Maximum 200 characters allowed.")
                        continue

                    feedback.fill_other_reason(other_message)
                    break

            return

        print("❌ Invalid choice. Try again.")


def validate_mentor_questions(feedback, settings):

    questions = feedback.get_active_questions()

    if not questions:
        raise RuntimeError(
            "No active mentor feedback questions were detected."
        )

    rating_count = 0
    text_count = 0

    for question in questions:

        question_id = question["id"]
        question_type = question["type"]

        if question_type == "MCQ":

            options = feedback.get_radio_options(question_id)

            if options.count() == 0:
                raise RuntimeError(
                    f"No rating options found for question {question_id}."
                )

            matching_rating = feedback.page.locator(
                f"#section2 input[type='radio']"
                f"[name='{question_id}']"
                f"[value='{settings['rating_value']}']"
            )

            if matching_rating.count() == 0:
                raise ValueError(
                    f"Configured rating '{settings['rating']}' "
                    f"is unavailable for question {question_id}."
                )

            rating_count += 1

        elif question_type == "TEXT":

            text_input = feedback.get_text_input(question_id)

            if text_input.count() == 0:
                raise RuntimeError(
                    f"Text input not found for question {question_id}."
                )

            rating_count += 0
            text_count += 1

        else:
            raise RuntimeError(
                f"Unexpected mentor question type: {question_type}"
            )

    print("\n🔎 Mentor form validation completed.")
    print(f"   Rating questions: {rating_count}")
    print(f"   Text questions: {text_count}")

    return questions


def fill_mentor_questions(feedback, settings):

    questions = validate_mentor_questions(feedback, settings)

    print("\n✍️ Filling mentor feedback...")

    for question in questions:

        question_id = question["id"]
        question_type = question["type"]

        if question_type == "MCQ":

            feedback.select_rating(
                question_id,
                settings["rating_value"]
            )

        elif question_type == "TEXT":

            feedback.fill_message(
                question_id,
                settings["message"]
            )

    print("\n✅ Mentor feedback filled successfully.")
    print(f"   Rating: {settings['rating']}")
    print(f"   Message: {settings['message']}")

def run_mentor_feedback_workflow(page: Page):

    print("\n======================================")
    print("       MENTOR FEEDBACK WORKFLOW")
    print("======================================")

    settings = load_mentor_config()

    feedback = MentorFeedbackPage(page)

    print(
        "\n🌐 Navigate to the Mentee Feedback Form "
        "in the opened browser."
    )

    feedback.wait_for_feedback_page()

    semesters = feedback.get_semester_options()

    if not semesters:
        raise RuntimeError(
            "No semesters are available in the mentor feedback form."
        )

    print("\n📅 Available semesters:")

    for index, semester in enumerate(semesters, start=1):
        print(f"{index}. {semester['label']}")

    while True:

        choice = input("\nSelect semester number: ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(semesters):
            selected_semester = semesters[int(choice) - 1]
            break

        print("❌ Invalid semester selection.")

    print(
        f"\n📅 Selected semester: {selected_semester['label']}"
    )

    try:
        with page.expect_response(
            lambda response: (
                "getEmpIdAndDepartId" in response.url
                and response.request.method == "POST"
            ),
            timeout=30000
        ):
            feedback.select_semester(selected_semester["value"])

    except PlaywrightTimeoutError:

        print(
            "⚠️ Semester loading response was not detected. "
            "Checking the form..."
        )

    feedback.wait_for_questions()

    print("\n✅ Mentor feedback form loaded.")

    attendance = ask_attendance(feedback)

    if attendance.strip().lower() in ["none", "one"]:

        print(
            "\n⚠️ You have attended fewer than two mentoring meetings."
        )

        ask_reason(feedback)

        print("\n✅ Required attendance reason has been filled.")

    else:
        feedback.page.wait_for_function(
            """() => {
                const block = document.querySelector('#feedbackBlock');
                return block &&
                    getComputedStyle(block).display !== 'none' &&
                    document.querySelectorAll(
                        "#feedbackBlock input[name='questionnumber']:not(:disabled)"
                    ).length > 0;
            }""",
            timeout=15000
        )

        fill_mentor_questions(feedback, settings)

    print("\n======================================")
    print("🎉 MENTOR FORM IS READY")
    print("======================================")

    print("\nReview the answers in the browser.")
    print("Submit the form manually when you are satisfied.")

    confirmation = input(
        "\nAfter submitting and seeing VTOP's success message, "
        "type SUBMITTED: "
    ).strip()

    if confirmation.upper() == "SUBMITTED":
        print("\n✅ Mentor feedback submission confirmed by user.")
    else:
        print("\n⛔ Workflow stopped. Submission not confirmed.")

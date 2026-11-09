
import json
from pathlib import Path

import yaml
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from elements.feedback_elements import FeedbackPage


ROOT_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = ROOT_DIR / "data"
OUTPUT_FILE = OUTPUT_DIR / "feedback_dropdowns.json"
CONFIG_PATH = ROOT_DIR / "config" / "config.yaml"


def load_feedback_config():

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_PATH}"
        )

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    if not isinstance(config, dict) or not isinstance(
        config.get("feedback"), dict
    ):
        raise ValueError(
            "Missing or invalid 'feedback' section in config.yaml."
        )

    settings = config["feedback"]

    rating_map = {
        "Needs Improvement": "1",
        "Satisfactory": "2",
        "Good": "3",
        "Very Good": "4",
        "Excellent": "5"
    }

    valid_ratings = list(rating_map.keys())

    # Validate default rating.
    default_rating = settings.get("default_rating")

    if not isinstance(default_rating, str):
        raise ValueError(
            "Invalid config.yaml value: feedback.default_rating "
            "must be a rating string."
        )

    default_rating = default_rating.strip()

    if default_rating not in valid_ratings:
        raise ValueError(
            f"Invalid spelling/value for feedback.default_rating: "
            f"'{default_rating}'.\n"
            f"Valid ratings are: {', '.join(valid_ratings)}"
        )

    # Validate category-specific ratings.
    category_ratings = {}

    for category in ["THEORY", "LAB", "LAB_FACILITY"]:

        value = settings.get(category)

        if not isinstance(value, str):
            raise ValueError(
                f"Invalid config.yaml value: feedback.{category} "
                f"must be a rating string or 'NONE'."
            )

        value = value.strip()

        if value.upper() != "NONE" and value not in valid_ratings:
            raise ValueError(
                f"Invalid spelling/value for feedback.{category}: "
                f"'{value}'.\n"
                f"Use 'NONE' or one of: {', '.join(valid_ratings)}"
            )

        category_ratings[category] = value

    auto_submit = settings.get("auto_submit")

    if not isinstance(auto_submit, bool):
        raise ValueError(
            "Invalid config.yaml value: feedback.auto_submit "
            "must be true or false."
        )

    if "MESSAGE" not in settings:
        raise ValueError(
            "Missing config.yaml value: feedback.MESSAGE"
        )

    message = settings["MESSAGE"]

    if not isinstance(message, str):
        raise ValueError(
            "Invalid config.yaml value: feedback.MESSAGE "
            "must be a string."
        )

    return {
        "auto_submit": auto_submit,
        "default_rating": default_rating,
        "rating_map": rating_map,
        "category_ratings": category_ratings,
        "message": message
    }


def get_category_rating(feedback_type, settings):

    category_rating = settings["category_ratings"][feedback_type]

    if category_rating.upper() == "NONE":
        selected_rating = settings["default_rating"]
    else:
        selected_rating = category_rating

    rating_value = settings["rating_map"][selected_rating]

    print(f"\n⭐ {feedback_type} rating: {selected_rating}")

    return selected_rating, rating_value


def select_and_wait(page, locator, value, endpoint):

    try:
        with page.expect_response(
            lambda response: (
                endpoint in response.url
                and response.request.method == "POST"
            ),
            timeout=30000
        ):
            locator.select_option(value=value)

    except PlaywrightTimeoutError:

        print(
            f"⚠️ {endpoint} response was not detected. "
            "Checking the dropdown contents..."
        )

    page.wait_for_timeout(1000)


def capture_courses(page, feedback):

    captured_data = {
        "semesters": [],
        "feedback_types": [],
        "courses_by_semester": []
    }

    print("\n📅 Capturing available semesters...")

    semesters = feedback.get_semester_options()
    captured_data["semesters"] = semesters

    print(f"✅ Found {len(semesters)} semesters")

    for semester in semesters:
        print(f"   - {semester['label']}")

    print("\n📝 Capturing feedback types...")

    feedback_types = feedback.get_feedback_type_options()
    captured_data["feedback_types"] = feedback_types

    print(f"✅ Found {len(feedback_types)} feedback types")

    for feedback_type in feedback_types:
        print(f"   - {feedback_type['label']}")

    for semester in semesters:

        print("\n======================================")
        print(f"📅 Semester: {semester['label']}")
        print("======================================")

        feedback.select_semester(semester["value"])

        semester_data = {
            "semester": semester,
            "feedback_types": []
        }

        for feedback_type in feedback_types:

            print(
                f"\n🔍 Loading courses for "
                f"{feedback_type['label']}..."
            )

            try:
                with page.expect_response(
                    lambda response: (
                        "getCourses" in response.url
                        and response.request.method == "POST"
                    ),
                    timeout=30000
                ):
                    feedback.select_feedback_type(
                        feedback_type["value"]
                    )

            except PlaywrightTimeoutError:

                print(
                    "⚠️ getCourses response was not detected. "
                    "Checking the course dropdown..."
                )

            page.wait_for_timeout(1000)

            courses = feedback.get_course_options()

            print(
                f"✅ {len(courses)} courses found "
                f"for {feedback_type['label']}"
            )

            for course in courses:
                print(f"   - {course['label']}")

            semester_data["feedback_types"].append({
                "feedback_type": feedback_type,
                "courses": courses
            })

        captured_data["courses_by_semester"].append(
            semester_data
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as json_file:

        json.dump(
            captured_data,
            json_file,
            indent=4,
            ensure_ascii=False
        )

    print("\n======================================")
    print("🎉 FEEDBACK DROPDOWN CAPTURE COMPLETED")
    print("======================================")

    print(f"📁 JSON saved at: {OUTPUT_FILE}")

    return captured_data


def validate_form_questions(feedback, feedback_type, rating_value):

    question_ids = feedback.get_question_ids()

    if not question_ids:
        raise RuntimeError(
            f"No questions were loaded for {feedback_type}. "
            "The form cannot be filled."
        )

    radio_count = 0
    text_count = 0

    for question_id in question_ids:

        radio_options = feedback.get_radio_options(question_id)
        text_input = feedback.get_text_input(question_id)

        if radio_options.count() > 0:

            rating_exists = radio_options.evaluate_all(
                "(elements, value) => "
                "elements.some(element => element.value === value)",
                rating_value
            )

            if not rating_exists:
                raise ValueError(
                    f"Rating value '{rating_value}' is not available "
                    f"for question ID {question_id} in {feedback_type}.\n"
                    "The form options may have changed. "
                    "No answers have been filled."
                )

            radio_count += 1

        elif text_input.count() > 0:
            text_count += 1

        else:
            raise RuntimeError(
                f"Unknown question type detected.\n"
                f"Feedback type: {feedback_type}\n"
                f"Question ID: {question_id}\n"
                "The form structure may have changed. "
                "No answers have been filled."
            )

    print("\n🔎 Form validation completed.")
    print(f"   Rating questions: {radio_count}")
    print(f"   Text questions: {text_count}")
    print(f"   Total questions: {len(question_ids)}")

    return question_ids, radio_count, text_count


def wait_after_submission(page, feedback):

    print("\n⏳ Waiting for VTOP to close its popup and refresh...")

    page.wait_for_timeout(4000)

    try:
        feedback.wait_for_feedback_page()

    except PlaywrightTimeoutError:

        raise RuntimeError(
            "VTOP submission was received, but the feedback page "
            "did not become available again after the refresh."
        )

    print("✅ VTOP page is ready for the next course.")


def fill_feedback_form(page, feedback, feedback_type, settings):

    selected_rating, rating_value = get_category_rating(
        feedback_type,
        settings
    )

    message = settings["message"]

    print("\n🔍 Validating the loaded feedback form...")

    # Validate every question before filling any answer.
    question_ids, radio_count, text_count = (
        validate_form_questions(
            feedback,
            feedback_type,
            rating_value
        )
    )

    print("\n✍️ Filling feedback form...")

    for question_id in question_ids:

        radio_options = feedback.get_radio_options(question_id)
        text_input = feedback.get_text_input(question_id)

        if radio_options.count() > 0:

            feedback.select_rating(
                question_id,
                rating_value
            )

        elif text_input.count() > 0:

            feedback.fill_message(
                question_id,
                message
            )

    print("\n✅ Feedback form filled successfully.")
    print(f"   Rating: {selected_rating}")
    print(f"   Rating questions filled: {radio_count}")
    print(f"   Text questions filled: {text_count}")


    if settings["auto_submit"]:

        print("\n⏳ Review period: 10 seconds.")

        for remaining in range(10, 0, -1):
            print(f"   Submitting in {remaining} seconds...")
            page.wait_for_timeout(1000)

        print("\n📤 Clicking the first Submit button...")

        try:
            with page.expect_response(
                lambda response: (
                    "onSave" in response.url
                    and response.request.method == "POST"
                ),
                timeout=30000
            ):
                feedback.submit_feedback()

        except PlaywrightTimeoutError:

            raise RuntimeError(
                "Feedback submission response was not detected "
                "after clicking Submit."
            )

        print("✅ Submission request received.")

        wait_after_submission(page, feedback)

        return True

    print("\n🛑 Auto-submit is disabled.")
    print("Review the answers in the browser.")
    print("Submit the form manually.")
    print("VTOP will handle its confirmation popup automatically.")

    confirmation = input(
        "\nAfter VTOP has completed the submission and refresh, "
        "type SUBMITTED to continue: "
    ).strip()

    if confirmation.upper() != "SUBMITTED":
        print("\n⛔ Workflow stopped by user.")
        return False

    wait_after_submission(page, feedback)

    return True

def fill_courses_by_type(
    page,
    feedback,
    semester_value,
    feedback_type,
    settings
):

    print("\n======================================")
    print(f"📝 Processing {feedback_type}")
    print("======================================")

    # Select semester and feedback type.
    feedback.select_semester(semester_value)

    select_and_wait(
        page,
        feedback.feedback_type,
        feedback_type,
        "getCourses"
    )

    courses = feedback.get_course_options()

    if not courses:
        print(
            f"⚠️ No courses found for {feedback_type}. "
            "Skipping this feedback type."
        )
        return True

    for index, course in enumerate(courses, start=1):

        print("\n--------------------------------------")
        print(
            f"📚 Course {index}/{len(courses)}: "
            f"{course['label']}"
        )
        print("--------------------------------------")

        feedback.select_semester(semester_value)

        select_and_wait(
            page,
            feedback.feedback_type,
            feedback_type,
            "getCourses"
        )

        # Load the selected course.
        select_and_wait(
            page,
            feedback.course_id,
            course["value"],
            "getDetails"
        )

        # Wait for either questions or an already-submitted message.
        try:
            feedback.wait_for_form_or_already_submitted(
                timeout=30000
            )

        except PlaywrightTimeoutError:

            raise RuntimeError(
                f"Feedback form did not load for course: "
                f"{course['label']}.\n"
                "Neither questions nor an already-submitted message "
                "was detected."
            )

        # Skip courses that already have feedback.
        if feedback.is_already_submitted():

            print(
                f"\n⏭️ Feedback already submitted for "
                f"{course['label']}. Skipping this course."
            )

            continue

        should_continue = fill_feedback_form(
            page,
            feedback,
            feedback_type,
            settings
        )

        if not should_continue:
            return False

    return True


def fill_all_feedback_types(
    page,
    feedback,
    semester_value,
    settings
):

    for feedback_type in [
        "THEORY",
        "LAB",
        "LAB_FACILITY"
    ]:

        should_continue = fill_courses_by_type(
            page,
            feedback,
            semester_value,
            feedback_type,
            settings
        )

        if not should_continue:
            print("\n⛔ Feedback workflow stopped.")
            return

    print("\n======================================")
    print("🎉 ALL FEEDBACK TYPES PROCESSED")
    print("======================================")


def run_feedback_workflow(page: Page):

    print("\n📝 Starting Feedback Workflow...")

    # Validate config before interacting with forms.
    settings = load_feedback_config()

    feedback = FeedbackPage(page)

    print(
        "\n🌐 Navigate to the VTOP Feedback Form "
        "in the opened browser."
    )

    feedback.wait_for_feedback_page()

    print("\n✅ Feedback form detected.")

    selected_semester = feedback.semester_selection.input_value()

    if not selected_semester:
        raise RuntimeError(
            "No semester is selected in the feedback form."
        )

    capture_courses(page, feedback)
    feedback.select_semester(selected_semester)

    fill_all_feedback_types(
        page,
        feedback,
        selected_semester,
        settings
    )

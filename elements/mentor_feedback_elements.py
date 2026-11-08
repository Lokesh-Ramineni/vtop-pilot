
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class MentorFeedbackPage:

    def __init__(self, page):
        self.page = page

        # Semester dropdown
        self.semester_selection = page.locator("#semesterSubId")

        # Dynamic form
        self.section = page.locator("#section2")

        # Submit button
        self.submit_button = page.locator(
            "#FeedbackForm button#submit"
        )

    def wait_for_feedback_page(self):
        self.semester_selection.wait_for(
            state="visible",
            timeout=30000
        )

    def get_semester_options(self):
        return self.semester_selection.locator(
            "option"
        ).evaluate_all(
            """options => options
                .filter(option => option.value !== "")
                .map(option => ({
                    value: option.value,
                    label: option.textContent.trim()
                }))
            """
        )

    def select_semester(self, value):
        self.semester_selection.select_option(value=value)

    def wait_for_questions(self):
        self.page.wait_for_function(
            """() => {
                return document.querySelectorAll(
                    "#section2 input[name='questionnumber']:not(:disabled)"
                ).length > 0;
            }""",
            timeout=30000
        )

    def get_active_questions(self):
        return self.page.locator(
            "#section2 input[name='questionnumber']:not(:disabled)"
        ).evaluate_all(
            """elements => elements.map(element => ({
                id: element.value,
                type: element.dataset.type
            }))"""
        )

    def get_attendance_options(self):
        return self.page.locator(
            "#section2 input.gate-attend"
        ).evaluate_all(
            """elements => elements.map(element => ({
                value: element.value,
                label: element.parentElement.textContent.trim()
            }))"""
        )

    def select_attendance(self, value):
        self.page.locator(
            "#section2 input.gate-attend"
        ).filter(
            has=self.page.locator(f"xpath=..")
        )

        self.page.locator(
            f"#section2 input.gate-attend[value='{value}']"
        ).check()

    def get_reason_options(self):
        return self.page.locator(
            "#section2 input.reason-radio"
        ).evaluate_all(
            """elements => elements.map(element => ({
                value: element.value,
                label: element.parentElement.textContent.trim()
            }))"""
        )

    def select_reason(self, value):
        self.page.locator(
            f"#section2 input.reason-radio[value='{value}']"
        ).check()

    def fill_other_reason(self, message):
        self.page.locator("#otherText").fill(message)

    def get_radio_options(self, question_id):
        return self.page.locator(
            f"#section2 input[type='radio'][name='{question_id}']"
        )

    def get_text_input(self, question_id):
        return self.page.locator(
            f"#section2 input[type='text'][name='{question_id}']"
        )

    def select_rating(self, question_id, rating_value):
        self.page.locator(
            f"#section2 input[type='radio']"
            f"[name='{question_id}'][value='{rating_value}']"
        ).check()

    def fill_message(self, question_id, message):
        self.get_text_input(question_id).fill(message)

    def submit_feedback(self):
        self.submit_button.click()

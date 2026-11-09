import yaml
from pathlib import Path
from playwright.sync_api import Page


ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "config.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as stream:
    config = yaml.safe_load(stream)


class FeedbackPage:

    def __init__(self, page: Page):
        self.page = page

        # Dropdown elements
        self.semester_selection = page.locator("#semesterSubId")
        self.feedback_type = page.locator("#type")
        self.course_id = page.locator("#courseId")

    def wait_for_feedback_page(self):

        print("⏳ Waiting for semester dropdown...")

        try:
            self.semester_selection.wait_for(
                state="visible",
                timeout=180000
            )

            self.feedback_type.wait_for(
                state="visible",
                timeout=30000
            )

            self.course_id.wait_for(
                state="visible",
                timeout=30000
            )

            print("✅ All three feedback dropdowns detected.")

        except Exception as e:

            print("❌ Feedback form detection failed.")
            print("Current URL:", self.page.url)
            print("Error:", str(e))

            raise

    def get_semester_options(self):
        """Capture all available semester options."""
        return self._get_options(self.semester_selection)

    def get_feedback_type_options(self):
        """Capture THEORY, LAB, LAB_FACILITY, etc."""
        return self._get_options(self.feedback_type)

    def get_course_options(self):
        """Capture courses currently loaded in the dropdown."""
        return self._get_options(self.course_id)

    @staticmethod
    def _get_options(locator):
        """Extract only actual dropdown option values and labels."""

        options = []

        for option in locator.locator("option").all():

            value = (option.get_attribute("value") or "").strip()
            label = option.inner_text().strip()

            # Ignore placeholder options
            if not value or not label:
                continue

            options.append({
                "label": label,
                "value": value
            })

        return options

    def select_semester(self, semester_value):
        self.semester_selection.select_option(
            value=semester_value
        )

    def select_feedback_type(self, type_value):
        self.feedback_type.select_option(
            value=type_value
        )

    def wait_for_course_dropdown(self):
        """Wait for the course dropdown to be populated."""
        self.course_id.wait_for(state="visible")

        self.page.wait_for_function(
            """() => {
                const select = document.querySelector('#courseId');
                return select && select.options.length > 0;
            }""",
            timeout=30000
        )

    def wait_for_questions(self):
        self.page.wait_for_function(
            """() => {
                return document.querySelectorAll(
                    "#section2 input[name='questionnumber']"
                ).length > 0;
            }""",
            timeout=30000
        )

    def get_question_ids(self):
        return self.page.locator(
            "#section2 input[name='questionnumber']"
        ).evaluate_all(
            "(elements) => elements.map(el => el.value)"
        )

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
        self.page.locator(
            "#section2 button#submit"
        ).click()

        
    def wait_for_form_or_already_submitted(self, timeout=30000):
        self.page.wait_for_function(
            """() => {
                const questions = document.querySelectorAll(
                    "#section2 input[name='questionnumber']"
                );

                const pageText = document.body.innerText.toLowerCase();

                const alreadySubmitted = pageText.includes(
                    "you have already given feedback"
                );

                return questions.length > 0 || alreadySubmitted;
            }""",
            timeout=timeout
        )


    def is_already_submitted(self):
        message = self.page.get_by_text(
            "You have already given Feedback",
            exact=False
        )

        return message.count() > 0 and message.first.is_visible()


    def click_confirmation_submit(self):
        # SweetAlert 2
        sweetalert2_button = self.page.locator(
            ".swal2-popup:visible .swal2-confirm"
        )

        if sweetalert2_button.count() > 0:
            sweetalert2_button.first.click()
            return True

        # SweetAlert 1
        sweetalert1_button = self.page.locator(
            ".sweet-alert:visible button.confirm"
        )

        if sweetalert1_button.count() > 0:
            sweetalert1_button.first.click()
            return True

        # Bootstrap modal
        modal_button = self.page.locator(
            ".modal.show button:visible"
        ).filter(has_text="Submit")

        if modal_button.count() > 0:
            modal_button.first.click()
            return True

        # Accessible dialog fallback
        dialog_button = self.page.get_by_role(
            "dialog"
        ).get_by_role(
            "button",
            name="Submit",
            exact=True
        )

        if dialog_button.count() > 0:
            dialog_button.first.click()
            return True

        return False

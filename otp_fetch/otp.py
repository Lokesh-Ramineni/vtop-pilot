import imaplib
import email
import re
import time
from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parents[1]
email_app = ROOT_DIR / "config" / "email_app.json"

with open(email_app, "r", encoding="utf-8") as json_stream:
    details = json.load(json_stream)

EMAIL = details["user_email"]
APP_PASSWORD = details["app_password"]

FROM = details["from"]
SUBJECT = details["subject"]

class OTPFetcher:
    def __init__(self):
        self.mail = imaplib.IMAP4_SSL(details["imap_server"])
        self.mail.login(EMAIL, APP_PASSWORD)
        self.mail.select("INBOX")

    def remember_last_email(self):
        _, data = self.mail.search(
            None,
            f'(FROM "{FROM}" SUBJECT "{SUBJECT}")'
        )

        ids = data[0].split()

        if ids:
            self.last_seen = ids[-1]
        else:
            self.last_seen = None

        print("Last OTP mail:", self.last_seen)

    def wait_for_new_otp(self, timeout=60):
        start = time.time()

        while time.time() - start < timeout:

            time.sleep(2)

            self.mail.noop()

            _, data = self.mail.search(
                None,
                f'(FROM "{FROM}" SUBJECT "{SUBJECT}")'
            )

            ids = data[0].split()

            if not ids:
                continue

            latest = ids[-1]

            if latest != self.last_seen:

                print("New OTP mail received.")

                _, msg_data = self.mail.fetch(latest, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])

                body = ""

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() in ("text/plain", "text/html"):
                            payload = part.get_payload(decode=True)

                            if payload:
                                body += payload.decode(
                                    part.get_content_charset() or "utf-8",
                                    errors="ignore"
                                )
                else:
                    payload = msg.get_payload(decode=True)

                    if payload:
                        body = payload.decode(
                            msg.get_content_charset() or "utf-8",
                            errors="ignore"
                        )

                otp = re.search(r"\b(\d{6})\b", body)

                if otp:
                    return otp.group(1)

        raise TimeoutError("OTP email did not arrive.")

    def close(self):
        self.mail.logout()
import os
import re
import time
import email
import imaplib
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

# ---------------------------------------------------------
# Load .env
# ---------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / "config" / ".env"

load_dotenv(ENV_PATH)

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

if not EMAIL:
    raise RuntimeError("EMAIL not found in .env")

if not APP_PASSWORD:
    raise RuntimeError("APP_PASSWORD not found in .env")

# ---------------------------------------------------------

IMAP_SERVER = "imap.gmail.com"

FROM_EMAIL = "noreply.sdc@vitap.ac.in"
EXPECTED_SUBJECT = "VTOP Login OTP Needed"


class OTPFetcher:

    def __init__(self):
        try:
            self.mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            self.mail.login(EMAIL, APP_PASSWORD)
            self.mail.select("INBOX")

        except imaplib.IMAP4.error as e:
            raise RuntimeError(f"Failed to login to Gmail: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def fetch_latest_otp(self, timeout=90, poll_interval=2):

        start = time.time()

        while time.time() - start < timeout:

            self.mail.select("INBOX")


            date_str = (datetime.now() - timedelta(minutes=5)).strftime("%d-%b-%Y")
            status, data =self.mail.search(None, f'(FROM "{FROM_EMAIL}" SINCE "{date_str}")')

            if status != "OK":
                time.sleep(poll_interval)
                continue

            ids = data[0].split()

            if not ids:
                time.sleep(poll_interval)
                continue

            latest = ids[-1]

            status, msg_data = self.mail.fetch(latest, "(RFC822)")

            if status != "OK":
                time.sleep(poll_interval)
                continue

            msg = email.message_from_bytes(msg_data[0][1])

            subject = msg.get("Subject", "")

            if EXPECTED_SUBJECT not in subject:
                time.sleep(poll_interval)
                continue

            body = ""

            if msg.is_multipart():

                for part in msg.walk():

                    if part.get_content_type() not in (
                        "text/plain",
                        "text/html"
                    ):
                        continue

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
                end=time.time()
                return otp.group(1)

            time.sleep(poll_interval)

        raise TimeoutError("OTP email did not arrive.")

    def close(self):

        try:
            self.mail.close()
        except Exception:
            pass

        try:
            self.mail.logout()
        except Exception:
            pass
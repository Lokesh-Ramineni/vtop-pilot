# VTOP PILOT (Automation Script) 🚀

An automated Python script for the VIT-AP VTOP portal. It handles logins (including captcha and email OTP), faculty feedback, mentor feedback, and hostel outing requests from a simple terminal dashboard.

## 🎯 Project Purpose

- **⚡ Eliminating the Hectic Feedback Forms:** Skip the time-consuming end-of-semester process. The script fills the repetitive radio buttons and mandatory text fields for every course (Theory, Lab and Lab Facility) and for the mentor feedback form.

- **🏃 Hassle-Free Last-Minute Outings:** Removes the client-side `readonly` restriction on the date fields so outing requests can be filled in and submitted without the date picker getting in the way.

- **🔐 Hands-Free Login:** Solves the login captcha with a bundled offline model and fetches the email OTP from Gmail, so you rarely have to type anything.

### 1. The End-of-Semester Feedback Grind 📝

- **The Problem:** Every semester you are blocked from viewing your grades or timetable until you fill out feedback forms for every course and for your mentor. Clicking 20+ repetitive radio buttons per course takes forever.

- **The Solution:** The script reads your ratings from `config.yaml`, validates the form before touching it, fills every question, and (optionally) submits and moves on to the next course.

### 2. Last-Minute Outing Applications 🏃💨

- **The Problem:** VTOP's date fields are read-only and driven by a date picker, which makes sudden weekend plans awkward to submit.

- **The Solution:** The script removes the `readonly` attribute from the date inputs, fills your configured values and clicks **SUBMIT**.

## 🌟 Features

- **Automated Login:** Reuses a saved session when valid, otherwise logs in automatically with captcha solving and email OTP.
- **Offline Captcha Solver:** A small CNN implemented in pure NumPy/SciPy (no PyTorch or TensorFlow needed) reads the 6-character captcha. Failed attempts retry automatically.
- **Email OTP Handling:** Detects VTOP's "Additional verification required" prompt, reads the OTP from Gmail over IMAP, and submits it.
- **Faculty Feedback Automation:** Fills Theory, Lab and Lab Facility feedback for every course in the selected semester, skipping courses that are already submitted.
- **Mentor Feedback Automation:** Fills the mentee feedback form, including the attendance and "reason for missing meetings" questions.
- **Outing Management:** Automates Weekend Outing and General Outing requests.
- **Persistent Sessions:** Saves browser state to `config/session.json` so you don't log in on every run.

## 📁 Project Structure

```text
vtop-pilot/
├── config/
│   ├── config.yaml                # URLs, feedback / mentor / outing settings
│   ├── .env                       # Gmail address + app password (OTP) — you create this
│   ├── credentials.json           # VTOP username/password — you create this
│   ├── session.json               # Saved browser session (auto-generated)
│   ├── example_credentials.json
│   ├── example_email_app.json
│   └── example_session.json
│
├── data/                          # Generated output (git-ignored)
│   └── feedback_dropdowns.json    # Captured semesters / feedback types / courses
│
├── elements/                      # Page objects (selectors + small actions)
│   ├── login_elements.py
│   ├── feedback_elements.py
│   ├── mentor_feedback_elements.py
│   └── outing_elements.py
│
├── otp_fetch/
│   └── otp.py                     # Gmail IMAP OTP fetcher
│
├── scraper/
│   └── test_scrape.py             # Collects captcha images (for model training)
│
├── solver/
│   └── cap_solver.py              # Offline CNN captcha solver
│
├── src/
│   └── automation/
│       ├── test_login.py          # Session check + login + captcha + OTP
│       ├── test_outing.py         # Outing workflow
│       ├── feedback_details.py    # Faculty feedback workflow
│       └── mentor_feedback.py     # Mentor feedback workflow
│
├── Weights/
│   ├── captcha_weights.npz        # Trained captcha model weights
│   └── labels.json                # Captcha character set
│
├── .gitignore
├── .python-version
├── pyproject.toml
├── pytest.ini
├── README.md
├── requirements.txt
├── run.py                         # Interactive dashboard (entry point)
└── uv.lock
```

## 🛠️ Installation & Setup

Requires **Python 3.12+** (the project uses `match` statements). The steps below use **uv**.

### 1. Clone the Repository

```bash
git clone https://github.com/Lokesh-Ramineni/vtop-pilot.git
cd vtop-pilot
```

### 2. Install uv

Install `uv` using the official installer for your operating system, then verify:

```bash
uv --version
```

### 3. Create and Activate the `.venv`

```bash
uv venv
```

**On Windows:**

```powershell
.venv\Scripts\activate
```

**On macOS / Linux:**

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

If `pyproject.toml` and `uv.lock` already exist (they do in this repository), sync the environment:

```bash
uv sync
```

Or install from `requirements.txt`:

```bash
uv add -r requirements.txt
```

The OTP module also needs `python-dotenv`. If you installed from `requirements.txt` and see an import error for `dotenv`, add it:

```bash
uv add python-dotenv
```

### 5. Install the Playwright Browser

Playwright needs its Chromium build downloaded once:

```bash
playwright install chromium
```

## ⚙️ Configuration

Three things need to be set up before the first run.

### 1. VTOP credentials — `config/credentials.json`

Duplicate `config/example_credentials.json`, rename the copy to `credentials.json`, and fill in your details:

```json
{
  "username": "YOUR_REGISTRATION_NUMBER",
  "password": "YOUR_VTOP_PASSWORD"
}
```

### 2. Email OTP — `config/.env`

VTOP sends a one-time password to your registered email on some logins. The OTP fetcher reads it from Gmail over IMAP using credentials stored in `config/.env`:

```env
EMAIL=your.email@gmail.com
APP_PASSWORD=your_gmail_app_password
```

- `APP_PASSWORD` must be a **Gmail App Password**, not your normal password. Create one under your Google Account → Security → 2-Step Verification → App passwords.
- IMAP must be enabled for the Gmail account.
- The fetcher looks for emails from `noreply.sdc@vitap.ac.in` with the subject `VTOP Login OTP Needed`.

> **Important:** The code reads `config/.env`. The `example_email_app.json` / `email_app.json` files are **not** used by the current code.

### 3. Your registration number check

After logging in, `src/automation/test_login.py` confirms success by checking that the navbar reads `24MIC7146 (STUDENT)`. **Change this string to your own registration number**, otherwise the check will fail for your account. It appears in two places in the file.

### 4. Behaviour settings — `config/config.yaml`

```yaml
urls:
  login_page: "https://vtop.vitap.ac.in/vtop/login"
  content_page: "https://vtop.vitap.ac.in/vtop/content"

feedback:
  auto_submit: false          # false = fill, then you review and submit manually
  default_rating: "Excellent" # Needs Improvement | Satisfactory | Good | Very Good | Excellent
  MESSAGE: "Nothing"          # Text for free-text questions
  THEORY: "NONE"              # Override rating for Theory ("NONE" = use default_rating)
  LAB: "NONE"                 # Override rating for Lab
  LAB_FACILITY: "NONE"        # Override rating for Lab Facility

mentor_feedback:
  rating: "Excellent"
  MESSAGE: "Nothing"          # Letters, numbers, spaces and ? @ # $ % ^ & * ( ) only

outing:
  default_leave_time: "09:00 AM"
  default_return_time: "06:00 PM"
  default_reason: "Local shopping and visiting relatives"
  default_contact: "9000110101"
  default_from_date: "25-JUN-26"   # General outing: leave date
  default_to_date: "30-JUN-26"     # General outing: return date
  default_place: "Enter Place"
  default_purpose: "Family visit"
  # default_date: "25"             # Weekend outing date (see note below)

sem:
  default_semester: "Winter Semester 2025-26"
```

Settings are validated before any form is touched, so a typo such as `"Very good"` fails immediately with a clear message listing the valid values.

> **Weekend Outing:** the weekend flow reads `outing.default_date`. It is commented out in the default config, so uncomment and set it before using option 2 → Weekend Outing.

Keep `credentials.json`, `config/.env` and `session.json` local. They are listed in `.gitignore`; never commit them.

## 🚀 How to Use

Make sure the virtual environment is active, then run:

```bash
python run.py
```

### Dashboard Menu Options

```text
⚙️   1. Check / Refresh Login Session Only
🧳  2. Apply for Outing (Auto-logins if needed)
📝  3. Auto-Fill Faculty Feedback Forms
📝  4. Auto-Fill Mentor Feedback Form
❌  5. Exit
```

- **Option 1 – Check / Refresh Login Session:** Silently validates `config/session.json` in a headless browser. If the session has expired, a visible browser opens and logs in automatically (captcha + OTP), then saves a fresh session.

- **Option 2 – Apply for Outing:** Validates the session (logging in if needed), then asks for the outing type:
  - **1. Weekend Outing**
  - **2. General Outing**

  A visible browser opens, opens the Hostels menu, fills the form using your `config.yaml` values and clicks **SUBMIT**.

- **Option 3 – Auto-Fill Faculty Feedback Forms:** Opens a visible browser with your saved session. Navigate to **Academics → Feedback Form** yourself; the script detects the form and then:
  1. Captures all semesters, feedback types and courses to `data/feedback_dropdowns.json`.
  2. Processes **THEORY**, **LAB** and **LAB_FACILITY** for the currently selected semester, one course at a time.
  3. Skips courses that show "You have already given Feedback".
  4. Validates every question before filling anything.

  With `auto_submit: false` (default) you review each form in the browser, submit it, and type `SUBMITTED` in the terminal to continue. With `auto_submit: true` it waits 10 seconds for review, then submits automatically.

  > This option loads `session.json` directly. If your session has expired, run **Option 1** first.

- **Option 4 – Auto-Fill Mentor Feedback Form:** Validates the session (logging in if needed), then waits for you to open the **Mentee Feedback Form**. It will:
  1. Ask you to choose the semester.
  2. Ask how many mentoring meetings you attended.
  3. If you attended fewer than two, ask for a reason (and a custom reason if you pick "Other"); otherwise fill all rating and text questions from `config.yaml`.
  4. Leave the form for you to review and submit, then wait for you to type `SUBMITTED`.

- **Option 5 – Exit.**

## 🔐 How the Login Flow Works

1. A headless browser loads `session.json` and checks that the VTOP navbar shows your registration number.
2. If that fails, a visible browser opens the login page.
3. The captcha image is read from the page and solved offline by `solver/cap_solver.py`.
4. Credentials and the captcha are submitted.
5. If VTOP shows **"Additional verification required. OTP sent to your registered email."**, the script fetches the OTP from Gmail, fills `#securityOtpCode` and clicks `#verifyOtpBtn`.
6. If the captcha was wrong, the page reloads and the loop retries.
7. On success, the session is saved to `config/session.json`.

## 🧪 Captcha Model & Data Collection

- `Weights/captcha_weights.npz` and `Weights/labels.json` hold the trained model and its character set (`2-9` and `A-Z` without `I`, `O`, `0`, `1`).
- `scraper/test_scrape.py` is a pytest script that downloads captcha images into `data/`. It was used to collect training data and is not needed for normal use.
- `pytest.ini` enables verbose output and live INFO logging for the test modules.

## 🔄 Updating Dependencies

```bash
uv add package-name
```

If you update `requirements.txt`, sync it with:

```bash
uv add -r requirements.txt
```

This updates `pyproject.toml` and `uv.lock`.

## 🩺 Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| `EMAIL not found in .env` / `APP_PASSWORD not found in .env` | Create `config/.env` with `EMAIL` and `APP_PASSWORD`. |
| `Failed to login to Gmail` | Use a Gmail **App Password** and make sure IMAP is enabled. |
| Login keeps failing after success | Update the `24MIC7146 (STUDENT)` check in `test_login.py` to your own registration number. |
| `OTP email did not arrive` | Check the email is arriving at the Gmail account in `.env`, and that it is from `noreply.sdc@vitap.ac.in`. |
| Feedback option errors immediately | Session expired. Run option 1, then retry. |
| `Invalid spelling/value for feedback...` | Fix the rating text in `config.yaml` (exact spelling, e.g. `Very Good`). |

## ⚠️ Disclaimer

This project is intended for educational and personal workflow-automation purposes only. It is provided "as is" and should be used responsibly.

The authors are not responsible for any account restrictions, disciplinary action, data loss, or other consequences resulting from the use or misuse of this project.

Do not use this tool to access, modify, or submit information belonging to another person.
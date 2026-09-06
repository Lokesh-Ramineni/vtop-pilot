# VTOP PILOT (Automation Script) 🚀

An automated Python script designed to handle routine tasks on the VIT VTOP portal, including seamless logins, automated feedback filling, and outing request submissions.

## 🎯 Project Purpose

- **⚡ Eliminating the Hectic Feedback Forms:** Skip the time-consuming process at the end of every semester. The script automates the repetitive radio buttons and mandatory fields for every faculty member, completing the entire evaluation grind in seconds.

- **🏃 Hassle-Free Last-Minute Outings:** Removes frontend JavaScript validations to enable seamless, last-minute application submissions.

### 1. The End-of-Semester Feedback Grind 📝

- **The Problem:** Every semester, you are blocked from viewing your grades or timetable until you fill out massive feedback forms for every single professor. Clicking 20+ repetitive radio buttons ("Excellent"/"Good") across 6+ teachers takes forever.

- **The Solution:** This script automatically navigates through the faculty evaluation pages, fills out the mandatory ratings instantly, and handles the submissions in seconds.

### 2. Last-Minute Outing Applications 🏃💨

- **The Problem:** VTOP strictly locks you out and blocks you from applying if you try to submit an outing request less than 24 hours before your departure time, giving you zero flexibility for sudden weekend plans.

- **The Solution:** **🏃 Hassle-Free Last-Minute Outings:** Removes frontend JavaScript validations to enable seamless, last-minute application submissions. The script bypasses client-side time-lock constraints, allowing you to submit your weekend leave requests instantly whenever you need them.

## 🌟 Features

- **Automated Login:** Handles secure authentication using localized session management.
- **Feedback Automation:** Automatically processes and submits Faculty feedback forms via `feedback_elements.py`.
- **Outing Management:** Automates the hostel outing applications via `outing_elements.py`.
- **Persistent Sessions:** Saves active browser states to `session.json` to bypass logging in every single run.

## 📁 Project Structure

```text
vtop-pilot/
├── config/
│   ├── config.yaml
│   ├── credentials.json
│   ├── email_app.json
│   ├── example_credentials.json
│   ├── example_email_app.json
│   ├── example_session.json
│   └── session.json
│
├── data/
│
├── elements/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── feedback_elements.py
│   ├── login_elements.py
│   └── outing_elements.py
│
├── otp_fetch/
│   ├── __pycache__/
│   └── otp.py
│
├── scraper/
│   ├── __pycache__/
│   └── test_scrape.py
│
├── solver/
│   ├── __pycache__/
│   └── cap_solver.py
│
├── src/
│   ├── __pycache__/
│   ├── automation/
│   │   ├── __pycache__/
│   │   ├── .pytest_cache/
│   │   ├── __init__.py
│   │   ├── test_login.py
│   │   └── test_outing.py
│   ├── vtop_pilot/
│   └── __init__.py
│
├── Weights/
│   ├── captcha_weights.npz
│   └── labels.json
│
├── .gitignore
├── .python-version
├── data.zip
├── pyproject.toml
├── pytest.ini
├── README.md
├── requirements.txt
├── run.py
└── uv.lock
```

> **Note:** `__pycache__/` and `.pytest_cache/` are generated directories and normally should not be committed. They are shown above only to reflect the current project layout.

## 🛠️ Installation & Setup

Follow these steps to set up the project locally using **uv**.

### 1. Clone the Repository

```bash
git clone https://github.com/Lokesh-Ramineni/vtop-pilot.git
cd vtop-pilot
```

### 2. Install uv

If you do not already have `uv` installed, install it using the official installer for your operating system.

Verify the installation:

```bash
uv --version
```

### 3. Initialize the uv Project

If you are setting up the project from scratch, initialize uv in the project directory:

```bash
uv init
```

If you cloned this repository and `pyproject.toml` already exists, you can skip `uv init` and continue with the virtual environment setup.

### 4. Create and Activate the `.venv`

Create the virtual environment using uv:

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

After activation, verify that the virtual environment is active:

```bash
python --version
```

### 5. Add Dependencies

Add all dependencies from `requirements.txt` to the uv-managed project:

```bash
uv add -r requirements.txt
```

This updates `pyproject.toml` and `uv.lock`.

For future dependencies, use:

```bash
uv add package-name
```

## ⚙️ Configuration

Before running the automation scripts, you must configure your local credentials.

1. Navigate to the `config/` directory.

2. Duplicate `example_credentials.json` and rename the copy to `credentials.json`.

3. Open `credentials.json` and fill in your actual VTOP login details:

   ```json
   {
     "username": "YOUR_REGISTRATION_NUMBER",
     "password": "YOUR_VTOP_PASSWORD"
   }
   ```

   > **Note:** `credentials.json` is ignored by Git to keep your account credentials safe.

4. If required by your setup, configure the email application details using `example_email_app.json` and create your local `email_app.json`.

5. Keep `session.json` local. It contains saved browser session information and should not be committed to Git.

## 🚀 How to Use

Always ensure your virtual environment is active before running commands.

### Launch the Automation Dashboard

Open your terminal and run the main entry file:

```bash
python run.py
```

### Dashboard Menu Options

When the interactive terminal dashboard opens, you can choose from the following operations:

- **Option 1 (`Check / Refresh Login Session Only`):** Verifies if your saved session in `session.json` is still valid. If it has expired, it automatically opens a visible browser window so you can quickly log in and solve the captcha.

- **Option 2 (`Apply for Outing`):** Validates your current login session and instantly launches a visible workspace to automate and submit your hostel outing application with ease before the weekend deadline hits.

- **Option 3 (`Auto-Fill Faculty Feedback Forms`):** Connects to the portal and triggers an automated clicking loop to fill out and submit the time-consuming end-of-semester mandatory faculty evaluation forms in seconds.

## 🔄 Updating Dependencies

If you add a new dependency to the project, use:

```bash
uv add package-name
```

If you update `requirements.txt`, sync those dependencies into the uv-managed project with:

```bash
uv add -r requirements.txt
```

This updates `pyproject.toml` and `uv.lock`.

## ⚠️ Disclaimer

This project is intended for educational and personal workflow-automation purposes only. It is provided "as is" and should be used responsibly.

 The authors are not responsible for any account restrictions, disciplinary action, data loss, or other consequences resulting from the use or misuse of this project.

Do not use this tool to access, modify, or submit information belonging to another person.

# VTOP PILOT (Automation Script) 🚀

An automated Python script designed to handle routine tasks on the VIT VTOP portal, including seamless logins, automated feedback filling, and outing request submissions.

## 🎯 Project Purpose

*   **⚡ Eliminating the Hectic Feedback Forms:** Skip the time-consuming process at the end of every semester. The script automates the repetitive radio buttons and mandatory fields for every faculty member, completing the entire evaluation grind in seconds.
*   **🏃 Hassle-Free Last-Minute Outings:** Removes frontend JavaScript validations to enable seamless, last-minute application submissions.


### 1. The End-of-Semester Feedback Grind 📝
* **The Problem:** Every semester, you are blocked from viewing your grades or timetable until you fill out massive feedback forms for every single professor. Clicking 20+ repetitive radio buttons ("Excellent"/"Good") across 6+ teachers takes forever.
* **The Solution:** This script automatically navigates through the faculty evaluation pages, fills out the mandatory ratings instantly, and handles the submissions in seconds.

### 2. Last-Minute Outing Applications 🏃💨
* **The Problem:** VTOP strictly locks you out and blocks you from applying if you try to submit an outing request less than 24 hours before your departure time, giving you zero flexibility for sudden weekend plans.
* **The Solution:** **🏃 Hassle-Free Last-Minute Outings:** Removes frontend JavaScript validations to enable seamless, last-minute application submissions. The script bypasses client-side time-lock constraints, allowing you to submit your weekend leave requests instantly whenever you need them.

## 🌟 Features

*   **Automated Login:** Handles secure authentication using localized session management.
*   **Feedback Automation:** Automatically processes and submits Faculty feedback forms via `feedback_elements.py`.
*   **Outing Management:** Automates the hostel outing applications via `outing_elements.py`.
*   **Persistent Sessions:** Saves active browser states to `session.json` to bypass logging in every single run.

## 📁 Project Structure

```text
vtop-pilot/
├── .venv/                        # Local Python virtual environment
├── config/
│   ├── config.yaml               # Application core settings and parameters
│   ├── credentials.json          # Your secure VTOP login credentials
│   ├── example_credentials.json  # Reference template for formatting credentials
│   └── session.json              # Saved browser cookies/states (Removes read-only blocks)
├── data/                         # Directory for stored logs, receipts, or data exports
├── elements/                     # DOM selectors and elements mapped by page context
│   ├── __init__.py
│   ├── feedback_elements.py      # Page elements for automated feedback processing
│   ├── login_elements.py         # Locators for VTOP auth and captcha fields
│   └── outing_elements.py        # Locators for the hostel outing module
├── src/
│   ├── __init__.py
│   └── automation/               # Automation operational modules
│       ├── __init__.py
│       ├── test_login.py         # Logic for active session persistence validations
│       └── test_outing.py        # Logic for executing outing forms
├── .gitignore                    # Ensures credential profiles are not pushed to Git
├── pytest.ini                    # Test execution configurations
├── README.md                     # Documentation manual
├── requirements.txt              # Core package dependencies
└── run.py                        # Interactive central execution entry point
```

## 🛠️ Installation & Setup

Follow these exact steps to set up the project locally on your machine.

### 1. Clone the Repository
```bash
git clone https://github.com/Lokesh-Ramineni/vtop-pilot.git
cd vtop-pilot
```

### 2. Set Up a Virtual Environment (`.venv`)
Isolate the project dependencies by creating and activating a Python virtual environment:

*   **On Windows:**
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```
*   **On macOS / Linux:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

### 3. Install Dependencies
Install all package configurations listed in `requirements.txt`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Before running the automation scripts, you must configure your local credentials:

1. Navigate to the `config/` directory.
2. Duplicate `example_credentials.json` and rename the copy to `credentials.json`.
3. Open `credentials.json` and fill in your actual VTOP login details:
   ```json
   {
     "username": "YOUR_REGISTRATION_NUMBER",
     "password": "YOUR_VTOP_PASSWORD"
   }
   ```
   *(Note: `credentials.json` is ignored by Git to keep your account safe).*

---

## 🚀 How to Use

Always ensure your virtual environment is active before running commands.

### Launch the Automation Dashboard
Instead of running individual background scripts, open your terminal and run the main entry file to launch the interactive control panel:

```bash
python run.py
```

### Dashboard Menu Options

When the interactive terminal dashboard opens, you can choose from the following operations:

*   **Option 1 (`Check / Refresh Login Session Only`):** Verifies if your saved session in `session.json` is still valid. If it has expired, it automatically opens a visible browser window so you can quickly log in and solve the captcha.
*   **Option 2 (`Apply for Outing`):** Validates your current login session and instantly launches a visible workspace to automate and submit your hostel outing application with ease before the weekend deadline hits.
*   **Option 3 (`Auto-Fill Faculty Feedback Forms`):** Connects to the portal and triggers an automated clicking loop to fill out and submit the time-consuming end-of-semester mandatory faculty evaluation forms in seconds.

---

## ⚠️ Disclaimer

This utility tool is developed strictly for educational and workflow acceleration purposes. Use it responsibly and ensure its behavior complies with your university's digital asset policies.



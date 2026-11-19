"""Central settings. All paths and SMTP values live here so other modules stay clean."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # python-dotenv is optional: real environment variables still work
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent
if load_dotenv:
    load_dotenv(BASE_DIR / ".env")  # reads secrets from .env (never committed to GitHub)

# ---- File locations ----
CONTACTS_CSV = BASE_DIR / "data" / "contacts.csv"
REMINDERS_CSV = BASE_DIR / "data" / "reminders.csv"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUTS_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"
REPORT_CSV = OUTPUTS_DIR / "email_report.csv"
STATE_FILE = OUTPUTS_DIR / "state.json"
LOG_FILE = LOGS_DIR / "app.log"

# ---- SMTP settings (secrets come from environment variables, never hard-coded) ----
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_NAME = os.getenv("SENDER_NAME", "Email Automation Demo")

# Safe default: simulate only. Override with DRY_RUN=false or the --live flag.
DRY_RUN_DEFAULT = os.getenv("DRY_RUN", "true").strip().lower() in ("1", "true", "yes")

DATETIME_FORMAT = "%Y-%m-%d %H:%M"

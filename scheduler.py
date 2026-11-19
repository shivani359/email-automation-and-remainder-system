"""Decide which reminders are due, send them, and handle repeating reminders."""
import json
import logging
import time
from datetime import datetime, timedelta

import pandas as pd

from src import config
from src.mailer import build_message, send_email
from src.templates_loader import load_template, render

log = logging.getLogger(__name__)

REPEAT_DELTAS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


# ---------- loading ----------
def load_reminders(path) -> list:
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    df.columns = [c.strip().lower() for c in df.columns]
    reminders = df.to_dict(orient="records")
    log.info("Loaded %d reminder(s) from %s", len(reminders), path)
    return reminders


def load_state() -> dict:
    """State remembers which reminders are finished / when repeating ones fire next."""
    if config.STATE_FILE.exists():
        return json.loads(config.STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict):
    config.OUTPUTS_DIR.mkdir(exist_ok=True)
    config.STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ---------- sending one reminder ----------
def _result(reminder_id, name, email, subject, status, error=""):
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reminder_id": reminder_id,
        "name": name,
        "email": email,
        "subject": subject,
        "status": status,
        "error": error,
    }


def send_reminder(reminder: dict, contacts: dict, dry_run: bool) -> dict:
    """Personalize and send ONE reminder. Never raises: problems become FAILED rows."""
    rid = reminder.get("reminder_id", "?")
    email = reminder.get("contact_email", "").strip().lower()

    contact = contacts.get(email)
    if contact is None:
        log.error("%s: contact %s not found in contacts.csv", rid, email)
        return _result(rid, "", email, "", "FAILED", "Contact not found in contacts.csv")

    try:
        template = load_template(reminder.get("template", ""))
        # contact fields first, then reminder fields (empty cells are ignored)
        context = {**contact, **{k: v for k, v in reminder.items() if v != ""}}
        subject, body = render(template, context)
    except (FileNotFoundError, ValueError, KeyError) as exc:
        log.error("%s: template problem: %s", rid, exc)
        return _result(rid, contact["name"], email, "", "FAILED", str(exc))

    msg = build_message(contact["name"], email, subject, body)
    status, error = send_email(msg, email, dry_run=dry_run)
    if status == "FAILED":
        log.error("%s: send failed: %s", rid, error)
    return _result(rid, contact["name"], email, subject, status, error)


# ---------- deciding what is due ----------
def process_due_reminders(reminders, contacts, now, dry_run, state) -> list:
    results = []
    for reminder in reminders:
        rid = reminder.get("reminder_id", "?")
        entry = state.get(rid, {})
        if entry.get("done"):
            continue

        try:
            first_time = datetime.strptime(reminder["send_at"], config.DATETIME_FORMAT)
        except (KeyError, ValueError):
            log.error("%s: invalid send_at (expected YYYY-MM-DD HH:MM)", rid)
            results.append(_result(rid, "", reminder.get("contact_email", ""), "",
                                   "FAILED", "Invalid send_at format"))
            state[rid] = {"done": True}
            continue

        next_due = datetime.fromisoformat(entry["next_due"]) if "next_due" in entry else first_time
        if next_due > now:
            continue  # not due yet

        results.append(send_reminder(reminder, contacts, dry_run))

        repeat = reminder.get("repeat", "none").strip().lower()
        if repeat in REPEAT_DELTAS:
            step = REPEAT_DELTAS[repeat]
            while next_due <= now:  # skip missed slots, so we never spam catch-up emails
                next_due += step
            state[rid] = {"next_due": next_due.isoformat(), "done": False}
        else:
            state[rid] = {"done": True}
    return results


# ---------- continuous mode ----------
def run_forever(job, interval_seconds: int):
    """Run `job` every N seconds using the `schedule` library."""
    try:
        import schedule
    except ImportError:
        raise SystemExit("The 'schedule' package is missing. Run: pip install -r requirements.txt")

    schedule.every(interval_seconds).seconds.do(job)
    log.info("Scheduler started: checking every %d second(s). Press Ctrl+C to stop.", interval_seconds)
    job()  # run once immediately
    while True:
        schedule.run_pending()
        time.sleep(1)

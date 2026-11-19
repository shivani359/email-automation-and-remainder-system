# Email Automation & Reminder System

A beginner-friendly Python project that reads contacts and reminders from CSV files,
personalizes email templates, sends them via SMTP (or simulates with **dry-run**),
tracks every result, and writes a CSV report.

## Features
- Contacts and reminders from CSV (Pandas)
- Template-based personalization (`{name}`, `{event_name}`, ...)
- One-off and repeating (daily / weekly) reminders
- Dry-run mode: test everything without sending a single email
- Logging to console and `logs/app.log`
- CSV report with SENT / FAILED / DRY_RUN status and error reasons
- Passwords kept in `.env` (never committed)

## Setup
```bash
python -m venv venv
# Windows: venv\Scripts\activate      Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # Windows: copy .env.example .env
```

## Run
```bash
python main.py --dry-run --as-of "2026-11-21 10:00"   # safe simulation
python main.py --live                                  # real emails (needs .env)
python main.py --daemon --interval 60                  # keep running
```

## Gmail setup (for --live)
Turn on 2-Step Verification, create an **App Password**, and put it in `.env` as `SMTP_PASSWORD`.
Test with your own address first.

## Project structure
| Folder | Purpose |
|---|---|
| `data/` | contacts.csv, reminders.csv (sample data) |
| `templates/` | email templates (first line `Subject: ...`) |
| `src/` | modules: config, contacts, templates, mailer, scheduler, reports |
| `outputs/` | CSV report, scheduler state |
| `logs/` | app.log |
| `images/` | screenshots for this README |
| `docs/` | architecture notes |

## Known limitations
- A reminder that fails in live mode is not retried automatically.
- Repeats support daily and weekly only.
- Sample data uses fake `example.com` addresses.

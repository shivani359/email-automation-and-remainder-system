"""Email Automation & Reminder System - command line entry point.

Examples
--------
python main.py --dry-run                       # simulate everything, send nothing
python main.py --dry-run --as-of "2026-11-21 10:00"   # pretend it is this date/time
python main.py --live                          # really send (needs .env credentials)
python main.py --daemon --interval 60          # keep running, check every 60 s
"""
import argparse
import logging
from datetime import datetime

from src import config
from src.contacts import load_contacts
from src.logger_setup import setup_logging
from src.reports import append_results, print_summary
from src.scheduler import (load_reminders, load_state, process_due_reminders,
                           run_forever, save_state)

log = logging.getLogger("main")


def parse_args():
    p = argparse.ArgumentParser(description="Email Automation & Reminder System")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="simulate only, send nothing")
    mode.add_argument("--live", action="store_true", help="really send emails via SMTP")
    p.add_argument("--daemon", action="store_true", help="keep running and check repeatedly")
    p.add_argument("--interval", type=int, default=60, help="seconds between checks (daemon)")
    p.add_argument("--as-of", help='pretend "now" is this time, e.g. "2026-11-21 10:00"')
    return p.parse_args()


def run_cycle(dry_run: bool, as_of, state: dict):
    """One full pass: load files -> find due reminders -> send -> report."""
    contacts = load_contacts(config.CONTACTS_CSV)       # re-read each cycle so edits are picked up
    reminders = load_reminders(config.REMINDERS_CSV)
    now = as_of or datetime.now()

    results = process_due_reminders(reminders, contacts, now, dry_run, state)
    append_results(results)
    print_summary(results)
    if not dry_run:
        save_state(state)  # dry runs never mark reminders as finished


def main():
    args = parse_args()
    setup_logging()

    dry_run = True if args.dry_run else (False if args.live else config.DRY_RUN_DEFAULT)
    as_of = datetime.strptime(args.as_of, config.DATETIME_FORMAT) if args.as_of else None
    log.info("Mode: %s", "DRY RUN (nothing is sent)" if dry_run else "LIVE (real emails)")

    state = {} if dry_run else load_state()

    if args.daemon:
        try:
            run_forever(lambda: run_cycle(dry_run, as_of, state), args.interval)
        except KeyboardInterrupt:
            log.info("Stopped by user")
    else:
        run_cycle(dry_run, as_of, state)


if __name__ == "__main__":
    main()

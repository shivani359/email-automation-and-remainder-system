"""Write results to a CSV report and print a summary."""
import logging
from collections import Counter

import pandas as pd

from src import config

log = logging.getLogger(__name__)

COLUMNS = ["timestamp", "reminder_id", "name", "email", "subject", "status", "error"]


def append_results(results: list):
    """Append this run's results to outputs/email_report.csv (header added once)."""
    if not results:
        return
    config.OUTPUTS_DIR.mkdir(exist_ok=True)
    df = pd.DataFrame(results, columns=COLUMNS)
    write_header = not config.REPORT_CSV.exists()
    df.to_csv(config.REPORT_CSV, mode="a", header=write_header, index=False, encoding="utf-8")
    log.info("Report updated: %s", config.REPORT_CSV)


def print_summary(results: list):
    counts = Counter(r["status"] for r in results)
    print("\n" + "=" * 44)
    print(" RUN SUMMARY")
    print("=" * 44)
    print(f" Processed : {len(results)}")
    print(f" Sent      : {counts.get('SENT', 0)}")
    print(f" Dry-run   : {counts.get('DRY_RUN', 0)}")
    print(f" Failed    : {counts.get('FAILED', 0)}")
    for r in results:
        if r["status"] == "FAILED":
            print(f"   - {r['reminder_id']} ({r['email']}): {r['error']}")
    print("=" * 44 + "\n")

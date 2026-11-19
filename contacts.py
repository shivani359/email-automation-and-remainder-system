"""Read the contact list from CSV and validate email addresses."""
import logging
import re

import pandas as pd

log = logging.getLogger(__name__)

EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email.strip()))


def load_contacts(path) -> dict:
    """Return {email: contact_dict}. Duplicate emails are dropped."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    df.columns = [c.strip().lower() for c in df.columns]

    missing = {"name", "email"} - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing required column(s): {sorted(missing)}")

    df["email"] = df["email"].str.strip().str.lower()
    before = len(df)
    df = df.drop_duplicates(subset="email")
    if len(df) < before:
        log.warning("Removed %d duplicate contact(s)", before - len(df))

    contacts = {row["email"]: row.to_dict() for _, row in df.iterrows()}
    log.info("Loaded %d contact(s) from %s", len(contacts), path)
    return contacts

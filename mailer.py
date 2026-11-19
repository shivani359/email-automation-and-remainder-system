"""Build and send emails through SMTP. Supports a safe dry-run mode."""
import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from src import config
from src.contacts import is_valid_email

log = logging.getLogger(__name__)


def build_message(to_name: str, to_email: str, subject: str, body: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = formataddr((config.SENDER_NAME, config.SMTP_USER or "noreply@example.com"))
    msg["To"] = formataddr((to_name, to_email))
    msg["Subject"] = subject
    msg.set_content(body)
    return msg


def send_email(msg: EmailMessage, to_email: str, dry_run: bool = True):
    """Send one email. Returns (status, error_message).

    status is one of: SENT, FAILED, DRY_RUN
    """
    if not is_valid_email(to_email):
        return "FAILED", "Invalid email address"

    if dry_run:
        log.info("[DRY RUN] Would send to %s | subject: %s", to_email, msg["Subject"])
        return "DRY_RUN", ""

    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        return "FAILED", "SMTP_USER / SMTP_PASSWORD not set in .env"

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)
        log.info("Sent to %s", to_email)
        return "SENT", ""
    except smtplib.SMTPAuthenticationError:
        return "FAILED", "SMTP login failed (check username / App Password)"
    except smtplib.SMTPRecipientsRefused:
        return "FAILED", "Recipient address refused by server"
    except (smtplib.SMTPException, OSError) as exc:  # network down, timeout, etc.
        return "FAILED", f"{type(exc).__name__}: {exc}"

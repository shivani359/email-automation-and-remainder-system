"""Load email templates and fill in {placeholders} for each person."""
import logging
from dataclasses import dataclass

from src import config

log = logging.getLogger(__name__)


@dataclass
class EmailTemplate:
    subject: str
    body: str


class SafeDict(dict):
    """Leaves unknown {placeholders} visible instead of crashing."""

    def __missing__(self, key):
        log.warning("Template placeholder {%s} has no value", key)
        return "{" + key + "}"


def load_template(name: str) -> EmailTemplate:
    """Template file format: first line 'Subject: ...', then a blank line, then the body."""
    path = config.TEMPLATES_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path.name}")

    text = path.read_text(encoding="utf-8")
    first_line, _, rest = text.partition("\n")
    if not first_line.lower().startswith("subject:"):
        raise ValueError(f"{path.name} must start with a 'Subject:' line")
    return EmailTemplate(subject=first_line[len("subject:"):].strip(), body=rest.strip())


def render(template: EmailTemplate, context: dict):
    """Personalize subject and body. Returns (subject, body)."""
    data = SafeDict(context)
    return template.subject.format_map(data), template.body.format_map(data)

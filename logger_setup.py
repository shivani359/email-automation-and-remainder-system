"""Logging: every important event goes to the console AND to logs/app.log."""
import logging

from src import config


def setup_logging(level=logging.INFO):
    config.LOGS_DIR.mkdir(exist_ok=True)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")

    root = logging.getLogger()
    root.setLevel(level)
    if root.handlers:  # avoid duplicate handlers if called twice
        return

    file_handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(fmt)
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(file_handler)
    root.addHandler(console)

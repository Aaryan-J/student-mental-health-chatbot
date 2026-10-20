"""Configuration loading: environment variables (.env) and helplines.

Everything is read with UTF-8 and resolved relative to the project root so the
program behaves the same on Windows and Linux.
"""

import json
import os
from typing import Any, Dict

from dotenv import load_dotenv

from . import paths

# Default bot name; can be overridden by BOT_NAME in .env or the environment.
DEFAULT_BOT_NAME = "School Support Bot"


def load_env() -> None:
    """Load variables from the project .env file (if it exists).

    Uses an explicit path so it works regardless of the current directory.
    Missing values are simply ignored.
    """
    if paths.ENV_FILE.exists():
        load_dotenv(dotenv_path=paths.ENV_FILE, encoding="utf-8")


def get_bot_name() -> str:
    """Return the bot name from the environment, or a sensible default."""
    return os.environ.get("BOT_NAME", DEFAULT_BOT_NAME).strip() or DEFAULT_BOT_NAME


def _valid_helplines(value: Any) -> bool:
    """Return True if value looks like a usable list of helpline entries.

    We accept an empty list (no helplines configured) and any list where every
    item is a dictionary. Anything else (None, a string, a list of strings) is
    rejected so callers can fall back safely instead of crashing.
    """
    if not isinstance(value, list):
        return False
    return all(isinstance(entry, dict) for entry in value)


def load_helplines() -> Dict[str, Any]:
    """Load helpline details from config/helplines.json.

    Returns a dictionary with the crisis message and a list of helplines.
    If the file is missing or invalid we return a safe fallback so the program
    never crashes and the user still gets some guidance.
    """
    fallback: Dict[str, Any] = {
        "crisis_message": (
            "It sounds like you are going through something very serious, and "
            "you deserve real support right now. Please reach out to a trusted "
            "adult or one of the helplines below. You are not alone."
        ),
        "helplines": [
            {
                "region": "Your Country",
                "name": "Replace this with your local crisis line",
                "number": "REPLACE-WITH-LOCAL-NUMBER",
                "note": "REPLACE WITH YOUR COUNTRY'S HELPLINE",
            }
        ],
    }

    try:
        raw = paths.HELPLINES_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, ValueError):
        # File missing/unreadable or bad JSON -> use the fallback.
        return fallback

    # The file must be a JSON object with a usable "helplines" list.
    if not isinstance(data, dict) or not _valid_helplines(data.get("helplines")):
        return fallback

    # Fill in the crisis message if it is missing or not a string.
    if not isinstance(data.get("crisis_message"), str) or not data["crisis_message"]:
        data["crisis_message"] = fallback["crisis_message"]

    return data

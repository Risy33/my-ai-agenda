"""Task rules and validation, shared by every interface (terminal now, AI assistant later).

These functions never call input() or print(), so any part of the program can use them,
and they are easy to test.
"""

from datetime import date

PRIORITIES = ("low", "medium", "high")
STATUSES = ("all", "open", "completed")


def parse_title(text):
    """Turn text into a task title. Raise ValueError if it is blank."""
    text = text.strip()
    if not text:
        raise ValueError("A task cannot be empty.")
    return text


def parse_due_date(text):
    """Turn text into 'YYYY-MM-DD'. Blank means no date (None). Raise ValueError if invalid."""
    text = text.strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        raise ValueError(
            "That is not a valid date. Use the format YYYY-MM-DD, for example 2026-12-31."
        ) from None


def parse_priority(text):
    """Turn text into 'low', 'medium', or 'high'. Blank means 'medium'. Raise ValueError if invalid."""
    text = text.strip().lower()
    if not text:
        return "medium"
    if text in PRIORITIES:
        return text
    raise ValueError("Priority must be 'low', 'medium', or 'high'.")


def parse_category(text):
    """Turn text into a category. Blank or whitespace-only means no category (None)."""
    text = text.strip()
    if not text:
        return None
    return text


def is_overdue(task, today):
    """A task is overdue when it is unfinished and its due date is before today."""
    return (
        not task["completed"]
        and task["due_date"] is not None
        and task["due_date"] < today.isoformat()
    )

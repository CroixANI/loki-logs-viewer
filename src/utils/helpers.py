from datetime import datetime, timezone


def format_timestamp(ns_str: str) -> datetime:
    """Convert a 19-digit nanosecond Unix epoch string to a UTC datetime object."""
    ns = int(ns_str)
    seconds = ns / 1_000_000_000
    return datetime.fromtimestamp(seconds, tz=timezone.utc)


def truncate(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length characters, appending '…' if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "…"

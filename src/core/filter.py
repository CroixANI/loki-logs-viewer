# NOTE: No streamlit imports allowed in this module.
import re

# Severity order from most critical to least — used for "show this level and above" filtering.
LEVEL_ORDER = ["error", "warn", "info", "debug", "trace"]


def apply_filters(
    entries: list,
    search: str = "",
    level: str = "all",
    use_regex: bool = False,
) -> list:
    """Filter log entries by level and/or search term.

    Args:
        entries:   List of log entry dicts (as produced by parser.parse_loki_json).
        search:    Keyword or regex string. Empty string means no search filter.
        level:     Level to filter to. "all" disables level filtering.
                   Otherwise shows entries at this level and all more severe ones
                   (e.g. "warn" → error + warn).
        use_regex: When True, treat search as a compiled regex pattern.

    Returns:
        Filtered list of entry dicts. Order is preserved.

    Raises:
        re.error: If use_regex is True and search is not a valid regex pattern.
    """
    filtered = _apply_level_filter(entries, level)
    filtered = _apply_search_filter(filtered, search, use_regex)
    return filtered


def _apply_level_filter(entries: list, level: str) -> list:
    if not level or level == "all":
        return entries
    if level in LEVEL_ORDER:
        allowed = set(LEVEL_ORDER[: LEVEL_ORDER.index(level) + 1])
    else:
        allowed = {level}
    # Entries with no detected level ("") are always shown.
    return [e for e in entries if e["level"] in allowed or e["level"] == ""]


def _apply_search_filter(entries: list, search: str, use_regex: bool) -> list:
    if not search:
        return entries
    if use_regex:
        pattern = re.compile(search, re.IGNORECASE)  # raises re.error on invalid pattern
        return [e for e in entries if pattern.search(e["message"])]
    lower = search.lower()
    return [e for e in entries if lower in e["message"].lower()]

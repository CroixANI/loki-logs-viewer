import re

import pytest

from src.core.filter import apply_filters, LEVEL_ORDER

# ── Shared fixtures ───────────────────────────────────────────────────────────

def _entry(message: str, level: str) -> dict:
    """Minimal log entry dict sufficient for filter tests."""
    return {"message": message, "level": level, "ts": None, "ts_ns": "0", "labels": {}}


SAMPLE = [
    _entry("connection error occurred",  "error"),
    _entry("disk space warning",         "warn"),
    _entry("server started successfully","info"),
    _entry("loading config file",        "debug"),
    _entry("entering trace span",        "trace"),
    _entry("plain line no level",        ""),
]


# ── Level filtering ───────────────────────────────────────────────────────────

class TestLevelFilter:
    def test_all_returns_everything(self):
        assert apply_filters(SAMPLE, level="all") == SAMPLE

    def test_empty_level_returns_everything(self):
        assert apply_filters(SAMPLE, level="") == SAMPLE

    def test_error_only_shows_error_and_no_level(self):
        result = apply_filters(SAMPLE, level="error")
        levels = {e["level"] for e in result}
        assert levels == {"error", ""}

    def test_warn_shows_error_warn_and_no_level(self):
        result = apply_filters(SAMPLE, level="warn")
        levels = {e["level"] for e in result}
        assert levels == {"error", "warn", ""}

    def test_info_shows_error_warn_info_and_no_level(self):
        result = apply_filters(SAMPLE, level="info")
        levels = {e["level"] for e in result}
        assert levels == {"error", "warn", "info", ""}

    def test_debug_excludes_trace(self):
        result = apply_filters(SAMPLE, level="debug")
        levels = {e["level"] for e in result}
        assert "trace" not in levels

    def test_trace_shows_all_levels(self):
        result = apply_filters(SAMPLE, level="trace")
        levels = {e["level"] for e in result}
        assert levels == {"error", "warn", "info", "debug", "trace", ""}

    def test_entries_with_no_level_always_pass(self):
        result = apply_filters(SAMPLE, level="error")
        assert any(e["level"] == "" for e in result)

    def test_empty_entries_returns_empty(self):
        assert apply_filters([], level="error") == []


# ── Keyword search ────────────────────────────────────────────────────────────

class TestKeywordSearch:
    def test_no_search_returns_all(self):
        assert apply_filters(SAMPLE, search="") == SAMPLE

    def test_exact_keyword_match(self):
        result = apply_filters(SAMPLE, search="error")
        assert len(result) == 1
        assert result[0]["message"] == "connection error occurred"

    def test_case_insensitive(self):
        result = apply_filters(SAMPLE, search="ERROR")
        assert len(result) == 1

    def test_partial_keyword_match(self):
        result = apply_filters(SAMPLE, search="config")
        assert len(result) == 1
        assert "config" in result[0]["message"]

    def test_no_match_returns_empty(self):
        result = apply_filters(SAMPLE, search="xyznotfound")
        assert result == []


# ── Regex search ──────────────────────────────────────────────────────────────

class TestRegexSearch:
    def test_regex_match(self):
        result = apply_filters(SAMPLE, search=r"(error|warning)", use_regex=True)
        assert len(result) == 2

    def test_regex_case_insensitive(self):
        result = apply_filters(SAMPLE, search=r"ERROR", use_regex=True)
        assert len(result) == 1

    def test_invalid_regex_raises(self):
        with pytest.raises(re.error):
            apply_filters(SAMPLE, search=r"[invalid", use_regex=True)

    def test_regex_anchors(self):
        result = apply_filters(SAMPLE, search=r"^connection", use_regex=True)
        assert len(result) == 1
        assert result[0]["message"].startswith("connection")


# ── Combined level + search ───────────────────────────────────────────────────

class TestCombinedFilters:
    def test_level_and_search_both_applied(self):
        result = apply_filters(SAMPLE, search="error", level="error")
        assert len(result) == 1
        assert result[0]["level"] == "error"

    def test_level_narrows_then_search_narrows_further(self):
        # level=warn → error + warn + no-level; search="disk" → only the warn entry
        result = apply_filters(SAMPLE, search="disk", level="warn")
        assert len(result) == 1
        assert result[0]["level"] == "warn"

    def test_no_match_on_combined(self):
        result = apply_filters(SAMPLE, search="xyznotfound", level="error")
        assert result == []


# ── LEVEL_ORDER constant ──────────────────────────────────────────────────────

class TestLevelOrder:
    def test_error_is_first(self):
        assert LEVEL_ORDER[0] == "error"

    def test_trace_is_last(self):
        assert LEVEL_ORDER[-1] == "trace"

    def test_severity_descending(self):
        # Each successive level is less severe — confirmed by position
        assert LEVEL_ORDER.index("error") < LEVEL_ORDER.index("warn")
        assert LEVEL_ORDER.index("warn")  < LEVEL_ORDER.index("info")
        assert LEVEL_ORDER.index("info")  < LEVEL_ORDER.index("debug")
        assert LEVEL_ORDER.index("debug") < LEVEL_ORDER.index("trace")

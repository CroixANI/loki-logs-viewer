from datetime import datetime, timezone

import pytest

from src.utils.helpers import format_timestamp, truncate


class TestFormatTimestamp:
    def test_returns_utc_datetime(self):
        dt = format_timestamp("1705312800000000000")
        assert isinstance(dt, datetime)
        assert dt.tzinfo == timezone.utc

    def test_known_value(self):
        # 2024-01-15 10:00:00 UTC  →  1705312800 seconds
        dt = format_timestamp("1705312800000000000")
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 10
        assert dt.minute == 0
        assert dt.second == 0

    def test_sub_millisecond_difference_same_second(self):
        # Two timestamps in the same second (differ only in sub-millisecond digits)
        dt1 = format_timestamp("1705312800000000000")
        dt2 = format_timestamp("1705312800000100000")  # +100 µs
        assert dt1.replace(microsecond=0) == dt2.replace(microsecond=0)

    def test_epoch_zero(self):
        dt = format_timestamp("0")
        assert dt == datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


class TestTruncate:
    def test_short_string_unchanged(self):
        assert truncate("hello") == "hello"

    def test_exactly_max_length_unchanged(self):
        text = "x" * 100
        assert truncate(text) == text

    def test_over_limit_gets_ellipsis(self):
        text = "x" * 101
        result = truncate(text)
        assert result.endswith("…")
        assert len(result) == 101  # 100 chars + ellipsis

    def test_custom_max_length(self):
        result = truncate("abcdef", max_length=3)
        assert result == "abc…"

    def test_empty_string(self):
        assert truncate("") == ""

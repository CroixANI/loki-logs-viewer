import json
from datetime import timezone
from pathlib import Path

import pytest

from src.core.parser import parse_loki_json, INSPECTABLE_LABELS

FIXTURE = Path(__file__).parent / "fixtures" / "stub_loki.json"


@pytest.fixture(scope="module")
def stub_raw() -> dict:
    return json.loads(FIXTURE.read_text())


@pytest.fixture(scope="module")
def stub_entries(stub_raw) -> list:
    return parse_loki_json(stub_raw)


class TestOutputShape:
    def test_returns_list(self, stub_entries):
        assert isinstance(stub_entries, list)

    def test_entries_are_dicts(self, stub_entries):
        assert all(isinstance(e, dict) for e in stub_entries)

    def test_expected_keys(self, stub_entries):
        assert set(stub_entries[0].keys()) == {"ts", "ts_ns", "message", "level", "labels"}

    def test_row_count(self, stub_entries):
        # 3 streams: 1 value + 2 values + 1 value = 4 rows total
        assert len(stub_entries) == 4

    def test_labels_are_dicts(self, stub_entries):
        assert all(isinstance(e["labels"], dict) for e in stub_entries)


class TestSorting:
    def test_sorted_descending_by_timestamp(self, stub_entries):
        ts_list = [e["ts"] for e in stub_entries]
        assert ts_list == sorted(ts_list, reverse=True)

    def test_first_entry_is_most_recent(self, stub_entries):
        assert stub_entries[0]["ts_ns"] == "1705312811000000000"


class TestTimestampConversion:
    def test_ts_is_utc_datetime(self, stub_entries):
        for e in stub_entries:
            assert e["ts"].tzinfo == timezone.utc

    def test_ts_ns_preserved_as_string(self, stub_entries):
        assert all(isinstance(e["ts_ns"], str) for e in stub_entries)


class TestLevelNormalisation:
    def _entry(self, stub_entries, ts_ns):
        return next(e for e in stub_entries if e["ts_ns"] == ts_ns)

    def test_information_normalised_to_info(self, stub_entries):
        assert self._entry(stub_entries, "1705312800000000000")["level"] == "info"

    def test_error_normalised(self, stub_entries):
        assert self._entry(stub_entries, "1705312810000000000")["level"] == "error"

    def test_debug_normalised(self, stub_entries):
        assert self._entry(stub_entries, "1705312790000000000")["level"] == "debug"

    def test_severity_text_key_used(self, stub_raw):
        stream = stub_raw["data"]["result"][0]["stream"]
        assert "severity_text" in stream
        assert "level" not in stream


class TestLabelsPreserved:
    def test_all_stream_labels_present(self, stub_entries):
        entry = next(e for e in stub_entries if e["ts_ns"] == "1705312800000000000")
        assert entry["labels"]["service_name"] == "acme-service"
        assert entry["labels"]["severity_text"] == "Information"
        assert "MessageBody" in entry["labels"]

    def test_message_body_label_accessible(self, stub_entries):
        entry = next(e for e in stub_entries if e["ts_ns"] == "1705312800000000000")
        body = json.loads(entry["labels"]["MessageBody"])
        assert "SessionId" in body


class TestEdgeCases:
    def test_empty_dict_returns_empty_list(self):
        result = parse_loki_json({})
        assert result == []

    def test_empty_result_list(self):
        result = parse_loki_json({"data": {"result": []}})
        assert result == []

    def test_stream_with_no_values(self):
        raw = {"data": {"result": [{"stream": {"severity_text": "Info"}, "values": []}]}}
        assert parse_loki_json(raw) == []

    def test_missing_severity_yields_empty_level(self):
        raw = {
            "data": {
                "result": [
                    {
                        "stream": {"service_name": "x"},
                        "values": [["1705312800000000000", "plain log"]],
                    }
                ]
            }
        }
        assert parse_loki_json(raw)[0]["level"] == ""


class TestInspectableLabels:
    def test_messagebody_is_inspectable(self):
        assert "MessageBody" in INSPECTABLE_LABELS

    def test_message_body_dot_notation_is_inspectable(self):
        assert "message.body" in INSPECTABLE_LABELS

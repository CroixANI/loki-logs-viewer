import json
from datetime import timezone
from pathlib import Path

import pandas as pd
import pytest

from src.core.parser import parse_loki_json, INSPECTABLE_LABELS

FIXTURE = Path(__file__).parent / "fixtures" / "stub_loki.json"


@pytest.fixture(scope="module")
def stub_raw() -> dict:
    return json.loads(FIXTURE.read_text())


@pytest.fixture(scope="module")
def stub_df(stub_raw) -> pd.DataFrame:
    return parse_loki_json(stub_raw)


class TestOutputShape:
    def test_returns_dataframe(self, stub_df):
        assert isinstance(stub_df, pd.DataFrame)

    def test_expected_columns(self, stub_df):
        assert set(stub_df.columns) == {"ts", "ts_ns", "message", "level", "labels"}

    def test_row_count(self, stub_df):
        # 3 streams: 1 value + 2 values + 1 value = 4 rows total
        assert len(stub_df) == 4

    def test_labels_column_contains_dicts(self, stub_df):
        assert all(isinstance(v, dict) for v in stub_df["labels"])


class TestSorting:
    def test_sorted_descending_by_timestamp(self, stub_df):
        ts_list = list(stub_df["ts"])
        assert ts_list == sorted(ts_list, reverse=True)

    def test_first_row_is_most_recent(self, stub_df):
        # The error stream has values at ...810 and ...811 — ...811 is newest overall
        assert stub_df.iloc[0]["ts_ns"] == "1705312811000000000"


class TestTimestampConversion:
    def test_ts_is_utc_datetime(self, stub_df):
        for ts in stub_df["ts"]:
            assert ts.tzinfo == timezone.utc

    def test_ts_ns_preserved_as_string(self, stub_df):
        assert all(isinstance(v, str) for v in stub_df["ts_ns"])


class TestLevelNormalisation:
    def test_information_normalised_to_info(self, stub_df):
        info_rows = stub_df[stub_df["ts_ns"] == "1705312800000000000"]
        assert info_rows.iloc[0]["level"] == "info"

    def test_error_normalised(self, stub_df):
        error_rows = stub_df[stub_df["ts_ns"] == "1705312810000000000"]
        assert error_rows.iloc[0]["level"] == "error"

    def test_debug_normalised(self, stub_df):
        debug_rows = stub_df[stub_df["ts_ns"] == "1705312790000000000"]
        assert debug_rows.iloc[0]["level"] == "debug"

    def test_severity_text_key_used(self, stub_raw):
        # Confirm fixture uses severity_text (OTel convention), not 'level'
        stream = stub_raw["data"]["result"][0]["stream"]
        assert "severity_text" in stream
        assert "level" not in stream


class TestLabelsPreserved:
    def test_all_stream_labels_present(self, stub_df):
        row = stub_df[stub_df["ts_ns"] == "1705312800000000000"].iloc[0]
        labels = row["labels"]
        assert labels["service_name"] == "acme-service"
        assert labels["severity_text"] == "Information"
        assert "MessageBody" in labels

    def test_message_body_label_accessible(self, stub_df):
        row = stub_df[stub_df["ts_ns"] == "1705312800000000000"].iloc[0]
        body = json.loads(row["labels"]["MessageBody"])
        assert "SessionId" in body


class TestEdgeCases:
    def test_empty_dict_returns_empty_df(self):
        df = parse_loki_json({})
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert set(df.columns) == {"ts", "ts_ns", "message", "level", "labels"}

    def test_empty_result_list(self):
        df = parse_loki_json({"data": {"result": []}})
        assert len(df) == 0

    def test_stream_with_no_values(self):
        raw = {"data": {"result": [{"stream": {"severity_text": "Info"}, "values": []}]}}
        df = parse_loki_json(raw)
        assert len(df) == 0

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
        df = parse_loki_json(raw)
        assert df.iloc[0]["level"] == ""


class TestInspectableLabels:
    def test_messagebody_is_inspectable(self):
        assert "MessageBody" in INSPECTABLE_LABELS

    def test_message_body_dot_notation_is_inspectable(self):
        assert "message.body" in INSPECTABLE_LABELS

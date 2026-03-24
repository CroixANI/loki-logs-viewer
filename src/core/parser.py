# NOTE: No streamlit imports allowed in this module.
import json

import pandas as pd

from src.utils.helpers import format_timestamp

# Label keys that may contain a JSON-encoded payload worth inspecting.
INSPECTABLE_LABELS = {"MessageBody", "message.body"}


def parse_loki_json(raw: dict) -> pd.DataFrame:
    """Parse a Loki /query_range JSON response into a flat DataFrame.

    Each row represents one log line. Stream labels are stored as a dict
    in the 'labels' column so the original structure is preserved and
    accessible to UI components without extra joins.

    Args:
        raw: Parsed JSON dict from a Loki export file.

    Returns:
        DataFrame sorted by timestamp descending with columns:
            ts          - UTC datetime
            ts_ns       - original nanosecond string (for stable row keys)
            message     - raw log line string
            level       - log level string or empty string if not found
            labels      - dict of all stream labels for this entry
    """
    results = raw.get("data", {}).get("result", [])
    if not results:
        return _empty_df()

    rows = []
    for stream_obj in results:
        labels: dict = stream_obj.get("stream", {})
        values: list = stream_obj.get("values", [])
        level = _extract_level(labels)
        for ts_ns, line in values:
            rows.append(
                {
                    "ts": format_timestamp(ts_ns),
                    "ts_ns": ts_ns,
                    "message": line,
                    "level": level,
                    "labels": labels,
                }
            )

    if not rows:
        return _empty_df()

    df = pd.DataFrame(rows)
    df.sort_values("ts", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def _empty_df() -> pd.DataFrame:
    return pd.DataFrame(columns=["ts", "ts_ns", "message", "level", "labels"])


# Known label keys that carry a log-level value, checked in priority order.
# severity_text / detected_level are standard OpenTelemetry/Loki export keys.
_LEVEL_KEYS = ("level", "severity_text", "detected_level", "severity", "lvl", "log_level")
_LEVEL_NORMALISE = {
    "error": "error", "err": "error", "critical": "error", "fatal": "error",
    "warn": "warn", "warning": "warn",
    "info": "info", "information": "info",
    "debug": "debug", "dbg": "debug",
    "trace": "trace",
}


def _extract_level(labels: dict) -> str:
    for key in _LEVEL_KEYS:
        raw = labels.get(key, "")
        if raw:
            return _LEVEL_NORMALISE.get(raw.lower(), raw.lower())
    return ""

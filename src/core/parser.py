# NOTE: No streamlit imports allowed in this module.
from src.utils.helpers import format_timestamp

# Label keys that may contain a JSON-encoded payload worth inspecting.
INSPECTABLE_LABELS = {"MessageBody", "message.body"}

# Type alias for a parsed log entry.
# Keys: ts (datetime), ts_ns (str), message (str), level (str), labels (dict)
LogEntry = dict


def parse_loki_json(raw: dict) -> list[LogEntry]:
    """Parse a Loki /query_range JSON response into a flat list of log entries.

    Each entry is a dict with keys:
        ts        - UTC datetime
        ts_ns     - original nanosecond string (for stable widget keys)
        message   - raw log line string
        level     - normalised log level string, or '' if not found
        labels    - dict of all stream labels for this entry

    Args:
        raw: Parsed JSON dict from a Loki export file.

    Returns:
        List of log entry dicts sorted by timestamp descending.
    """
    results = raw.get("data", {}).get("result", [])
    if not results:
        return []

    entries: list[LogEntry] = []
    for stream_obj in results:
        labels: dict = stream_obj.get("stream", {})
        values: list = stream_obj.get("values", [])
        level = _extract_level(labels)
        for ts_ns, line in values:
            entries.append(
                {
                    "ts": format_timestamp(ts_ns),
                    "ts_ns": ts_ns,
                    "message": line,
                    "level": level,
                    "labels": labels,
                }
            )

    entries.sort(key=lambda e: e["ts"], reverse=True)
    return entries


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

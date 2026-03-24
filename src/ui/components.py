import json

import streamlit as st

from src.core.parser import INSPECTABLE_LABELS
from src.utils.helpers import truncate

# Maps normalised level string to the CSS class suffix and emoji prefix.
_LEVEL_META = {
    "error": ("error", "🔴"),
    "warn":  ("warn",  "🟡"),
    "info":  ("info",  "🟢"),
    "debug": ("debug", "🔵"),
    "trace": ("trace", "🟣"),
}


def render_log_row(row: dict, row_key: str) -> None:
    """Render a single log entry as a collapsible expander.

    Args:
        row:     Dict with keys ts, ts_ns, message, level, labels.
        row_key: A unique string key used to namespace Streamlit widget keys.
    """
    level = row.get("level", "")
    level_css, level_icon = _LEVEL_META.get(level, ("", "⚪"))
    ts_str = row["ts"].strftime("%Y-%m-%d %H:%M:%S UTC")
    message_preview = truncate(row["message"], 100)

    header = f"{level_icon} `{ts_str}` &nbsp; {message_preview}"

    with st.expander(header, expanded=False):
        _render_labels_table(row["labels"], row_key)


def _render_labels_table(labels: dict, row_key: str) -> None:
    """Render the labels dict as a two-column table with optional eye buttons."""
    for label_key, label_value in labels.items():
        col_key, col_val, col_btn = st.columns([2, 6, 1])

        with col_key:
            st.markdown(f'<span class="label-key">{label_key}</span>', unsafe_allow_html=True)

        with col_val:
            st.markdown(f'<span class="label-value">{label_value}</span>', unsafe_allow_html=True)

        with col_btn:
            if label_key in INSPECTABLE_LABELS:
                btn_key = f"eye_{row_key}_{label_key}"
                if st.button("👁", key=btn_key, help=f"Inspect {label_key}"):
                    _show_json_dialog(label_key, label_value)


@st.dialog("JSON Inspector")
def _show_json_dialog(label_key: str, raw_value: str) -> None:
    """Modal dialog that renders a JSON label value as an interactive tree."""
    st.caption(f"Label: `{label_key}`")
    try:
        parsed = json.loads(raw_value)
        st.json(parsed)
    except (json.JSONDecodeError, TypeError):
        st.code(raw_value, language="text")

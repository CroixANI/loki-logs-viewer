import json

import streamlit as st

from src.core.parser import parse_loki_json


def init_state() -> None:
    """Initialize all session_state keys. Safe to call on every rerun."""
    if "files" not in st.session_state:
        st.session_state["files"] = {}        # filename -> list[LogEntry]
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = None
    if "page_sizes" not in st.session_state:
        st.session_state["page_sizes"] = {}   # filename -> int (rows visible)


@st.cache_data(show_spinner=False)
def _cached_parse(file_bytes: bytes) -> list:
    """Cache-wrapped parser — avoids re-processing on every UI interaction."""
    raw = json.loads(file_bytes)
    return parse_loki_json(raw)


def add_file(filename: str, file_bytes: bytes) -> None:
    """Parse and store a new file. No-op if filename is already loaded."""
    if filename in st.session_state["files"]:
        return
    entries = _cached_parse(file_bytes)
    st.session_state["files"][filename] = entries
    st.session_state["page_sizes"][filename] = 500
    st.session_state["active_tab"] = filename


def remove_file(filename: str) -> None:
    """Remove a loaded file and clean up related state."""
    st.session_state["files"].pop(filename, None)
    st.session_state["page_sizes"].pop(filename, None)
    remaining = list(st.session_state["files"].keys())
    st.session_state["active_tab"] = remaining[-1] if remaining else None


def load_more(filename: str, increment: int = 500) -> None:
    """Extend the visible row count for a file by increment."""
    current = st.session_state["page_sizes"].get(filename, 500)
    st.session_state["page_sizes"][filename] = current + increment

import re

import streamlit as st

from src.core.filter import apply_filters, LEVEL_ORDER
from src.core.state import add_file, remove_file, load_more
from src.ui.components import render_log_row


def render_sidebar() -> None:
    """Render the sidebar: file uploader and loaded sessions list."""
    with st.sidebar:
        st.markdown("### 🔭 Loki Viewer")
        st.divider()

        uploaded = st.file_uploader(
            "Upload Loki JSON export",
            type=["json"],
            accept_multiple_files=False,
            key="file_uploader",
            label_visibility="collapsed",
        )
        if uploaded is not None:
            add_file(uploaded.name, uploaded.getvalue())

        if st.session_state["files"]:
            st.markdown("**Loaded sessions**")
            for filename in list(st.session_state["files"].keys()):
                col_name, col_close = st.columns([5, 1])
                with col_name:
                    st.markdown(f"📄 `{filename}`")
                with col_close:
                    if st.button("✕", key=f"close_{filename}", help=f"Close {filename}"):
                        remove_file(filename)
                        st.rerun()


def render_main() -> None:
    """Render the main area: one tab per loaded file with paginated log rows."""
    files = st.session_state["files"]

    if not files:
        st.info("Upload a Loki JSON export using the sidebar to get started.")
        return

    tab_labels = list(files.keys())
    tabs = st.tabs(tab_labels)

    for tab, filename in zip(tabs, tab_labels):
        with tab:
            _render_file_tab(filename)


def _render_file_tab(filename: str) -> None:
    """Render filter controls and paginated log rows for a single file tab."""
    entries = st.session_state["files"][filename]
    total = len(entries)

    if total == 0:
        st.warning("No log entries found in this file.")
        return

    # ── Filter controls ───────────────────────────────────────────────────────
    present_levels = _levels_present(entries)
    search, level, use_regex = _render_filter_controls(filename, present_levels)

    # ── Apply filters ─────────────────────────────────────────────────────────
    regex_error = None
    try:
        filtered = apply_filters(entries, search=search, level=level, use_regex=use_regex)
    except re.error as exc:
        regex_error = str(exc)
        filtered = []

    if regex_error:
        st.error(f"Invalid regex: {regex_error}")

    matched = len(filtered)
    if search or level != "all":
        st.caption(f"**{matched:,}** / {total:,} entries match")

    # ── Paginated rows ────────────────────────────────────────────────────────
    page_size = st.session_state["page_sizes"].get(filename, 500)
    visible = filtered[:page_size]

    if not regex_error:
        st.caption(f"Showing {min(page_size, matched):,} of {matched:,} entries (newest first)")

    for idx, entry in enumerate(visible):
        render_log_row(entry, row_key=f"{filename}_{idx}")

    if page_size < matched:
        remaining = matched - page_size
        if st.button(
            f"Load 500 more  ({remaining:,} remaining)",
            key=f"load_more_{filename}",
        ):
            load_more(filename)
            st.rerun()


def _render_filter_controls(filename: str, present_levels: list) -> tuple:
    """Render search + level filter controls. Returns (search, level, use_regex)."""
    col_search, col_level, col_regex = st.columns([4, 2, 1])

    with col_search:
        search = st.text_input(
            "Search",
            placeholder="🔍  Keyword or regex…",
            key=f"search_{filename}",
            label_visibility="collapsed",
        )

    with col_level:
        level_options = ["all"] + present_levels
        level = st.selectbox(
            "Level",
            options=level_options,
            format_func=lambda x: "ALL LEVELS" if x == "all" else x.upper(),
            key=f"level_{filename}",
            label_visibility="collapsed",
        )

    with col_regex:
        use_regex = st.checkbox("Regex", key=f"regex_{filename}")

    return search, level, use_regex


def _levels_present(entries: list) -> list:
    """Return level values present in entries, sorted by severity order."""
    found = {e["level"] for e in entries if e["level"]}
    return [lvl for lvl in LEVEL_ORDER if lvl in found]

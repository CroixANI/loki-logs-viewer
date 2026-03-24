import streamlit as st

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
    """Render all paginated log rows for a single file tab."""
    df = st.session_state["files"][filename]
    page_size = st.session_state["page_sizes"].get(filename, 500)
    total = len(df)

    if total == 0:
        st.warning("No log entries found in this file.")
        return

    visible = df.head(page_size)

    st.caption(f"Showing {min(page_size, total):,} of {total:,} entries (newest first)")

    for idx, row in visible.iterrows():
        render_log_row(row.to_dict(), row_key=f"{filename}_{idx}")

    if page_size < total:
        remaining = total - page_size
        if st.button(
            f"Load 500 more  ({remaining:,} remaining)",
            key=f"load_more_{filename}",
        ):
            load_more(filename)
            st.rerun()

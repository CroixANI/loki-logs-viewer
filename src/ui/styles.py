from pathlib import Path

import streamlit as st

_CSS_PATH = Path(__file__).parent.parent.parent / "assets" / "style.css"


def inject_css() -> None:
    """Read assets/style.css and inject it into the Streamlit app.

    Must be called once near the top of app.py, after st.set_page_config().
    """
    css = _CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

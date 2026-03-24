import streamlit as st

# Must be the very first Streamlit call.
st.set_page_config(
    page_title="Loki Viewer",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.ui.styles import inject_css
from src.core.state import init_state
from src.ui.layout import render_sidebar, render_main

inject_css()
init_state()
render_sidebar()
render_main()

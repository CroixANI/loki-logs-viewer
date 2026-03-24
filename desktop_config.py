"""Desktop window configuration for the pywebview launcher."""

APP_TITLE = "Loki Viewer"
APP_WIDTH = 1400
APP_HEIGHT = 900
SERVER_PORT = 8501
SERVER_URL = f"http://localhost:{SERVER_PORT}"

# Streamlit flags applied when launched in desktop mode.
STREAMLIT_ARGS = [
    "--server.headless=true",
    "--server.runOnSave=false",
    f"--server.port={SERVER_PORT}",
    "--browser.gatherUsageStats=false",
    "--theme.base=dark",
]

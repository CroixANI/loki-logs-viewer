"""Desktop launcher — starts Streamlit then opens a native pywebview window.

Usage:
    python run_app.py

For development without the desktop window use:
    streamlit run app.py
"""
import sys
import os
import threading
import time
from urllib.request import urlopen
from urllib.error import URLError


def resource_path(relative_path: str) -> str:
    """Resolve paths correctly both in dev and when bundled by PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def _wait_for_server(url: str, timeout: int = 30) -> bool:
    """Poll url until it responds or timeout (seconds) is reached."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urlopen(url, timeout=1)
            return True
        except (URLError, OSError):
            time.sleep(0.2)
    return False


def _run_streamlit(app_path: str) -> None:
    """Start the Streamlit server (blocking — meant to run in a thread)."""
    from desktop_config import STREAMLIT_ARGS
    from streamlit.web import cli as stcli

    sys.argv = ["streamlit", "run", app_path] + STREAMLIT_ARGS
    sys.exit(stcli.main())


def main() -> None:
    import webview
    from desktop_config import APP_TITLE, APP_WIDTH, APP_HEIGHT, SERVER_URL

    app_path = resource_path("app.py")

    # Start Streamlit in a background daemon thread.
    server_thread = threading.Thread(
        target=_run_streamlit,
        args=(app_path,),
        daemon=True,
    )
    server_thread.start()

    # Wait until Streamlit is ready before showing the window.
    if not _wait_for_server(SERVER_URL):
        print("ERROR: Streamlit did not start within 30 seconds.", file=sys.stderr)
        sys.exit(1)

    # Open the native window on the main thread (required by pywebview).
    window = webview.create_window(
        APP_TITLE,
        SERVER_URL,
        width=APP_WIDTH,
        height=APP_HEIGHT,
        resizable=True,
        min_size=(800, 600),
    )
    # gui=None lets pywebview pick the best backend for the platform:
    # EdgeChromium (WebView2) on Windows, WKWebView on macOS.
    webview.start(gui=None)

    # Reaching here means the window was closed — the daemon thread dies with us.


if __name__ == "__main__":
    main()

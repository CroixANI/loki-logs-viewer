"""Desktop launcher — starts Streamlit then opens a native pywebview window.

Usage:
    python run_app.py

For development without the desktop window use:
    streamlit run app.py

Logs are written to %TEMP%/LokiViewer.log (Windows) or /tmp/LokiViewer.log
so startup errors remain visible even when the EXE runs without a console.
"""
import sys
import os
import logging
import tempfile
import threading
import time
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

# ── File logging (console is hidden in the packaged EXE) ─────────────────────
_log_path = Path(tempfile.gettempdir()) / "LokiViewer.log"
logging.basicConfig(
    filename=str(_log_path),
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)
log = logging.getLogger(__name__)


def resource_path(relative_path: str) -> str:
    """Resolve paths correctly both in dev and when bundled by PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def _wait_for_server(url: str, timeout: int = 60) -> bool:
    """Poll url until it responds or timeout (seconds) is reached."""
    log.info("Waiting for Streamlit at %s (timeout %ds)", url, timeout)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urlopen(url, timeout=1)
            log.info("Streamlit is ready")
            return True
        except (URLError, OSError):
            time.sleep(0.25)
    log.error("Streamlit did not respond within %ds", timeout)
    return False


def _run_streamlit(app_path: str) -> None:
    """Start the Streamlit server (blocking — meant to run in a thread).

    NOTE: Do NOT call sys.exit() here. Calling sys.exit() inside a non-main
    thread raises SystemExit in that thread only, which kills the server
    before it starts serving and causes _wait_for_server to time out.
    """
    try:
        from desktop_config import STREAMLIT_ARGS
        from streamlit.web import cli as stcli

        log.info("Starting Streamlit: %s", app_path)
        sys.argv = ["streamlit", "run", app_path] + STREAMLIT_ARGS
        stcli.main()
        log.info("Streamlit exited normally")
    except Exception:
        log.exception("Streamlit thread raised an exception")


def main() -> None:
    log.info("LokiViewer starting (Python %s)", sys.version)
    log.info("Log file: %s", _log_path)

    from desktop_config import APP_TITLE, APP_WIDTH, APP_HEIGHT, SERVER_URL

    app_path = resource_path("app.py")
    log.info("app_path: %s", app_path)

    # Start Streamlit in a background daemon thread.
    server_thread = threading.Thread(
        target=_run_streamlit,
        args=(app_path,),
        daemon=True,
    )
    server_thread.start()

    if not _wait_for_server(SERVER_URL):
        log.error("Giving up — see %s for details", _log_path)
        sys.exit(1)

    # Open the native window on the main thread (required by pywebview).
    log.info("Opening pywebview window")
    try:
        import webview
        webview.create_window(
            APP_TITLE,
            SERVER_URL,
            width=APP_WIDTH,
            height=APP_HEIGHT,
            resizable=True,
            min_size=(800, 600),
        )
        # Explicitly request the EdgeChromium backend on Windows.
        webview.start(gui="edgechromium")
    except Exception:
        log.exception("pywebview failed — falling back to system browser")
        import webbrowser
        webbrowser.open(SERVER_URL)
        server_thread.join()  # Keep the process alive until Streamlit exits
        return

    log.info("Window closed — exiting")


if __name__ == "__main__":
    main()

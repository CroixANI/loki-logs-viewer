import sys
import os
import threading
import webbrowser
import time


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def open_browser():
    # Wait briefly for Streamlit to start, then open the browser
    time.sleep(3)
    webbrowser.open("http://localhost:8501")


if __name__ == '__main__':
    from streamlit.web import cli as stcli

    app_path = resource_path("app.py")
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--browser.serverAddress=localhost",
        "--theme.base=dark",
    ]

    threading.Thread(target=open_browser, daemon=True).start()
    sys.exit(stcli.main())

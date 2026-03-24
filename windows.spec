# PyInstaller spec for Windows — produces dist/LokiViewer.exe
#
# Build command (run from project root with venv active):
#   pip install pyinstaller pywebview
#   pyinstaller windows.spec
#
# Requirements:
#   - Windows 10+ with WebView2 runtime installed (ships with Edge/Win11).
#     Silent installer: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
#   - PyInstaller 6+

import sys
from pathlib import Path
import streamlit

STREAMLIT_DIR = Path(streamlit.__file__).parent
PROJECT_ROOT  = Path(SPEC).parent          # noqa: F821  (SPEC is a PyInstaller built-in)

block_cipher = None

a = Analysis(
    [str(PROJECT_ROOT / "run_app.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        # Streamlit static assets (HTML, JS, CSS)
        (str(STREAMLIT_DIR / "static"),  "streamlit/static"),
        (str(STREAMLIT_DIR / "runtime"), "streamlit/runtime"),
        # App assets and source
        (str(PROJECT_ROOT / "assets"),   "assets"),
        (str(PROJECT_ROOT / "src"),      "src"),
        (str(PROJECT_ROOT / "app.py"),   "."),
        (str(PROJECT_ROOT / "desktop_config.py"), "."),
    ],
    hiddenimports=[
        "streamlit",
        "streamlit.web.cli",
        "streamlit.runtime.scriptrunner",
        "webview",
        "webview.platforms.edgechromium",
        "clr",           # pythonnet — required by pywebview on Windows
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "scipy"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="LokiViewer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,      # No terminal window — windowed app
    icon=None,          # Replace with path to .ico file if desired
)

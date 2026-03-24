# PyInstaller spec for macOS — produces dist/LokiViewer.app
#
# Build command (run from project root with venv active):
#   pip install pyinstaller pywebview
#   pyinstaller macos.spec
#
# Distribution notes:
#   - For local use the .app bundle works as-is.
#   - For distribution outside your own machine, macOS requires code signing:
#       codesign --deep --force --sign "Developer ID Application: <Name>" dist/LokiViewer.app
#     and notarisation via Apple's notarytool before Gatekeeper will allow it.
#   - pywebview uses WKWebView (WebKit) — built into macOS, no extra runtime needed.

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
        "webview.platforms.cocoa",
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
    [],
    exclude_binaries=True,
    name="LokiViewer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="LokiViewer",
)

app = BUNDLE(  # noqa: F821
    coll,
    name="LokiViewer.app",
    icon=None,          # Replace with path to .icns file if desired
    bundle_identifier="com.lokiviewer.app",
    info_plist={
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "12.0",
    },
)

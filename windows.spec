# PyInstaller spec for Windows — produces dist/LokiViewer.exe
#
# Build command (run from project root with venv active):
#   pip install -r requirements-desktop.txt
#   pyinstaller windows.spec
#
# Requirements:
#   - Windows 10+ with WebView2 runtime installed (ships with Edge/Win11).
#     Silent installer: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
#   - PyInstaller 6+

from pathlib import Path
from PyInstaller.utils.hooks import collect_all, copy_metadata

PROJECT_ROOT = Path(SPEC).parent  # noqa: F821  (SPEC is a PyInstaller built-in)

# collect_all() is equivalent to --collect-all on the CLI.
# It captures every submodule, data file, and binary for the package —
# essential for complex packages like streamlit that load modules dynamically.
st_datas,  st_binaries,  st_hidden  = collect_all('streamlit')
wv_datas,  wv_binaries,  wv_hidden  = collect_all('webview')

block_cipher = None

a = Analysis(
    [str(PROJECT_ROOT / "run_app.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[] + st_binaries + wv_binaries,
    datas=[
        # App source and assets
        (str(PROJECT_ROOT / "assets"),          "assets"),
        (str(PROJECT_ROOT / "src"),             "src"),
        (str(PROJECT_ROOT / "app.py"),          "."),
        (str(PROJECT_ROOT / "desktop_config.py"), "."),
    ] + st_datas + wv_datas
      + copy_metadata('streamlit'),   # needed for importlib.metadata version checks
    hiddenimports=[
        "streamlit.web.cli",
        "streamlit.runtime.scriptrunner",
        "webview",
        "webview.platforms.edgechromium",
    ] + st_hidden + wv_hidden,
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

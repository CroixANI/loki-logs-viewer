# 🔭 Loki Viewer

A clean, fast desktop viewer for Grafana Loki JSON stream exports, built with Python + Streamlit.

---

## Features

- ⚡ **Grafana Loki JSON support** — open Loki HTTP API query-response files directly
- 📋 **Multi-file tabs** — open several log files at once with per-tab close buttons
- 🎨 **Log level coloring** — ERROR (red), WARN (yellow), INFO (green), DEBUG (blue), TRACE (purple)
- 🔍 **Search & filter** — keyword or regex search with level filter
- ▸ **Expandable rows** — click any row to reveal all stream labels as a key/value panel
- 👁 **MessageBody JSON viewer** — eye button opens nested JSON in a modal

---

## How to run

### Option 1 — Windows EXE (no Python or Docker required)

1. Go to the [Releases](../../releases) page and download `LokiViewer.exe`
2. Double-click to run — the app opens in a native window automatically

> Requires the **WebView2 runtime** (ships with Windows 11 and Edge; for Windows 10 install it from [Microsoft](https://developer.microsoft.com/en-us/microsoft-edge/webview2/))

---

### Option 2 — Docker (no Python required)

**Prerequisites:** Docker Desktop installed and running.

**Windows** — double-click `launch-docker.bat`

**macOS / Linux**
```sh
make up        # build image, start container, open browser
make down      # stop the container
make restart   # rebuild and restart
make logs      # tail container logs
```

Or with plain Docker Compose:
```sh
docker compose up -d --build
# then open http://localhost:8501
```

---

### Option 3 — Run locally (development)

**Prerequisites:** Python 3.11+

**1. Create and activate a virtual environment**

macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate
```

Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

To deactivate when done:
```bash
deactivate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` in your browser.

**4. Run tests**
```bash
PYTHONPATH=. pytest tests/ -v
```

Windows:
```cmd
set PYTHONPATH=. && pytest tests/ -v
```

Or with Make:
```bash
make test
```

---

## Log Level Detection

Loki JSON files: level is read from the `severity_text`, `detected_level`, `level`, or `severity` stream label (OpenTelemetry conventions supported).

Severity order: `ERROR` → `WARN` → `INFO` → `DEBUG` → `TRACE`

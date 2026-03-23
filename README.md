# 🔭 LogLens — Log Viewer

A clean, fast log viewer for structured and plain-text log files, built with Python + Streamlit.

---

## Features

- ⚡ **Grafana Loki JSON support** — open Loki HTTP API query-response files directly
- 📋 **Multi-file tabs** — open several log files at once with per-tab close buttons
- 🎨 **Log level coloring** — CRITICAL (orange), ERROR (red), WARN (yellow), INFO (green), DEBUG (blue), TRACE (purple)
- 🔍 **Search & highlight** — keyword or regex search with match highlighting
- 📊 **Level filtering** — filter by severity level
- 📈 **Stats bar** — see line counts and level distribution at a glance
- ▸ **Expandable Loki rows** — click any row to reveal all stream labels as a key/value panel
- 👁 **MessageBody JSON viewer** — eye button opens nested JSON formatted and syntax-highlighted in a modal
- 🕓 **Recent files** — last 5 opened files remembered across sessions, one click to reopen

---

## Running on Windows

### Prerequisites

1. Install **Python 3.11 or newer** from [python.org](https://python.org/downloads)
   - During installation check **"Add Python to PATH"**
2. Download or clone this repository and extract it to a folder of your choice

### Start the app

**Double-click `launch.bat`** — it will:
1. Verify Python is installed
2. Install all required packages automatically (first run only)
3. Start the LogLens server
4. Open your browser at `http://localhost:8501`

> If your browser does not open automatically, navigate to `http://localhost:8501` manually.

### Stop the app

Close the terminal window that opened, or press `Ctrl + C` inside it.

### Manual start (alternative)

If you prefer the command line:

```cmd
pip install -r requirements.txt
streamlit run app.py
```

---

## Supported File Formats

| Extension | Description |
|---|---|
| `.json` | Grafana Loki HTTP API query-response (`resultType: streams`) |
| `.log` | Any text-based log file |
| `.txt` | Plain text logs |
| `.out` | Standard output captures |
| `.err` | Standard error captures |

---

## Log Level Detection

For plain-text files, LogLens auto-detects severity by scanning each line for keywords:

`CRITICAL` / `FATAL` → `ERROR` → `WARN` / `WARNING` → `INFO` → `DEBUG` → `TRACE`

For Loki JSON files, the level is read directly from the `severity_text` or `detected_level` stream label.

Works with Log4j, NLog, Serilog, Python logging, syslog, OpenTelemetry, and most common formats.

---

## Data Storage

LogLens stores recent file history and a file cache in `%USERPROFILE%\.loglens\`:

```
~\.loglens\
├── recent_files.json   ← list of up to 5 recently opened files
└── cache\              ← copies of uploaded files for quick reopening
```

This folder is created automatically on first use.

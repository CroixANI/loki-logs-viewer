# 🔭 LogLens — Windows Log Viewer

A clean, fast log viewer built with Python + Streamlit.

## Features
- 📄 **Multi-file tabs** — open several log files at once
- 🎨 **Log level coloring** — ERROR (red), WARN (yellow), INFO (green), DEBUG (blue), TRACE (purple)
- 🔍 **Search & highlight** — keyword or regex search with match highlighting
- 📊 **Level filtering** — filter by ERROR / WARN / INFO / DEBUG / TRACE
- 📈 **Stats bar** — see error/warn counts at a glance

## Quick Start (Windows)

### Option A — Double-click launcher
```
1. Install Python 3.9+ from https://python.org
2. Double-click launch.bat
```

### Option B — Manual
```bash
pip install streamlit
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Supported Formats
- `.log` — any text-based log file
- `.txt` — plain text logs
- `.out` / `.err` — stdout/stderr captures

## Log Level Detection
LogLens auto-detects log levels by scanning each line for keywords:
`CRITICAL` / `FATAL` / `ERROR` / `WARN` / `WARNING` / `INFO` / `DEBUG` / `TRACE`

Works with Log4j, NLog, Python logging, syslog, and most common formats.

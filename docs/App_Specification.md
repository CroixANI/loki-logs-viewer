# Project: Loki Log Viewer (Desktop Edition)

## Overview
A standalone desktop application built with Python, Streamlit, and `streamlit-desktop-app`. The app acts as a local log viewer for JSON files exported from Grafana Loki (HTTP Query Response format).

## Data Format
- **Input:** JSON files matching the Loki `matrix` or `streams` response structure.
- **Key Fields:** `result.values` (containing timestamps and log strings) and `result.stream` (containing labels).

## Functional Requirements
1. **File Management:**
   - Sidebar file uploader to "Open" JSON files.
   - Each opened file must appear as a new tab in the main view.
   - Tabs must be closable (managed via session state).
2. **Log Display:**
   - Display logs chronologically.
   - Each line is a collapsible element (Expander).
   - **Collapsed View:** Shows Timestamp and the raw Log Message.
   - **Expanded View:** Shows a table of all labels/metadata associated with that line.
3. **JSON Detail View:**
   - Specific labels (e.g., `content`, `payload`, `request`) contain stringified JSON.
   - Provide an "Eye" icon/button next to these labels.
   - Clicking the button opens a Modal (`st.dialog`) showing the JSON formatted with syntax highlighting.

## UI/UX Style
- **Theme:** Dark mode (matching Grafana aesthetics).
- **Layout:** Wide mode.
- **Components:** `st.tabs`, `st.expander`, `st.json`, `st.column`.

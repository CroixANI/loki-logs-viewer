# Implementation Plan: Loki Viewer Development

## 1. Project Directory Structure
The implementation MUST follow this structure. Do not consolidate into a single file.

```text
loki-desktop-viewer/
├── app.py                # Entry point & Tab orchestration
├── requirements.txt      # Pinned dependencies
├── assets/
│   └── style.css         # Custom CSS (Log colors, button positioning)
├── src/
│   ├── core/
│   │   ├── parser.py     # Logic: JSON -> Clean Pandas DataFrame (no streamlit imports)
│   │   └── state.py      # Logic: Session State initialization/updates & cached wrappers
│   ├── ui/
│   │   ├── components.py # UI: Log Row, JSON Dialog, Eye Button
│   │   ├── layout.py     # UI: Main Tab rendering & Sidebar
│   │   └── styles.py     # Utility: CSS Injection logic
│   └── utils/
│       └── helpers.py    # Logic: Timestamp formatting & path handling
└── desktop_config.py     # Configuration for streamlit-desktop-app
```

## 2. Implementation Phases

### Phase 1: Project Setup
1. Create `requirements.txt` with pinned versions for all dependencies: `streamlit`, `pandas`, `streamlit-desktop-app`, `pywebview`.
2. Create the full directory structure above (empty placeholder files where needed).
3. Create `src/utils/helpers.py` with:
   - `format_timestamp(ns_str)`: converts a 19-digit nanosecond Unix epoch string to an ISO 8601 `datetime` object.
   - Any other pure utility functions (string truncation, path helpers).

### Phase 2: Core Parsing (`src/core/`)
1. Create `parser.py` — **no `streamlit` imports allowed here**.
   - `parse_loki_json(raw_dict) -> pd.DataFrame`: accepts the parsed JSON dict and returns a clean, flat DataFrame.
   - **Transform Logic:** Flatten the nested `values` so each log line is a standalone record linked to its parent `stream` labels.
   - **Time Conversion:** Call `helpers.format_timestamp()` to convert nanosecond strings to `datetime` objects.
   - **Sort:** Return logs sorted by timestamp descending by default.
2. Create `state.py`:
   - Initialize `st.session_state` keys: `files` (dict of filename → DataFrame) and `active_tab` (currently selected filename).
   - Wrap `parser.parse_loki_json` with `@st.cache_data` here (not in `parser.py`) to avoid re-processing on every UI interaction.
   - Expose action functions (e.g., `add_file`, `remove_file`) that are the only way to mutate `st.session_state['files']`.

### Phase 3: Styling (`assets/` & `src/ui/styles.py`)
1. Define CSS classes in `assets/style.css`: `.log-row`, `.log-timestamp`, `.log-level-error`, `.log-level-warn`, `.log-level-info`, `.eye-button`.
2. Implement `inject_css()` in `src/ui/styles.py`: reads `assets/style.css` and injects it into the Streamlit app using `st.markdown`.

### Phase 4: Components (`src/ui/components.py`)
1. Create `render_log_row(row_data)`:
   - Uses `st.expander` with header format: `{timestamp} | {level} | {message[:100]}`.
   - Inside the expander, displays a 2-column table of all stream labels and values.
   - For labels in `['MessageBody', 'message.body']`, renders an "Eye" button (`st.button("👁️", key=...)`).
2. Create `show_json_dialog(label_value)` decorated with `@st.dialog("JSON Detail")`:
   - Calls `st.json(label_value)` for interactive tree-view and syntax highlighting.
   - Triggered by the Eye button.

### Phase 5: Orchestration (`app.py`)
1. Call `st.set_page_config(layout="wide")` as the first Streamlit call.
2. Call `inject_css()` from `src/ui/styles.py`.
3. Call state initializer from `src/core/state.py`.
4. Import and render the sidebar (file uploader + loaded sessions list with close buttons) from `src/ui/layout.py`.
5. Iterate through `st.session_state['files']` to build `st.tabs()`, one tab per loaded file.
6. Inside each tab, apply pagination: show the last 500 log entries by default, with a "Load 500 More" button at the bottom that extends the visible slice.
7. Call `render_log_row(row)` for each visible row.

### Phase 6: Desktop Packaging
1. Create `desktop_config.py` for `streamlit-desktop-app` / `pywebview`:
   - Configure window title, size, and ensure the app opens in a standalone window (no browser).
2. **Windows build:** Generate a PyInstaller spec file or command that bundles the Streamlit runtime, pywebview, and all assets into a single `.exe`.
3. **macOS build:** Generate a separate PyInstaller command producing a `.app` bundle. Note: macOS requires code signing for distribution; document this requirement.
4. **Testing:** Verify that closing the window kills the background Python process on both platforms.

## 3. Coding Guidelines for LLM
* **No Globals**: Use functions and return values.
* **No Inline Styles**: Use the classes defined in `style.css`.
* **Pure Logic**: `parser.py` must not import `streamlit`. Cache wrappers live in `state.py`.
* **Atomic UI**: Keep UI components small and reusable.
* **`st.set_page_config`** must be the very first Streamlit call in `app.py`.

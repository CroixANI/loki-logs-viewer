# Implementation Plan: Loki Viewer Development

## 1. Project Directory Structure
The implementation MUST follow this structure. Do not consolidate into a single file.

```text
loki-desktop-viewer/
├── app.py                # Entry point & Tab orchestration
├── assets/
│   └── style.css         # Custom CSS (Log colors, button positioning)
├── src/
│   ├── core/
│   │   ├── parser.py     # Logic: JSON -> Clean Pandas DataFrame
│   │   └── state.py      # Logic: Session State initialization/updates
│   ├── ui/
│   │   ├── components.py # UI: Log Row, JSON Dialog, Eye Button
│   │   ├── layout.py     # UI: Main Tab rendering & Sidebar
│   │   └── styles.py     # Utility: CSS Injection logic
│   └── utils/
│       └── helpers.py    # Logic: Timestamp formatting & Path handling
└── desktop_config.py     # Configuration for streamlit-desktop-app
```

## 2. Implementation Phases

### Phase 1: Core & State (src/core/)
1. Create a module `parser.py` with `@st.cache_data` to ingest Loki JSON.
2. **Transform Logic:** Flatten the nested `values` so each log line is a standalone record linked to its parent `stream` labels.
3. **Time Conversion:** Convert Loki's 19-digit nanosecond strings into Python `datetime` objects.
4. **Sort:** Ensure logs are sorted by time (descending by default).
5. Implement `state.py` to handle `st.session_state['files']` (a dict of DataFrames).

### Phase 2: State Management
1. Initialize `st.session_state` keys:
    - `files`: A dictionary where key=filename, value=parsed_dataframe.
    - `active_tab`: Tracks the currently selected file.
2. Implement a callback for the file uploader to prevent re-processing on every UI interaction.

### Phase 2: Styling (`assets/` & `src/ui/styles.py`)
1. Define CSS classes: `.log-row`, `.log-timestamp`, `.eye-button`.
2. Implement `inject_css()` to read the file and apply it to the Streamlit app.

### Phase 3: Components (`src/ui/components.py`)
1. Create `render_log_row(row_data)` function.
2. Create `@st.dialog` function for the JSON popup.
3. **Layout:** Use `st.set_page_config(layout="wide")`.
4. **Tabs:** Iterate through `st.session_state.files` to generate `st.tabs()`.
5. **Log Rendering:**
    - Use a `for` loop to iterate through the DataFrame.
    - Inside the loop, use `st.expander(f"{row['ts']} | {row['message'][:100]}...")`.
    - Inside the expander, display a 2-column layout for labels and values.
6. **The Eye Button:** - Place `st.button("👁️", key=...)` next to specific labels.
    - Button triggers a function decorated with `@st.dialog("JSON Detail")` that runs `st.json(label_value)`.

### Phase 4: Orchestration (`app.py`)
1. Import modules and assemble the UI.

### Phase 5: Desktop Build
1. Create `main.py` (the Streamlit entry point).
2. Create `desktop_config.py` for `streamlit-desktop-app`.
3. **Build Command:**
    - Instruction for the LLM: "Generate a PyInstaller command or a build script that bundles the Streamlit library, the 'st-json-view' component, and the webview assets into a single executable."
4. **Testing:** Verify that closing the window kills the background Python process.
5. Ensure `pywebview` is configured to open a standalone window (no browser).

## 3. Coding Guidelines for LLM
* **No Globals**: Use functions and return values.
* **No Inline Styles**: Use the classes defined in `style.css`.
* **Pure Logic**: `parser.py` must not import `streamlit`.
* **Atomic UI**: Keep UI components small and reusable.

---

### Final Check & Next Step

This plan ensures that your application remains scalable. If you want to add a "Search" or "Filter" feature later, you simply add a file to `src/core/` and a component to `src/ui/` without breaking the whole app.

**Would you like me to generate the `style.css` and the `src/ui/styles.py` file to establish the visual foundation for the "Eye" buttons and log lines?**

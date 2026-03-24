# Implementation Plan: Loki Viewer Development

## Phase 1: Data Parsing Engine
1. Create a module `parser.py` to ingest Loki JSON.
2. **Transform Logic:** Flatten the nested `values` so each log line is a standalone record linked to its parent `stream` labels.
3. **Time Conversion:** Convert Loki's 19-digit nanosecond strings into Python `datetime` objects.
4. **Sort:** Ensure logs are sorted by time (descending by default).

## Phase 2: State Management
1. Initialize `st.session_state` keys:
    - `files`: A dictionary where key=filename, value=parsed_dataframe.
    - `active_tab`: Tracks the currently selected file.
2. Implement a callback for the file uploader to prevent re-processing on every UI interaction.

## Phase 3: UI Construction (Main App)
1. **Layout:** Use `st.set_page_config(layout="wide")`.
2. **Tabs:** Iterate through `st.session_state.files` to generate `st.tabs()`.
3. **Log Rendering:**
    - Use a `for` loop to iterate through the DataFrame.
    - Inside the loop, use `st.expander(f"{row['ts']} | {row['message'][:100]}...")`.
    - Inside the expander, display a 2-column layout for labels and values.
4. **The Eye Button:** - Place `st.button("👁️", key=...)` next to specific labels.
    - Button triggers a function decorated with `@st.dialog("JSON Detail")` that runs `st.json(label_value)`.

## Phase 4: Desktop Packaging
1. Create `main.py` (the Streamlit entry point).
2. Create `desktop_config.py` for `streamlit-desktop-app`.
3. **Build Command:**
    - Instruction for the LLM: "Generate a PyInstaller command or a build script that bundles the Streamlit library, the 'st-json-view' component, and the webview assets into a single executable."
4. **Testing:** Verify that closing the window kills the background Python process.

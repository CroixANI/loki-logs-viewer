# Project Code Guidelines: Loki Viewer

## 1. Directory Structure
The application MUST follow this structure to ensure maintainability:
- `/assets`: CSS files and icons.
- `/src/core`: Business logic (Loki JSON parsing, data filtering).
- `/src/ui`: Pure UI components (custom cards, dialogs, headers).
- `/src/utils`: Helper functions (formatters, state initializers).
- `app.py`: The entry point (routing and main layout only).

## 2. State Management Rules
- All file data must be stored in `st.session_state['files']`.
- Never modify session state directly inside a UI component; use "Action" functions located in `/src/core`.

## 3. Component Architecture
- **Functional Components:** Every UI element (e.g., a Log Row) should be a function that accepts data and returns nothing (e.g., `render_log_row(data)`).
- **Separation of Concerns:** `parser.py` should return a Clean Pandas DataFrame; it should NOT contain any `st.` calls.

## 4. CSS & Styling
- Do not use inline `style=` arguments in Markdown.
- All custom CSS must reside in `assets/style.css`.
- Inject CSS once at the top of `app.py` using a utility function.
- Use CSS selectors carefully to target specific elements (e.g., `.log-timestamp`).

## 5. Performance
- Use `@st.cache_data` for the JSON parsing functions to avoid re-processing 50MB files on every click.
- The `@st.cache_data` wrapper must live in `src/core/state.py`, not in `parser.py`, to keep `parser.py` free of Streamlit imports.

## 6. Dependencies
- All dependencies must be pinned to exact versions in `requirements.txt` (e.g., `streamlit==1.35.0`).
- This is essential for reproducible builds across Windows and macOS.

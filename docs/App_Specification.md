# Specification: Loki Desktop Log Viewer

## 1. Goal
A desktop application to visualize Loki JSON stream exports. It must provide a "Grafana-like" experience for inspecting logs and their associated metadata (labels), with special handling for JSON-encoded label values.

## 2. Technical Stack
- **Language:** Python 3.10+
- **UI Framework:** Streamlit
- **Desktop Wrapper:** `streamlit-desktop-app` (using PyWebview)
- **Data Handling:** Pandas (for log sorting/filtering)

## 3. Input Data Architecture (Loki Streams)
- **Format:** JSON HTTP Response from Grafana Loki `/loki/api/v1/query_range`.
- **Target Path:** `data.result[]`
- **Logic:** - Each `result` contains a `stream` object (labels) and `values` (list of [timestamp, log_line]).
    - Timestamps are in nanoseconds (Unix Epoch); must be converted to ISO 8601.

## 4. UI Requirements
- **Sidebar:** - File uploader (Accepts `.json`).
    - List of "Loaded Sessions" with a "Close" (X) button for each.
- **Main View (Tabs):**
    - One tab per JSON file.
    - Each tab contains a scrollable list of log entries.
- **Log Entry Component:**
    - **Header (Collapsed):** Timestamp (Blue text) | Log Level (Color-coded if found) | Truncated Log Message.
    - **Body (Expanded):** A table showing all labels from that stream.
    - **JSON Inspector:** If a label key is in `['msg', 'content', 'payload', 'data']`, show an "Eye" icon. Clicking it opens a `st.dialog` modal.
- **Modal View:** - Displays the label's value using `st.json()` for interactive tree-view and syntax highlighting.

## 5. Performance Constraints
- Support files up to 50MB.
- Default view: Show last 500 lines with a "Load 500 More" button at the bottom.

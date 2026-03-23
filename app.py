import streamlit as st
import re
import json
import base64
import shutil
from pathlib import Path
from datetime import datetime, timezone

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LogLens",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;800&display=swap');

:root {
    --bg:       #0d0f14;
    --surface:  #13161e;
    --surface2: #1a1e2a;
    --border:   #252a38;
    --accent:   #5b8af5;
    --accent2:  #a78bfa;
    --text:     #c9d1e8;
    --muted:    #505878;
    --error:    #f87171;
    --warn:     #fbbf24;
    --info:     #34d399;
    --debug:    #60a5fa;
    --trace:    #a78bfa;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif;
}
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }
.main .block-container { padding: 1.5rem 2rem; max-width: 100%; }
header[data-testid="stHeader"] { display: none; }

.app-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.89rem;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #5b8af5, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.1rem;
}
.app-subtitle { color: var(--muted); font-size: 1.00rem; margin-bottom: 1.2rem; }

.log-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    height: 60vh;
    overflow-y: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem;
    line-height: 1.75;
}
.log-container::-webkit-scrollbar { width: 5px; }
.log-container::-webkit-scrollbar-track { background: var(--bg); }
.log-container::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

.log-line { display: flex; align-items: flex-start; gap: 0.6rem; padding: 1px 4px; border-radius: 3px; }
.log-line:hover { background: rgba(255,255,255,0.03); }
.line-num { color: var(--muted); min-width: 3.5rem; text-align: right; user-select: none; font-size: 0.84rem; padding-top: 2px; flex-shrink: 0; }
.line-text { flex: 1; white-space: pre-wrap; word-break: break-all; }

.level-ERROR, .level-CRITICAL, .level-FATAL { color: #f87171; }
.level-WARN, .level-WARNING { color: #fbbf24; }
.level-INFO { color: #34d399; }
.level-DEBUG { color: #60a5fa; }
.level-TRACE { color: #a78bfa; }
.level-DEFAULT { color: var(--text); }

.highlight { background: rgba(251,191,36,0.3); border-radius: 2px; padding: 0 2px; color: #000 !important; }

.stats-bar {
    display: flex; gap: 1.2rem; padding: 0.55rem 1rem;
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 8px; margin-bottom: 0.8rem; flex-wrap: wrap; align-items: center;
}
.stat-pill { display: flex; align-items: center; gap: 0.4rem; font-size: 0.95rem; }
.stat-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.stat-count { font-family: 'JetBrains Mono', monospace; font-weight: 600; }

div[data-testid="stTextInput"] input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 7px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.00rem !important;
}

div[data-testid="stButton"] button {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 7px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.95rem !important;
}
div[data-testid="stButton"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

.empty-state {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    height: 40vh; color: var(--muted); gap: 0.6rem;
}
.empty-icon { font-size: 3rem; opacity: 0.35; }
.empty-text { font-size: 1.10rem; }

/* ── Hide native uploader file list ─────────────────────────────────────── */
[data-testid="stFileUploaderFileList"] { display: none !important; }

/* ── Custom tab bar ─────────────────────────────────────────────────────── */
.tab-bar {
    display: flex; flex-wrap: wrap; gap: 2px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.8rem; padding-bottom: 0;
}
.tab-bar div[data-testid="stButton"] button {
    background: none !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 6px 6px 0 0 !important;
    color: var(--muted) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1.05rem !important;
    padding: 0.4rem 0.8rem !important;
    margin-bottom: -1px !important;
    white-space: nowrap !important;
    box-shadow: none !important;
    transition: color 0.15s, border-color 0.15s !important;
}
.tab-bar div[data-testid="stButton"] button:hover {
    color: var(--text) !important;
    border-bottom-color: var(--muted) !important;
    background: rgba(255,255,255,0.03) !important;
}
.tab-bar-active div[data-testid="stButton"] button {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
    background: rgba(91,138,245,0.07) !important;
}
.tab-close div[data-testid="stButton"] button {
    background: none !important;
    border: none !important;
    color: var(--muted) !important;
    font-size: 0.75rem !important;
    padding: 0.4rem 0.3rem !important;
    min-width: unset !important;
    box-shadow: none !important;
}
.tab-close div[data-testid="stButton"] button:hover {
    color: var(--error) !important;
    background: rgba(248,113,113,0.08) !important;
}

/* ── Recent file link buttons ───────────────────────────────────────────── */
section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] {
    background: none !important;
    border: none !important;
    padding: 2px 0 !important;
    color: #5b8af5 !important;
    font-size: 0.92rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"]:hover {
    color: #a78bfa !important;
    text-decoration: underline !important;
    background: none !important;
    border: none !important;
}

/* ── Expandable log rows (Loki labels) ──────────────────────────────────── */
details.log-entry { list-style: none; }
details.log-entry > summary {
    display: flex; align-items: flex-start; gap: 0.6rem;
    padding: 1px 4px; border-radius: 3px;
    cursor: pointer; list-style: none;
}
details.log-entry > summary::-webkit-details-marker { display: none; }
details.log-entry > summary::marker { display: none; }
details.log-entry > summary:hover { background: rgba(255,255,255,0.03); }
details.log-entry[open] > summary { background: rgba(91,138,245,0.07); border-radius: 3px 3px 0 0; }

.expand-arrow {
    color: var(--muted); font-size: 0.76rem; padding-top: 5px;
    flex-shrink: 0; width: 0.8rem; text-align: center;
    transition: transform 0.15s ease;
    user-select: none;
}
details.log-entry[open] .expand-arrow { transform: rotate(90deg); color: var(--accent); }

.labels-panel {
    margin: 0 0 4px 4.8rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-top: none;
    border-radius: 0 0 6px 6px;
    padding: 0.5rem 0.8rem;
    display: grid;
    grid-template-columns: minmax(160px, max-content) 1fr;
    gap: 0 1.2rem;
    font-size: 0.89rem;
}
.label-key {
    color: var(--accent2);
    font-weight: 600;
    padding: 2px 0;
    white-space: nowrap;
    user-select: text;
}
.label-val {
    color: var(--text);
    padding: 2px 0;
    word-break: break-all;
    user-select: text;
}
.label-row-alt .label-key,
.label-row-alt .label-val { background: rgba(255,255,255,0.02); }

/* ── Eye button ─────────────────────────────────────────────────────────── */
.eye-btn {
    background: none; border: none; padding: 0 0 0 0.4rem;
    cursor: pointer; color: #505878; line-height: 1;
    vertical-align: middle; flex-shrink: 0;
    transition: color 0.15s ease;
}
.eye-btn:hover { color: #5b8af5; }
.eye-btn svg { display: block; }

/* ── JSON modal ─────────────────────────────────────────────────────────── */
dialog#json-modal {
    background: #13161e; color: #c9d1e8;
    border: 1px solid #252a38; border-radius: 10px;
    padding: 0; width: min(72vw, 900px); max-height: 80vh;
    box-shadow: 0 24px 60px rgba(0,0,0,0.6);
    font-family: 'JetBrains Mono', monospace;
}
dialog#json-modal[open] { display: flex; flex-direction: column; }
dialog#json-modal::backdrop {
    background: rgba(0,0,0,0.55); backdrop-filter: blur(3px);
}
.modal-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.7rem 1rem; border-bottom: 1px solid #252a38;
    font-family: 'Syne', sans-serif; font-size: 0.82rem; font-weight: 600;
    flex-shrink: 0;
}
.modal-title { color: #a78bfa; letter-spacing: 0.02em; }
.modal-close {
    background: none; border: none; color: #505878; font-size: 1rem;
    cursor: pointer; padding: 2px 6px; border-radius: 4px;
    transition: color 0.15s, background 0.15s;
}
.modal-close:hover { color: #c9d1e8; background: #1a1e2a; }
.modal-body {
    overflow-y: auto; padding: 1rem;
    flex: 1;
}
.modal-body::-webkit-scrollbar { width: 5px; }
.modal-body::-webkit-scrollbar-track { background: #0d0f14; }
.modal-body::-webkit-scrollbar-thumb { background: #252a38; border-radius: 4px; }
pre#json-content {
    margin: 0; font-size: 0.76rem; line-height: 1.7;
    white-space: pre-wrap; word-break: break-all;
}
/* JSON syntax colours */
.jk { color: #a78bfa; }   /* key    */
.js { color: #34d399; }   /* string */
.jn { color: #fbbf24; }   /* number */
.jb { color: #60a5fa; }   /* bool   */
.jz { color: #505878; }   /* null   */
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
LEVEL_PATTERNS = [
    (re.compile(r'\b(CRITICAL|FATAL)\b', re.I), 'CRITICAL'),
    (re.compile(r'\b(ERROR)\b', re.I), 'ERROR'),
    (re.compile(r'\b(WARN(?:ING)?)\b', re.I), 'WARN'),
    (re.compile(r'\b(INFO)\b', re.I), 'INFO'),
    (re.compile(r'\b(DEBUG)\b', re.I), 'DEBUG'),
    (re.compile(r'\b(TRACE)\b', re.I), 'TRACE'),
]
LEVEL_ORDER = ['CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE']
LEVEL_COLORS = {
    'CRITICAL': '#fb923c', 'ERROR': '#f87171',
    'WARN': '#fbbf24', 'INFO': '#34d399',
    'DEBUG': '#60a5fa', 'TRACE': '#a78bfa', 'DEFAULT': '#505878',
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def detect_level(line: str) -> str:
    for pattern, level in LEVEL_PATTERNS:
        if pattern.search(line):
            return level
    return 'DEFAULT'

def escape_html(text: str) -> str:
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def highlight_text(text: str, keyword: str) -> str:
    escaped = re.escape(keyword)
    return re.sub(f'({escaped})', r'<span class="highlight">\1</span>', text, flags=re.I)

def parse_file(content: str) -> list:
    result = []
    for i, line in enumerate(content.splitlines(), 1):
        result.append({'num': i, 'text': line, 'level': detect_level(line)})
    return result

_LOKI_LEVEL_MAP = {
    'debug':       'DEBUG',
    'information': 'INFO',
    'info':        'INFO',
    'warning':     'WARN',
    'warn':        'WARN',
    'error':       'ERROR',
    'critical':    'CRITICAL',
    'fatal':       'CRITICAL',
    'trace':       'TRACE',
}

def _ns_to_dt(ns_str: str) -> str:
    """Convert a nanosecond-epoch string to a human-readable UTC timestamp."""
    try:
        ts = int(ns_str) / 1_000_000_000
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' UTC'
    except (ValueError, OSError):
        return ns_str

def parse_loki_json(content: str) -> list | None:
    """Parse a Grafana Loki query-response JSON file into log entries.

    Returns a list of entries on success, or None if the content is not a
    recognisable Loki response (so the caller can fall back to plain-text).
    """
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None

    # Validate Loki envelope
    try:
        streams = data['data']['result']
        if not isinstance(streams, list):
            return None
    except (KeyError, TypeError):
        return None

    result = []
    entry_num = 0

    for stream in streams:
        labels = stream.get('stream', {})
        severity_raw = labels.get('severity_text') or labels.get('detected_level') or ''
        level = _LOKI_LEVEL_MAP.get(severity_raw.lower(), 'DEFAULT')

        service  = labels.get('service_instance_id') or labels.get('service_name', '')
        scope    = labels.get('scope_name', '')

        for value in stream.get('values', []):
            if len(value) < 2:
                continue
            ts_str, message = value[0], value[1]
            ts = _ns_to_dt(ts_str)

            # Build a readable prefix from available metadata
            prefix_parts = [f'[{ts}]']
            if service:
                prefix_parts.append(f'[{service}]')
            if scope:
                prefix_parts.append(f'[{scope}]')
            prefix = ' '.join(prefix_parts)

            entry_num += 1
            result.append({
                'num':    entry_num,
                'text':   f'{prefix} {message}',
                'level':  level,
                'labels': labels,      # full stream labels for expanded view
                'ts':     ts,          # formatted timestamp for label panel
            })

    return result if result else None

def count_levels(entries: list) -> dict:
    counts = {}
    for e in entries:
        counts[e['level']] = counts.get(e['level'], 0) + 1
    return counts

# Labels shown first in the expanded panel (if present), rest follow alphabetically
_LABEL_PRIORITY = [
    'service_name', 'service_instance_id', 'severity_text', 'detected_level',
    'scope_name', 'TraceId', 'SpanId', 'RequestPath', 'ActionName',
    'deployment_environment', 'service_namespace', 'cluster_id',
]

_EYE_ICON = (
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>'
    '<circle cx="12" cy="12" r="3"/>'
    '</svg>'
)

def _render_labels_panel(labels: dict, ts: str) -> str:
    # Build ordered list: timestamp first, then priority keys, then the rest
    ordered_keys = ['_timestamp']
    seen = {'_timestamp'}
    for k in _LABEL_PRIORITY:
        if k in labels and k not in seen:
            ordered_keys.append(k)
            seen.add(k)
    for k in sorted(labels.keys()):
        if k not in seen:
            ordered_keys.append(k)
            seen.add(k)

    rows = []
    for idx, k in enumerate(ordered_keys):
        alt = ' label-row-alt' if idx % 2 == 1 else ''
        key_display = 'timestamp' if k == '_timestamp' else escape_html(k)

        if k == '_timestamp':
            val_html = ts
        elif k == 'MessageBody':
            raw = str(labels[k])
            preview = escape_html(raw[:60] + ('…' if len(raw) > 60 else ''))
            # Base64-encode so the value is safe inside any HTML attribute
            b64 = base64.b64encode(raw.encode('utf-8')).decode('ascii')
            eye_btn = (
                f'<button class="eye-btn" title="View JSON" '
                f"onclick=\"showJson('{b64}')\">{_EYE_ICON}</button>"
            )
            val_html = f'<span style="opacity:0.7">{preview}</span>{eye_btn}'
        else:
            val_html = escape_html(str(labels[k]))

        rows.append(
            f'<span class="label-key{alt}">{key_display}</span>'
            f'<span class="label-val{alt}" style="display:flex;align-items:center;gap:0.2rem">{val_html}</span>'
        )
    return f'<div class="labels-panel">{"".join(rows)}</div>'

_IFRAME_HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background: #0d0f14; color: #c9d1e8;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem; line-height: 1.75;
    overflow: hidden;
}
.log-container {
    background: #13161e; border: 1px solid #252a38;
    border-radius: 10px; padding: 1rem;
    height: calc(100vh - 4px); overflow-y: auto;
}
.log-container::-webkit-scrollbar { width: 5px; }
.log-container::-webkit-scrollbar-track { background: #0d0f14; }
.log-container::-webkit-scrollbar-thumb { background: #252a38; border-radius: 4px; }

.log-line { display: flex; align-items: flex-start; gap: 0.6rem; padding: 1px 4px; border-radius: 3px; }
.log-line:hover { background: rgba(255,255,255,0.03); }
.line-num { color: #505878; min-width: 3.5rem; text-align: right; user-select: none; font-size: 0.84rem; padding-top: 2px; flex-shrink: 0; }
.line-text { flex: 1; white-space: pre-wrap; word-break: break-all; }

.level-ERROR, .level-CRITICAL, .level-FATAL { color: #f87171; }
.level-WARN, .level-WARNING { color: #fbbf24; }
.level-INFO  { color: #34d399; }
.level-DEBUG { color: #60a5fa; }
.level-TRACE { color: #a78bfa; }
.level-DEFAULT { color: #c9d1e8; }

.highlight { background: rgba(251,191,36,0.3); border-radius: 2px; padding: 0 2px; color: #000 !important; }

/* Expandable rows */
details.log-entry { list-style: none; }
details.log-entry > summary {
    display: flex; align-items: flex-start; gap: 0.6rem;
    padding: 1px 4px; border-radius: 3px;
    cursor: pointer; list-style: none;
}
details.log-entry > summary::-webkit-details-marker { display: none; }
details.log-entry > summary::marker { display: none; }
details.log-entry > summary:hover { background: rgba(255,255,255,0.03); }
details.log-entry[open] > summary { background: rgba(91,138,245,0.07); border-radius: 3px 3px 0 0; }
.expand-arrow {
    color: #505878; font-size: 0.76rem; padding-top: 5px;
    flex-shrink: 0; width: 0.8rem; text-align: center;
    transition: transform 0.15s ease; user-select: none;
}
details.log-entry[open] .expand-arrow { transform: rotate(90deg); color: #5b8af5; }

/* Labels panel */
.labels-panel {
    margin: 0 0 4px 4.8rem;
    background: #1a1e2a; border: 1px solid #252a38; border-top: none;
    border-radius: 0 0 6px 6px; padding: 0.5rem 0.8rem;
    display: grid; grid-template-columns: minmax(160px, max-content) 1fr;
    gap: 0 1.2rem; font-size: 0.89rem;
}
.label-key { color: #a78bfa; font-weight: 600; padding: 2px 0; white-space: nowrap; user-select: text; }
.label-val { color: #c9d1e8; padding: 2px 0; word-break: break-all; user-select: text; display: flex; align-items: center; gap: 0.2rem; }
.label-row-alt .label-key,
.label-row-alt .label-val { background: rgba(255,255,255,0.02); }

/* Eye button */
.eye-btn {
    background: none; border: none; padding: 0 0 0 0.4rem;
    cursor: pointer; color: #505878; line-height: 1;
    vertical-align: middle; flex-shrink: 0;
    transition: color 0.15s ease;
}
.eye-btn:hover { color: #5b8af5; }
.eye-btn svg { display: block; }

/* JSON modal */
dialog#json-modal {
    background: #13161e; color: #c9d1e8;
    border: 1px solid #252a38; border-radius: 10px;
    padding: 0; width: min(72vw, 900px); max-height: 80vh;
    box-shadow: 0 24px 60px rgba(0,0,0,0.6);
    font-family: 'JetBrains Mono', monospace;
}
dialog#json-modal[open] { display: flex; flex-direction: column; }
dialog#json-modal::backdrop { background: rgba(0,0,0,0.55); backdrop-filter: blur(3px); }
.modal-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.7rem 1rem; border-bottom: 1px solid #252a38;
    font-family: 'Syne', sans-serif; font-size: 1.00rem; font-weight: 600; flex-shrink: 0;
}
.modal-title { color: #a78bfa; letter-spacing: 0.02em; }
.modal-close {
    background: none; border: none; color: #505878; font-size: 1rem;
    cursor: pointer; padding: 2px 6px; border-radius: 4px;
    transition: color 0.15s, background 0.15s;
}
.modal-close:hover { color: #c9d1e8; background: #1a1e2a; }
.modal-body { overflow-y: auto; padding: 1rem; flex: 1; }
.modal-body::-webkit-scrollbar { width: 5px; }
.modal-body::-webkit-scrollbar-track { background: #0d0f14; }
.modal-body::-webkit-scrollbar-thumb { background: #252a38; border-radius: 4px; }
pre#json-content { margin: 0; font-size: 0.95rem; line-height: 1.75; white-space: pre-wrap; word-break: break-all; }
.jk { color: #a78bfa; }
.js { color: #34d399; }
.jn { color: #fbbf24; }
.jb { color: #60a5fa; }
.jz { color: #505878; }

/* Truncation notice */
.trunc-notice { color: #505878; padding: 8px 4px; font-size: 0.89rem; }
</style>

<dialog id="json-modal">
  <div class="modal-header">
    <span class="modal-title">MessageBody</span>
    <button class="modal-close" onclick="document.getElementById('json-modal').close()">&#10005;</button>
  </div>
  <div class="modal-body"><pre id="json-content"></pre></div>
</dialog>
<script>
function colorizeJson(raw) {
    var str;
    try { str = JSON.stringify(JSON.parse(raw), null, 2); } catch(e) { return raw; }
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g,
        function(m) {
          if (/^"/.test(m)) {
            return /:$/.test(m)
              ? '<span class="jk">' + m + '</span>'
              : '<span class="js">' + m + '</span>';
          }
          if (/true|false/.test(m)) return '<span class="jb">' + m + '</span>';
          if (/null/.test(m))       return '<span class="jz">' + m + '</span>';
          return '<span class="jn">' + m + '</span>';
        });
}
function showJson(b64) {
    var raw = atob(b64);
    document.getElementById('json-content').innerHTML = colorizeJson(raw);
    document.getElementById('json-modal').showModal();
}
document.getElementById('json-modal').addEventListener('click', function(e) {
    if (e.target === this) this.close();
});
</script>
"""

def render_log_lines(entries: list, search_term: str, max_lines: int = 3000) -> str:
    parts = [_IFRAME_HEAD, '<div class="log-container">']
    for i, e in enumerate(entries):
        if i >= max_lines:
            parts.append(f'<div class="trunc-notice">⚠ Showing first {max_lines:,} matching lines — refine filters to see more.</div>')
            break
        safe = escape_html(e['text'])
        if search_term:
            safe = highlight_text(safe, search_term)

        summary_inner = (
            f'<span class="line-num">{e["num"]}</span>'
            f'<span class="line-text level-{e["level"]}">{safe or "&nbsp;"}</span>'
        )

        if 'labels' in e:
            labels_html = _render_labels_panel(e['labels'], e.get('ts', ''))
            parts.append(
                f'<details class="log-entry">'
                f'<summary>'
                f'<span class="expand-arrow">&#9658;</span>'
                f'{summary_inner}'
                f'</summary>'
                f'{labels_html}'
                f'</details>'
            )
        else:
            parts.append(
                f'<div class="log-line">'
                f'{summary_inner}'
                f'</div>'
            )
    parts.append('</div>')
    return ''.join(parts)

# ── Recent files persistence ──────────────────────────────────────────────────
_RECENT_MAX = 5

def _loglens_dir() -> Path:
    d = Path.home() / '.loglens'
    (d / 'cache').mkdir(parents=True, exist_ok=True)
    return d

def load_recent() -> list:
    try:
        return json.loads((_loglens_dir() / 'recent_files.json').read_text())
    except Exception:
        return []

def save_recent(items: list) -> None:
    (_loglens_dir() / 'recent_files.json').write_text(json.dumps(items))

def add_to_recent(name: str, cached_path: str) -> None:
    items = [i for i in load_recent() if i['name'] != name]
    items.insert(0, {'name': name, 'path': cached_path})
    save_recent(items[:_RECENT_MAX])

def remove_from_recent(cached_path: str) -> None:
    save_recent([i for i in load_recent() if i['path'] != cached_path])

def cache_file(name: str, raw_bytes: bytes) -> str:
    dest = _loglens_dir() / 'cache' / name
    dest.write_bytes(raw_bytes)
    return str(dest)

def parse_content(name: str, content: str) -> list:
    if name.lower().endswith('.json'):
        entries = parse_loki_json(content)
        if entries is None:
            entries = parse_file(content)
    else:
        entries = parse_file(content)
    return entries

# ── Session state ─────────────────────────────────────────────────────────────
if 'files' not in st.session_state:
    st.session_state.files = {}
if 'active_file' not in st.session_state:
    st.session_state.active_file = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="app-title">🔭 LogLens</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Multi-file Log Viewer for Windows</div>', unsafe_allow_html=True)

    st.markdown("**Open Log Files**")
    uploaded = st.file_uploader(
        "Drop files here",
        type=["log", "txt", "out", "err", "json"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded:
        for f in uploaded:
            if f.name not in st.session_state.files:
                raw = f.read()
                content = raw.decode("utf-8", errors="replace")
                st.session_state.files[f.name] = parse_content(f.name, content)
                st.session_state.active_file = f.name
                cached_path = cache_file(f.name, raw)
                add_to_recent(f.name, cached_path)

    # ── Recent files ──────────────────────────────────────────────────────────
    recent = load_recent()
    if recent:
        st.divider()
        st.markdown("**Recent**")
        for item in recent:
            name, path = item['name'], item['path']
            label = name[:24] + ('…' if len(name) > 24 else '')
            if st.button(label, key=f"recent_{path}", help=path, use_container_width=True):
                if name not in st.session_state.files:
                    try:
                        raw = Path(path).read_bytes()
                        content = raw.decode("utf-8", errors="replace")
                        st.session_state.files[name] = parse_content(name, content)
                        st.session_state.active_file = name
                        add_to_recent(name, path)
                    except Exception:
                        remove_from_recent(path)
                        st.toast("Failed to open file", icon="🚨", duration=8)
                else:
                    st.session_state.active_file = name
                st.rerun()

    st.divider()
    st.markdown('<span style="color:var(--muted);font-size:0.74rem;">LogLens v1.0 · Python + Streamlit</span>', unsafe_allow_html=True)

# ── Main view ─────────────────────────────────────────────────────────────────
def render_file_view(name: str):
    entries = st.session_state.files[name]
    counts = count_levels(entries)
    total = len(entries)

    # Stats bar
    stats_html = '<div class="stats-bar">'
    stats_html += f'<div class="stat-pill"><span style="color:var(--muted)">Lines</span>&nbsp;<span class="stat-count">{total:,}</span></div>'
    for lvl in LEVEL_ORDER:
        n = counts.get(lvl, 0)
        if n > 0:
            c = LEVEL_COLORS[lvl]
            stats_html += (
                f'<div class="stat-pill">'
                f'<span class="stat-dot" style="background:{c}"></span>'
                f'<span style="color:{c}">{lvl}</span>&nbsp;'
                f'<span class="stat-count" style="color:{c}">{n:,}</span>'
                f'</div>'
            )
    stats_html += '</div>'
    st.markdown(stats_html, unsafe_allow_html=True)

    # Controls
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        search = st.text_input("Search", placeholder="🔍  Keyword or regex…", key=f"s_{name}", label_visibility="collapsed")
    with col2:
        available_levels = ["ALL LEVELS"] + [l for l in LEVEL_ORDER if counts.get(l, 0) > 0]
        level_filter = st.selectbox("Level", available_levels, key=f"l_{name}", label_visibility="collapsed")
    with col3:
        use_regex = st.checkbox("Regex", key=f"r_{name}")

    # Apply level filter
    filtered = entries
    if level_filter != "ALL LEVELS":
        idx = LEVEL_ORDER.index(level_filter)
        allowed = set(LEVEL_ORDER[:idx + 1])
        filtered = [e for e in filtered if e['level'] in allowed or e['level'] == 'DEFAULT']

    # Apply search filter
    highlight_term = ""
    if search:
        try:
            if use_regex:
                pattern = re.compile(search, re.I)
                filtered = [e for e in filtered if pattern.search(e['text'])]
            else:
                filtered = [e for e in filtered if search.lower() in e['text'].lower()]
                highlight_term = search
        except re.error as ex:
            st.error(f"Invalid regex: {ex}")

    # Match count
    match_count = len(filtered)
    if match_count != total:
        st.markdown(
            f'<div style="font-size:0.92rem;color:var(--muted);margin-bottom:0.35rem;">'
            f'<b style="color:#5b8af5">{match_count:,}</b> / {total:,} lines match</div>',
            unsafe_allow_html=True
        )

    # Render log (components.v1.html allows JS for the modal)
    st.components.v1.html(render_log_lines(filtered, highlight_term), height=600, scrolling=False)

# ── Dispatch ──────────────────────────────────────────────────────────────────
def _tab_icon(name: str) -> str:
    return '⚡' if name.lower().endswith('.json') else '📋'

if not st.session_state.files:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">📂</div>
        <div class="empty-text">Open a log file from the sidebar to get started</div>
        <div style="font-size:0.79rem;color:var(--muted);margin-top:0.3rem">Supports .log · .txt · .out · .err · .json (Loki)</div>
    </div>
    """, unsafe_allow_html=True)
else:
    file_names = list(st.session_state.files.keys())

    # Ensure active_file is valid
    if st.session_state.active_file not in st.session_state.files:
        st.session_state.active_file = file_names[0]
    active = st.session_state.active_file

    # ── Custom tab bar ────────────────────────────────────────────────────────
    st.markdown('<div class="tab-bar">', unsafe_allow_html=True)
    cols = st.columns([6, 1] * len(file_names))
    close_target = None
    for i, name in enumerate(file_names):
        label = f"{_tab_icon(name)} {name[:22]}{'…' if len(name) > 22 else ''}"
        is_active = name == active
        tab_class = "tab-bar-active" if is_active else ""

        with cols[i * 2]:
            st.markdown(f'<div class="{tab_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"tab_{name}", use_container_width=True):
                st.session_state.active_file = name
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with cols[i * 2 + 1]:
            st.markdown('<div class="tab-close">', unsafe_allow_html=True)
            if st.button("✕", key=f"tabclose_{name}"):
                close_target = name
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if close_target:
        del st.session_state.files[close_target]
        if st.session_state.active_file == close_target:
            remaining = [n for n in file_names if n != close_target]
            st.session_state.active_file = remaining[0] if remaining else None
        st.rerun()

    # ── Render active file ────────────────────────────────────────────────────
    render_file_view(active)

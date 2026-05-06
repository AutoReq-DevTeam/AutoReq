"""
app.py — Ana Uygulama Modülü
"""

import os
import streamlit as st
from dotenv import load_dotenv
from ui.state import init_state

load_dotenv()

st.set_page_config(
    page_title="AutoReq",
    layout="wide",
)

init_state()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ================================================================
   AUTOREQ — PREMIUM DARK THEME
   ================================================================ */

:root {
  --bg-base: #0a0e14;
  --bg-elevated: #11161d;
  --bg-card: #161c24;
  --bg-card-hover: #1c2330;
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --text-tertiary: #6e7681;
  --border-subtle: #21262d;
  --border-default: #30363d;
  --accent-primary: #3fb984;
  --accent-primary-hover: #4ac896;
  --accent-glow: rgba(63, 185, 132, 0.15);
  --color-danger: #f85149;
  --color-danger-bg: rgba(248, 81, 73, 0.1);
  --color-warning: #d29922;
  --color-warning-bg: rgba(210, 153, 34, 0.1);
  --color-success: #3fb950;
  --color-info: #58a6ff;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background-color: var(--bg-base) !important;
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-primary) !important;
}

.main .block-container {
    padding-top: 2.5rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 1200px !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
}

h1 {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em !important;
    margin-bottom: 0.25rem !important;
    padding-bottom: 0 !important;
    border-bottom: none !important;
}

h1 + hr, h1 + div hr { display: none !important; }

h2 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    letter-spacing: -0.01em !important;
}

h3 {
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: var(--text-tertiary) !important;
}

[class*="material-icons"],
[class*="material-symbols"],
[data-testid="stIconMaterial"],
span[aria-hidden="true"],
.stSidebarNavItems span,
[data-testid="stSidebarNav"] span,
nav span,
[role="navigation"] span {
    font-family: 'Material Symbols Rounded', 'Material Icons', 'Material Icons Outlined' !important;
}

.stMarkdown p,
.stMarkdown li,
.stMarkdown ol,
.stMarkdown ul,
.stText,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    font-family: 'Inter', sans-serif !important;
}

/* === SIDEBAR === */
section[data-testid="stSidebar"] {
    background-color: var(--bg-elevated) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

section[data-testid="stSidebar"] > div {
    padding: 1rem 0.875rem !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--text-tertiary) !important;
    border: none !important;
    padding: 0 !important;
    margin: 0.75rem 0 0.4rem !important;
}

section[data-testid="stSidebar"] p {
    font-size: 0.82rem !important;
    color: var(--text-secondary) !important;
    margin: 0 !important;
}

section[data-testid="stSidebar"] hr {
    border-top: 1px solid var(--border-subtle) !important;
    margin: 0.6rem 0 !important;
}

[data-testid="stSidebarNav"] a {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.825rem !important;
    font-weight: 400 !important;
    color: var(--text-tertiary) !important;
    padding: 0.45rem 0.875rem !important;
    border-left: 2px solid transparent !important;
    border-radius: 4px !important;
    margin: 1px 0 !important;
    display: block !important;
    transition: color 0.15s ease, background-color 0.15s ease !important;
}

[data-testid="stSidebarNav"] a:hover {
    color: var(--text-primary) !important;
    background-color: var(--bg-card) !important;
    border-left-color: var(--border-default) !important;
    text-decoration: none !important;
}

[data-testid="stSidebarNav"] [aria-current="page"] {
    color: var(--accent-primary) !important;
    background-color: var(--accent-glow) !important;
    border-left-color: var(--accent-primary) !important;
    font-weight: 500 !important;
}

/* Sidebar metric buttons scoped */
#ar-metric-btns .stButton > button {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 5px !important;
    padding: 0.45rem 0.15rem !important;
    width: 100% !important;
    text-align: center !important;
    color: var(--text-secondary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 400 !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    line-height: 1.3 !important;
    box-shadow: none !important;
}

#ar-metric-btns .stButton > button:hover {
    background-color: var(--bg-card-hover) !important;
    border-color: var(--border-default) !important;
    color: var(--text-primary) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* === BUTTONS === */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0 !important;
    background-color: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-default) !important;
    padding: 0.55rem 1.25rem !important;
    border-radius: 6px !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
}

.stButton > button:hover {
    border-color: var(--accent-primary) !important;
    color: var(--accent-primary) !important;
    background-color: var(--accent-glow) !important;
    box-shadow: none !important;
}

.stButton > button:active {
    transform: scale(0.98) !important;
}

.stButton > button:focus:not(:active) {
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
    border-color: var(--accent-primary) !important;
    outline: none !important;
}

.stButton > button:focus-visible {
    outline: 2px solid var(--accent-primary) !important;
    outline-offset: 2px !important;
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background-color: var(--accent-primary) !important;
    color: #040d08 !important;
    border-color: var(--accent-primary) !important;
    font-weight: 600 !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background-color: var(--accent-primary-hover) !important;
    border-color: var(--accent-primary-hover) !important;
    color: #040d08 !important;
}

.stDownloadButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.825rem !important;
    font-weight: 500 !important;
    background-color: var(--bg-card) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-subtle) !important;
    padding: 0.65rem 1rem !important;
    border-radius: 6px !important;
    width: 100% !important;
    text-align: left !important;
    transition: all 0.15s ease !important;
}

.stDownloadButton > button:hover {
    border-color: var(--accent-primary) !important;
    color: var(--accent-primary) !important;
    background-color: var(--accent-glow) !important;
}

/* === TEXT AREAS === */
.stTextArea textarea,
.stTextInput input {
    background-color: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-subtle) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    line-height: 1.7 !important;
    border-radius: 6px !important;
    caret-color: var(--accent-primary) !important;
    box-shadow: none !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
    outline: none !important;
}

.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
    color: var(--text-tertiary) !important;
    opacity: 0.5 !important;
}

.stTextArea textarea:disabled,
.stTextInput input:disabled {
    opacity: 0.4 !important;
}

.stTextArea label, .stTextInput label,
.stSelectbox label, .stFileUploader label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}

/* === SELECT BOX === */
.stSelectbox > div > div,
.stSelectbox [data-baseweb="select"] > div {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    border-radius: 6px !important;
    box-shadow: none !important;
}

.stSelectbox [data-baseweb="select"] > div:hover {
    border-color: var(--border-default) !important;
}

[data-baseweb="popover"] [data-baseweb="menu"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 6px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
}

[data-baseweb="popover"] [role="option"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    color: var(--text-secondary) !important;
}

[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [aria-selected="true"] {
    background-color: var(--accent-glow) !important;
    color: var(--accent-primary) !important;
}

/* === FILE UPLOADER === */
.stFileUploader {
    background-color: var(--bg-elevated) !important;
    border: 1px dashed var(--border-default) !important;
    border-radius: 6px !important;
}

.stFileUploader section {
    background-color: transparent !important;
    border: none !important;
}

.stFileUploader button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    color: var(--text-tertiary) !important;
    border: 1px solid var(--border-default) !important;
    background-color: transparent !important;
    border-radius: 5px !important;
    transition: color 0.15s ease, border-color 0.15s ease !important;
}

.stFileUploader button span,
.stButton > button span,
.stDownloadButton > button span {
    font-family: 'Material Symbols Rounded', 'Material Icons', 'Material Icons Outlined' !important;
}

.stFileUploader button:hover {
    color: var(--accent-primary) !important;
    border-color: var(--accent-primary) !important;
}

/* === TABS === */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 1px solid var(--border-subtle) !important;
    gap: 0 !important;
    padding: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: var(--text-tertiary) !important;
    background-color: transparent !important;
    padding: 0.75rem 1.5rem !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    transition: color 0.15s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-secondary) !important;
    background-color: transparent !important;
}

.stTabs [aria-selected="true"] {
    color: var(--accent-primary) !important;
    border-bottom-color: var(--accent-primary) !important;
    background-color: transparent !important;
}

.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.75rem !important;
    background-color: transparent !important;
}

/* === METRICS === */
div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: var(--accent-primary) !important;
    line-height: 1.1 !important;
}

div[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: var(--text-tertiary) !important;
}

/* === ALERTS === */
div[data-testid="stAlert"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    padding: 0.75rem 1rem !important;
}

div[data-testid="stAlert"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    color: var(--text-secondary) !important;
}

div[data-testid="stAlert"] svg { opacity: 0.55 !important; }

.stInfo    { border-left: 3px solid var(--color-info) !important; }
.stWarning { border-left: 3px solid var(--color-warning) !important; }
.stError   { border-left: 3px solid var(--color-danger) !important; }
.stSuccess { border-left: 3px solid var(--color-success) !important; }

/* === EXPANDERS === */
[data-testid="stExpander"] summary,
.streamlit-expanderHeader {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.825rem !important;
    font-weight: 500 !important;
    color: var(--text-tertiary) !important;
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 6px !important;
    padding: 0.6rem 0.875rem !important;
    transition: color 0.15s ease, border-color 0.15s ease !important;
}

[data-testid="stExpander"] summary:hover,
.streamlit-expanderHeader:hover {
    color: var(--text-secondary) !important;
    border-color: var(--border-default) !important;
}

[data-testid="stExpander"] details[open] summary {
    border-radius: 6px 6px 0 0 !important;
    border-bottom: none !important;
    color: var(--text-secondary) !important;
}

.streamlit-expanderContent,
[data-testid="stExpanderDetails"] {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-top: none !important;
    border-radius: 0 0 6px 6px !important;
    padding: 0.875rem 1rem !important;
}

/* === DIVIDERS === */
hr {
    border: none !important;
    border-top: 1px solid var(--border-subtle) !important;
    margin: 0.75rem 0 !important;
}

/* === CHECKBOXES === */
.stCheckbox label span {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
    color: var(--text-secondary) !important;
}

.stCheckbox [data-baseweb="checkbox"] span:first-child {
    border-color: var(--border-default) !important;
    border-radius: 3px !important;
    background-color: transparent !important;
}

/* === STATUS === */
[data-testid="stStatus"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 6px !important;
}

[data-testid="stStatus"] summary {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    color: var(--text-secondary) !important;
}

/* === PROGRESS BAR === */
.stProgress > div > div > div {
    background-color: var(--accent-primary) !important;
    border-radius: 4px !important;
    transition: width 0.3s ease !important;
}
.stProgress > div > div {
    background-color: var(--border-subtle) !important;
    border-radius: 4px !important;
}

/* === SPINNER === */
.stSpinner > div { border-top-color: var(--accent-primary) !important; }

/* === TOAST === */
[data-testid="toastContainer"] > div {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 6px !important;
    color: var(--text-secondary) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5) !important;
}

/* === CODE === */
code {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: var(--bg-card) !important;
    color: var(--accent-primary) !important;
    padding: 0.15em 0.4em !important;
    border-radius: 3px !important;
    font-size: 0.85em !important;
}

/* === SCROLLBAR === */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-default); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-default); filter: brightness(1.3); }

/* ================================================================
   COMPONENT CLASSES
   ================================================================ */

/* Step indicator */
.ar-stepper {
    display: flex;
    align-items: center;
    margin-bottom: 1.75rem;
    user-select: none;
}

.ar-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.3rem;
    flex-shrink: 0;
}

.ar-step-dot {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.6rem;
    font-weight: 700;
    transition: all 0.2s ease;
    font-family: 'Inter', sans-serif;
}

.ar-step--complete .ar-step-dot {
    background-color: var(--accent-primary);
    color: #040d08;
}

.ar-step--active .ar-step-dot {
    background-color: var(--accent-primary);
    color: #040d08;
    box-shadow: 0 0 14px var(--accent-glow);
}

.ar-step--future .ar-step-dot {
    background-color: transparent;
    border: 2px solid var(--border-default);
}

.ar-step-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 500;
    white-space: nowrap;
}

.ar-step--complete .ar-step-label { color: var(--accent-primary); }
.ar-step--active .ar-step-label   { color: var(--accent-primary); font-weight: 600; }
.ar-step--future .ar-step-label   { color: var(--text-tertiary); }

.ar-step-line {
    flex: 1;
    height: 2px;
    background-color: var(--accent-primary);
    margin: 0 0.5rem;
    margin-bottom: 1.15rem;
    transition: background-color 0.2s ease;
}

.ar-step-line--future {
    background-color: var(--border-default);
}

/* Page title */
.ar-page-title {
    margin-bottom: 2rem;
}

.ar-page-title h1 {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.4rem !important;
}

.ar-title-bar {
    width: 36px;
    height: 3px;
    background-color: var(--accent-primary);
    border-radius: 2px;
    margin-bottom: 1.5rem;
}

/* Section labels */
.ar-section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-tertiary);
    margin-bottom: 0.75rem;
    margin-top: 0.25rem;
}

/* Requirement card */
.ar-req-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--accent-primary);
    border-radius: 6px;
    padding: 1rem 1.125rem;
    margin-bottom: 0.625rem;
    transition: all 0.15s ease;
}

.ar-req-card:hover {
    background-color: var(--bg-card-hover);
    border-color: var(--border-default);
    border-left-color: var(--accent-primary);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

.ar-req-card--nfr {
    border-left-color: var(--color-info);
}

.ar-req-card--nfr:hover {
    border-left-color: var(--color-info);
}

/* Badges */
.ar-badge {
    display: inline-flex;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    letter-spacing: 0.05em;
    vertical-align: middle;
    margin-right: 0.6rem;
}

.ar-badge--func   { background-color: rgba(63, 185, 132, 0.12); color: var(--accent-primary); }
.ar-badge--nfr    { background-color: rgba(88, 166, 255, 0.12);  color: var(--color-info); }
.ar-badge--high   { background-color: var(--color-danger-bg);    color: var(--color-danger); }
.ar-badge--medium { background-color: var(--color-warning-bg);   color: var(--color-warning); }
.ar-badge--low    { background-color: rgba(110, 118, 129, 0.15); color: var(--text-tertiary); }

/* Requirement ID */
.ar-req-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-tertiary);
    vertical-align: middle;
}

/* Requirement text */
.ar-req-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.7;
    margin-top: 0.55rem;
}

/* Conflict card — high severity gets a glow */
.ar-conflict-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--color-danger);
    border-radius: 6px;
    padding: 0.875rem 1.125rem 0.625rem;
    margin-bottom: 0.625rem;
    box-shadow: 0 0 24px var(--color-danger-bg);
    transition: all 0.15s ease;
}

.ar-conflict-card:hover {
    background-color: var(--bg-card-hover);
    border-color: var(--border-default);
    border-left-color: var(--color-danger);
    transform: translateY(-1px);
}

.ar-conflict-card--medium {
    border-left-color: var(--color-warning);
    box-shadow: 0 0 24px var(--color-warning-bg);
}
.ar-conflict-card--medium:hover { border-left-color: var(--color-warning); }

.ar-conflict-card--low {
    border-left-color: var(--border-default);
    box-shadow: none;
}
.ar-conflict-card--low:hover { border-left-color: var(--border-default); }

.ar-conflict-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-primary);
    vertical-align: middle;
}

/* Requirement ID links */
.ar-req-link {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-tertiary);
    margin-right: 0.4rem;
    margin-bottom: 0.3rem;
    background-color: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 3px;
    padding: 0.1rem 0.4rem;
    text-decoration: none !important;
    transition: all 0.15s ease;
}

.ar-req-link:hover {
    color: var(--accent-primary) !important;
    border-color: rgba(63, 185, 132, 0.35) !important;
    background-color: var(--accent-glow) !important;
}

/* Gap card */
.ar-gap-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--color-warning);
    border-radius: 6px;
    padding: 0.875rem 1.125rem 0.625rem;
    margin-bottom: 0.625rem;
    transition: all 0.15s ease;
}

.ar-gap-card:hover {
    background-color: var(--bg-card-hover);
    border-color: var(--border-default);
    border-left-color: var(--color-warning);
    transform: translateY(-1px);
}

.ar-gap-card--low { border-left-color: var(--border-default); }
.ar-gap-card--low:hover { border-left-color: var(--border-default); }

.ar-gap-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-primary);
    vertical-align: middle;
}

.ar-gap-area {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 0.35rem;
    line-height: 1.5;
}

/* Improvement diff */
.ar-diff-wrap {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    margin-bottom: 0.875rem;
    overflow: hidden;
    transition: all 0.15s ease;
}

.ar-diff-wrap:hover {
    border-color: var(--border-default);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.ar-diff-header {
    display: flex;
    border-bottom: 1px solid var(--border-subtle);
}

.ar-diff-col {
    flex: 1;
    padding: 0.5rem 1rem;
}

.ar-diff-col:first-child {
    border-right: 1px solid var(--border-subtle);
}

.ar-diff-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-tertiary);
    margin-bottom: 0;
}

.ar-diff-body { display: flex; }

.ar-diff-before {
    flex: 1;
    border-right: 1px solid var(--border-subtle);
    background-color: rgba(248, 81, 73, 0.04);
    padding: 0.75rem 1rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    line-height: 1.7;
    color: var(--text-secondary);
    border-left: 3px solid var(--color-danger);
}

.ar-diff-after {
    flex: 1;
    background-color: rgba(63, 185, 132, 0.04);
    padding: 0.75rem 1rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    line-height: 1.7;
    color: var(--text-primary);
    border-left: 3px solid var(--accent-primary);
}

/* Sidebar brand */
.ar-sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border-subtle);
}

.ar-sidebar-brand-name {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}

.ar-sidebar-brand-dot {
    width: 6px;
    height: 6px;
    background-color: var(--accent-primary);
    border-radius: 50%;
    flex-shrink: 0;
}

.ar-sidebar-section { margin-bottom: 0.75rem; }

.ar-sidebar-section-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-tertiary);
    margin-bottom: 0.4rem;
}

.ar-stat-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.35rem 0;
    border-bottom: 1px solid var(--border-subtle);
}

.ar-stat-row:last-child { border-bottom: none; }

.ar-stat-key {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    color: var(--text-tertiary);
}

.ar-stat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-secondary);
}

.ar-demo-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--accent-primary);
    background-color: rgba(63, 185, 132, 0.08);
    border: 1px solid rgba(63, 185, 132, 0.25);
    border-radius: 4px;
    padding: 0.3rem 0.6rem;
    margin-top: 0.4rem;
}

/* Empty state */
.ar-empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3.5rem 2rem;
    text-align: center;
}

.ar-empty-state-icon {
    font-size: 2.25rem;
    margin-bottom: 1rem;
    opacity: 0.35;
    line-height: 1;
}

.ar-empty-state-title {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
}

.ar-empty-state-body {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: var(--text-tertiary);
    line-height: 1.6;
    max-width: 360px;
    margin-bottom: 1.25rem;
}

/* Export file card */
.ar-export-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    transition: all 0.15s ease;
}

.ar-export-card:hover {
    background-color: var(--bg-card-hover);
    border-color: var(--border-default);
}

.ar-export-card-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-tertiary);
    margin-bottom: 0.75rem;
}

.ar-export-meta {
    display: flex;
    gap: 1.5rem;
    margin-top: 0.75rem;
    flex-wrap: wrap;
}

.ar-export-meta-item {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}

.ar-export-meta-key {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-tertiary);
}

.ar-export-meta-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-secondary);
}

/* Conflict side-by-side detail */
.ar-conflict-detail {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
    margin-bottom: 0.875rem;
}

.ar-conflict-detail-pane {
    background-color: var(--bg-base);
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    padding: 0.875rem;
}

.ar-conflict-detail-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--color-danger);
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.ar-conflict-detail-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

.ar-conflict-reason {
    background-color: var(--bg-base);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--color-danger);
    border-radius: 6px;
    padding: 0.875rem 1rem;
}

.ar-conflict-reason-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-tertiary);
    margin-bottom: 0.5rem;
}

.ar-conflict-reason-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

# — Sidebar
session_tokens = int(st.session_state.get("total_tokens_used", 0))
session_cost = float(st.session_state.get("total_cost_usd", 0.0))
req_count = st.session_state.get("req_count", 0)
conflict_count = st.session_state.get("conflict_count", 0)
gap_count = st.session_state.get("gap_count", 0)

if os.getenv("OPENROUTER_API_KEY"):
    api_label, api_color = "Aktif — OpenRouter", "var(--color-success)"
elif os.getenv("DEEPSEEK_API_KEY"):
    api_label, api_color = "Aktif — DeepSeek", "var(--color-success)"
elif os.getenv("GEMINI_API_KEY"):
    api_label, api_color = "Aktif — Gemini", "var(--color-success)"
else:
    api_label, api_color = "Tanımsız", "var(--color-danger)"

st.sidebar.markdown(f"""
<div class="ar-sidebar-brand">
    <div class="ar-sidebar-brand-dot"></div>
    <span class="ar-sidebar-brand-name">AutoReq</span>
</div>

<div class="ar-sidebar-section">
    <div class="ar-sidebar-section-title">Sistem Durumu</div>
    <div class="ar-stat-row">
        <span class="ar-stat-key">API</span>
        <span class="ar-stat-val" style="color:{api_color}">{api_label}</span>
    </div>
    <div class="ar-stat-row">
        <span class="ar-stat-key">Maliyet</span>
        <span class="ar-stat-val">${session_cost:.4f}</span>
    </div>
    <div class="ar-stat-row">
        <span class="ar-stat-key">Token</span>
        <span class="ar-stat-val">{session_tokens:,}</span>
    </div>
</div>

<div class="ar-sidebar-section" style="margin-top:0.75rem;">
    <div class="ar-sidebar-section-title">Analiz Özeti</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div id="ar-metric-btns">', unsafe_allow_html=True)
_mc1, _mc2, _mc3 = st.sidebar.columns(3)
with _mc1:
    _req_click = st.button(
        f"{req_count}\nGerek.",
        key="sb_req_metric",
        help="Gereksinimler sayfasına git",
        use_container_width=True,
    )
with _mc2:
    _conf_click = st.button(
        f"{conflict_count}\nÇelişki",
        key="sb_conflict_metric",
        help="Çelişkiler bölümüne git",
        use_container_width=True,
    )
with _mc3:
    _gap_click = st.button(
        f"{gap_count}\nEksiklik",
        key="sb_gap_metric",
        help="Eksiklikler bölümüne git",
        use_container_width=True,
    )
st.sidebar.markdown('</div>', unsafe_allow_html=True)

if _conf_click:
    st.session_state.result_scroll_to = "conflicts"
    st.switch_page("ui/pages/03_results.py")
elif _gap_click:
    st.session_state.result_scroll_to = "gaps"
    st.switch_page("ui/pages/03_results.py")
elif _req_click:
    st.session_state.result_scroll_to = "requirements"
    st.switch_page("ui/pages/03_results.py")

st.sidebar.markdown('<div style="border-top:1px solid var(--border-subtle);margin:0.875rem 0 0.625rem;"></div>', unsafe_allow_html=True)

demo_mode = st.sidebar.checkbox(
    "Demo Modu",
    value=st.session_state.get("demo_mode", False),
    help="Demo senaryolarını gösterir ve sunum dostu arayüzü etkinleştirir.",
    key="demo_mode_toggle",
)
st.session_state.demo_mode = demo_mode
if demo_mode:
    st.sidebar.markdown(
        '<div class="ar-demo-badge">'
        '<div style="width:5px;height:5px;background:var(--accent-primary);border-radius:50%;"></div>'
        ' Demo Modu Aktif'
        '</div>',
        unsafe_allow_html=True,
    )

pages = {
    "AutoReq": [
        st.Page("ui/pages/01_input.py", title="Girdi"),
        st.Page("ui/pages/02_analysis.py", title="Analiz"),
        st.Page("ui/pages/03_results.py", title="Sonuçlar"),
        st.Page("ui/pages/04_export.py", title="Dışa Aktarım"),
    ]
}

pg = st.navigation(pages)
pg.run()

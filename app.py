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
   AUTOREQ — PROFESSIONAL DARK THEME
   Kurumsal, temiz, herkesin gözüne hitap eden tasarım.
   ================================================================ */

*, *::before, *::after { box-sizing: border-box; }

/* === TEMEL === */
html, body, .stApp {
    background-color: #0d0d0d !important;
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #e0e0e0 !important;
}

/* === İÇERİK ALANI === */
.main .block-container {
    padding-top: 2.5rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 1120px !important;
}

/* === TİPOGRAFİ === */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: #f0f0f0 !important;
}

h1 {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #ffffff !important;
    letter-spacing: -0.02em !important;
    margin-bottom: 0.25rem !important;
    padding-bottom: 0 !important;
    border-bottom: none !important;
}

/* Yeşil vurgu çizgisi — başlığın altında ince bir şerit */
h1 + hr, h1 + div hr { display: none !important; }

h2 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #c8c8c8 !important;
    letter-spacing: -0.01em !important;
}

h3 {
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: #a0a0a0 !important;
}

/* Material Icons fontunu her koşulda koru */
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

/* Sadece içerik alanı elementlerine Inter uygula */
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
    background-color: #0a0a0a !important;
    border-right: 1px solid #1e1e1e !important;
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
    color: #555555 !important;
    border: none !important;
    padding: 0 !important;
    margin: 0.75rem 0 0.4rem !important;
}

section[data-testid="stSidebar"] p {
    font-size: 0.82rem !important;
    color: #888888 !important;
    margin: 0 !important;
}

section[data-testid="stSidebar"] hr {
    border-top: 1px solid #1a1a1a !important;
    margin: 0.6rem 0 !important;
}

/* Sidebar navigasyon linkleri */
[data-testid="stSidebarNav"] a {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.825rem !important;
    font-weight: 400 !important;
    color: #666666 !important;
    padding: 0.45rem 0.875rem !important;
    border-left: 2px solid transparent !important;
    border-radius: 4px !important;
    margin: 1px 0 !important;
    display: block !important;
    transition: color 0.15s, background-color 0.15s !important;
}

[data-testid="stSidebarNav"] a:hover {
    color: #d0d0d0 !important;
    background-color: #161616 !important;
    border-left-color: #333333 !important;
    text-decoration: none !important;
}

[data-testid="stSidebarNav"] [aria-current="page"] {
    color: #00ff99 !important;
    background-color: rgba(0, 255, 153, 0.07) !important;
    border-left-color: #00ff99 !important;
    font-weight: 500 !important;
}

/* === BUTONLAR === */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0 !important;
    background-color: transparent !important;
    color: #888888 !important;
    border: 1px solid #2a2a2a !important;
    padding: 0.55rem 1.25rem !important;
    border-radius: 6px !important;
    transition: border-color 0.15s, color 0.15s, background-color 0.15s !important;
    box-shadow: none !important;
}

.stButton > button:hover {
    border-color: #00ff99 !important;
    color: #00ff99 !important;
    background-color: rgba(0, 255, 153, 0.05) !important;
    box-shadow: none !important;
}

.stButton > button:focus:not(:active) {
    box-shadow: 0 0 0 3px rgba(0, 255, 153, 0.15) !important;
    border-color: #00ff99 !important;
    outline: none !important;
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background-color: #00ff99 !important;
    color: #040d08 !important;
    border-color: #00ff99 !important;
    font-weight: 600 !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background-color: #00e88a !important;
    border-color: #00e88a !important;
    color: #040d08 !important;
}

/* İndirme butonları */
.stDownloadButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.825rem !important;
    font-weight: 500 !important;
    background-color: #141414 !important;
    color: #888888 !important;
    border: 1px solid #1e1e1e !important;
    padding: 0.65rem 1rem !important;
    border-radius: 6px !important;
    width: 100% !important;
    text-align: left !important;
    transition: border-color 0.15s, color 0.15s !important;
}

.stDownloadButton > button:hover {
    border-color: #00ff99 !important;
    color: #00ff99 !important;
    background-color: rgba(0, 255, 153, 0.05) !important;
}

/* === METIN ALANLARI === */
.stTextArea textarea,
.stTextInput input {
    background-color: #111111 !important;
    color: #e0e0e0 !important;
    border: 1px solid #1e1e1e !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    line-height: 1.7 !important;
    border-radius: 6px !important;
    caret-color: #00ff99 !important;
    box-shadow: none !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}

.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: #00ff99 !important;
    box-shadow: 0 0 0 3px rgba(0, 255, 153, 0.1) !important;
    outline: none !important;
}

.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
    color: #3a3a3a !important;
}

.stTextArea textarea:disabled,
.stTextInput input:disabled {
    opacity: 0.4 !important;
}

/* Widget etiketleri */
.stTextArea label, .stTextInput label,
.stSelectbox label, .stFileUploader label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #777777 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}

/* === SEÇİM KUTUSU === */
.stSelectbox > div > div,
.stSelectbox [data-baseweb="select"] > div {
    background-color: #111111 !important;
    border: 1px solid #1e1e1e !important;
    color: #e0e0e0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    border-radius: 6px !important;
    box-shadow: none !important;
}

.stSelectbox [data-baseweb="select"] > div:hover {
    border-color: #333333 !important;
}

[data-baseweb="popover"] [data-baseweb="menu"] {
    background-color: #161616 !important;
    border: 1px solid #222222 !important;
    border-radius: 6px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
}

[data-baseweb="popover"] [role="option"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    color: #888888 !important;
}

[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [aria-selected="true"] {
    background-color: rgba(0, 255, 153, 0.08) !important;
    color: #00ff99 !important;
}

/* === DOSYA YÜKLEYİCİ === */
.stFileUploader {
    background-color: #111111 !important;
    border: 1px dashed #252525 !important;
    border-radius: 6px !important;
}

.stFileUploader section {
    background-color: transparent !important;
    border: none !important;
}

.stFileUploader button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    color: #666666 !important;
    border: 1px solid #2a2a2a !important;
    background-color: transparent !important;
    border-radius: 5px !important;
    transition: color 0.15s, border-color 0.15s !important;
}

/* File uploader ve buton içindeki Material ikon span'larını koru */
.stFileUploader button span,
.stButton > button span,
.stDownloadButton > button span {
    font-family: 'Material Symbols Rounded', 'Material Icons', 'Material Icons Outlined' !important;
}

.stFileUploader button:hover {
    color: #00ff99 !important;
    border-color: #00ff99 !important;
}

/* === SEKMELER === */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 1px solid #1e1e1e !important;
    gap: 0 !important;
    padding: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #555555 !important;
    background-color: transparent !important;
    padding: 0.75rem 1.5rem !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    transition: color 0.15s !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #aaaaaa !important;
    background-color: transparent !important;
}

.stTabs [aria-selected="true"] {
    color: #00ff99 !important;
    border-bottom-color: #00ff99 !important;
    background-color: transparent !important;
}

.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.75rem !important;
    background-color: transparent !important;
}

/* === METRİKLER === */
div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: #00ff99 !important;
    line-height: 1.1 !important;
}

div[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #555555 !important;
}

/* === UYARI / BİLGİ KUTULARI === */
div[data-testid="stAlert"] {
    background-color: #111111 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    padding: 0.75rem 1rem !important;
}

div[data-testid="stAlert"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    color: #c8c8c8 !important;
}

div[data-testid="stAlert"] svg { opacity: 0.55 !important; }

.stInfo  { border-left: 3px solid #4d90ff !important; }
.stWarning { border-left: 3px solid #f5a623 !important; }
.stError   { border-left: 3px solid #ff5252 !important; }
.stSuccess { border-left: 3px solid #00ff99 !important; }

/* === GENİŞLETİCİLER === */
[data-testid="stExpander"] summary,
.streamlit-expanderHeader {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.825rem !important;
    font-weight: 500 !important;
    color: #666666 !important;
    background-color: #141414 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 6px !important;
    padding: 0.6rem 0.875rem !important;
    transition: color 0.15s, border-color 0.15s !important;
}

[data-testid="stExpander"] summary:hover,
.streamlit-expanderHeader:hover {
    color: #aaaaaa !important;
    border-color: #2a2a2a !important;
}

[data-testid="stExpander"] details[open] summary {
    border-radius: 6px 6px 0 0 !important;
    border-bottom: none !important;
    color: #aaaaaa !important;
}

.streamlit-expanderContent,
[data-testid="stExpanderDetails"] {
    background-color: #0f0f0f !important;
    border: 1px solid #1e1e1e !important;
    border-top: none !important;
    border-radius: 0 0 6px 6px !important;
    padding: 0.875rem 1rem !important;
}

/* === AYRAÇLAR === */
hr {
    border: none !important;
    border-top: 1px solid #181818 !important;
    margin: 0.75rem 0 !important;
}

/* === ONAY KUTULARI === */
.stCheckbox label span {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
    color: #888888 !important;
}

.stCheckbox [data-baseweb="checkbox"] span:first-child {
    border-color: #2a2a2a !important;
    border-radius: 3px !important;
    background-color: transparent !important;
}

/* === DURUM WİDGETİ === */
[data-testid="stStatus"] {
    background-color: #111111 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 6px !important;
}

[data-testid="stStatus"] summary {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    color: #777777 !important;
}

/* === DÖNDÜRÜCÜ === */
.stSpinner > div { border-top-color: #00ff99 !important; }

/* === TOAST === */
[data-testid="toastContainer"] > div {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    background-color: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 6px !important;
    color: #c8c8c8 !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5) !important;
}

/* === KOD === */
code {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: #1a1a1a !important;
    color: #00ff99 !important;
    padding: 0.15em 0.4em !important;
    border-radius: 3px !important;
    font-size: 0.85em !important;
}

/* === KAYDIRMA ÇUBUĞU === */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0d0d0d; }
::-webkit-scrollbar-thumb { background: #252525; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #333333; }

/* ================================================================
   BİLEŞEN SINIFLARI (components.py tarafından kullanılır)
   ================================================================ */

/* Sayfa başlık vurgu çizgisi */
.ar-page-title {
    margin-bottom: 2rem;
}

.ar-page-title h1 {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #ffffff !important;
    margin-bottom: 0.4rem !important;
}

.ar-title-bar {
    width: 36px;
    height: 3px;
    background-color: #00ff99;
    border-radius: 2px;
    margin-bottom: 1.5rem;
}

/* Bölüm başlıkları */
.ar-section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #555555;
    margin-bottom: 0.75rem;
    margin-top: 0.25rem;
}

/* Gereksinim kartı */
.ar-req-card {
    background-color: #111111;
    border: 1px solid #1e1e1e;
    border-left: 3px solid #00ff99;
    border-radius: 6px;
    padding: 1rem 1.125rem;
    margin-bottom: 0.625rem;
    transition: border-color 0.15s;
}

.ar-req-card:hover {
    border-color: #2a2a2a;
    border-left-color: #00ff99;
}

.ar-req-card--nfr {
    border-left-color: #4d90ff;
}

.ar-req-card--nfr:hover {
    border-left-color: #4d90ff;
}

/* Rozet */
.ar-badge {
    display: inline-flex;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    letter-spacing: 0.05em;
    vertical-align: middle;
    margin-right: 0.6rem;
}

.ar-badge--func {
    background-color: rgba(0, 255, 153, 0.1);
    color: #00ff99;
}

.ar-badge--nfr {
    background-color: rgba(77, 144, 255, 0.1);
    color: #4d90ff;
}

.ar-badge--high {
    background-color: rgba(255, 82, 82, 0.12);
    color: #ff5252;
}

.ar-badge--medium {
    background-color: rgba(245, 166, 35, 0.12);
    color: #f5a623;
}

.ar-badge--low {
    background-color: rgba(100, 100, 100, 0.15);
    color: #777777;
}

/* Kimlik etiketi */
.ar-req-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #555555;
    vertical-align: middle;
}

/* Gereksinim metni */
.ar-req-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: #c8c8c8;
    line-height: 1.7;
    margin-top: 0.55rem;
}

/* Çelişki kartı */
.ar-conflict-card {
    background-color: #111111;
    border: 1px solid #1e1e1e;
    border-left: 3px solid #ff5252;
    border-radius: 6px;
    padding: 0.875rem 1.125rem 0.625rem;
    margin-bottom: 0.625rem;
}

.ar-conflict-card--medium { border-left-color: #f5a623; }
.ar-conflict-card--low    { border-left-color: #3a3a3a; }

.ar-conflict-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    color: #d0d0d0;
    vertical-align: middle;
}

/* Gereksinim ID linkleri */
.ar-req-link {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #555555;
    margin-right: 0.4rem;
    margin-bottom: 0.3rem;
    background-color: #1a1a1a;
    border: 1px solid #252525;
    border-radius: 3px;
    padding: 0.1rem 0.4rem;
    text-decoration: none !important;
    transition: color 0.15s, border-color 0.15s;
}

.ar-req-link:hover {
    color: #00ff99 !important;
    border-color: rgba(0, 255, 153, 0.3) !important;
    background-color: rgba(0, 255, 153, 0.05) !important;
}

/* Eksiklik kartı */
.ar-gap-card {
    background-color: #111111;
    border: 1px solid #1e1e1e;
    border-left: 3px solid #f5a623;
    border-radius: 6px;
    padding: 0.875rem 1.125rem 0.625rem;
    margin-bottom: 0.625rem;
}

.ar-gap-card--low { border-left-color: #3a3a3a; }

.ar-gap-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    color: #d0d0d0;
    vertical-align: middle;
}

.ar-gap-area {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: #777777;
    margin-top: 0.35rem;
    line-height: 1.5;
}

/* İyileştirme farkı */
.ar-diff-wrap {
    background-color: #111111;
    border: 1px solid #1e1e1e;
    border-radius: 6px;
    margin-bottom: 0.875rem;
    overflow: hidden;
}

.ar-diff-header {
    display: flex;
    border-bottom: 1px solid #1e1e1e;
}

.ar-diff-col {
    flex: 1;
    padding: 0.5rem 1rem;
}

.ar-diff-col:first-child {
    border-right: 1px solid #1e1e1e;
}

.ar-diff-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #555555;
    margin-bottom: 0;
}

.ar-diff-body {
    display: flex;
}

.ar-diff-before {
    flex: 1;
    border-right: 1px solid #1e1e1e;
    background-color: rgba(255, 82, 82, 0.04);
    padding: 0.75rem 1rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    line-height: 1.7;
    color: #aaaaaa;
    border-left: 3px solid #ff5252;
}

.ar-diff-after {
    flex: 1;
    background-color: rgba(0, 255, 153, 0.04);
    padding: 0.75rem 1rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    line-height: 1.7;
    color: #c8c8c8;
    border-left: 3px solid #00ff99;
}

/* Sidebar bileşenleri */
.ar-sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #1a1a1a;
}

.ar-sidebar-brand-name {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: #e0e0e0;
    letter-spacing: -0.01em;
}

.ar-sidebar-brand-dot {
    width: 6px;
    height: 6px;
    background-color: #00ff99;
    border-radius: 50%;
    flex-shrink: 0;
}

.ar-sidebar-section {
    margin-bottom: 0.75rem;
}

.ar-sidebar-section-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #444444;
    margin-bottom: 0.4rem;
}

.ar-stat-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.35rem 0;
    border-bottom: 1px solid #141414;
}

.ar-stat-row:last-child { border-bottom: none; }

.ar-stat-key {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    color: #666666;
}

.ar-stat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #aaaaaa;
}

.ar-metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.4rem;
    margin-top: 0.4rem;
}

.ar-metric-box {
    background-color: #111111;
    border: 1px solid #1a1a1a;
    border-radius: 5px;
    padding: 0.5rem 0.4rem;
    text-align: center;
}

.ar-metric-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.25rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.2rem;
}

.ar-metric-key {
    font-family: 'Inter', sans-serif;
    font-size: 0.58rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #444444;
}

.ar-demo-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    color: #00ff99;
    background-color: rgba(0, 255, 153, 0.08);
    border: 1px solid rgba(0, 255, 153, 0.25);
    border-radius: 4px;
    padding: 0.3rem 0.6rem;
    margin-top: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

# — Sidebar
session_tokens = int(st.session_state.get("total_tokens_used", 0))
session_cost = float(st.session_state.get("total_cost_usd", 0.0))
req_count = st.session_state.get("req_count", 0)
conflict_count = st.session_state.get("conflict_count", 0)
gap_count = st.session_state.get("gap_count", 0)

if os.getenv("GEMINI_API_KEY"):
    api_label, api_color = "Aktif — Gemini", "#00ff99"
elif os.getenv("DEEPSEEK_API_KEY"):
    api_label, api_color = "Aktif — DeepSeek", "#00ff99"
else:
    api_label, api_color = "Tanımsız", "#ff5252"

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
    <div class="ar-metrics-grid">
        <div class="ar-metric-box">
            <div class="ar-metric-val" style="color:#00ff99">{req_count}</div>
            <div class="ar-metric-key">Gereksinim</div>
        </div>
        <div class="ar-metric-box">
            <div class="ar-metric-val" style="color:#ff5252">{conflict_count}</div>
            <div class="ar-metric-key">Çelişki</div>
        </div>
        <div class="ar-metric-box">
            <div class="ar-metric-val" style="color:#f5a623">{gap_count}</div>
            <div class="ar-metric-key">Eksiklik</div>
        </div>
    </div>
</div>

<div style="border-top:1px solid #1a1a1a;margin:0.875rem 0 0.625rem;"></div>
""", unsafe_allow_html=True)

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
        '<div style="width:5px;height:5px;background:#00ff99;border-radius:50%;"></div>'
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

"""
app.py — Ana Uygulama Modülü
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
AutoReq sisteminin merkezi giriş noktasıdır. core, modules, outputs ve ui
modülleri bu dosya üzerinden entegre edilir. Uygulama `streamlit run app.py`
komutu ile başlatılır.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from ui.state import init_state

# Çevresel değişkenleri yükle (.env dosyasını oku)
load_dotenv()

st.set_page_config(
    page_title="AutoReq",
    layout="wide",
)

init_state()

# Özel Profesyonel CSS (VIP & Minimalist Esintiler)
st.markdown("""
    <style>
    /* Global Background and Typography */
    .stApp {
        background-color: #0E1117;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Elegant Headings */
    h1, h2, h3 {
        color: #F8F9FA !important;
        font-weight: 300 !important;
        letter-spacing: 0.5px;
    }
    
    /* Primary Accent Color (Subtle Gold/Champagne) */
    .stButton>button {
        background-color: transparent !important;
        color: #D4AF37 !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 4px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #D4AF37 !important;
        color: #121212 !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        color: #D4AF37;
        font-size: 1.8rem;
    }
    
    /* Status UI */
    .stAlert {
        border-radius: 4px;
        border-left: 3px solid #D4AF37;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Proje Durumu
st.sidebar.title("Sistem Durumu")

if os.getenv("GEMINI_API_KEY"):
    st.sidebar.markdown("**API Durumu:** Aktif")
else:
    st.sidebar.warning("API Key tanımsız — Gelişmiş analiz devre dışı")

session_tokens = int(st.session_state.get("total_tokens_used", 0))
session_cost = float(st.session_state.get("total_cost_usd", 0.0))
st.sidebar.markdown(
    f"**Maliyet:** ${session_cost:.2f} ({session_tokens} token)"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Analiz Özeti")
col1, col2, col3 = st.sidebar.columns(3)
col1.metric("Gereksinim", st.session_state.req_count)
col2.metric("Çelişki", st.session_state.conflict_count)
col3.metric("Eksiklik", st.session_state.gap_count)

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
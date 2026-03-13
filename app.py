"""
app.py — Ana Uygulama Modülü
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
AutoReq sisteminin merkezi giriş noktasıdır. core, modules, outputs ve ui 
modülleri bu dosya üzerinden entegre edilir. Uygulama `streamlit run app.py` 
komutu ile başlatılır.
"""

import streamlit as st

st.set_page_config(
    page_title="AutoReq – Gereksinim Analizörü",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 AutoReq")
st.subheader("Otomatik Yazılım Gereksinim Analizörü")
st.info("Proje geliştirme aşamasındadır. Modüller entegre edildikçe bu ekran güncellenecektir.")

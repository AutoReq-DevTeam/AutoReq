"""
app.py — Sistemin Ana Şalteri
Sahibi: Üye 1 (Metin Hazırlık) / Scrum Master

Senin Görevin:
Burası arabanın kontağıdır. Ekipteki herkes kendi parçalarını (motor, tekerlek, direksiyon) ayrı ayrı dosyalarda yaptı.
Şimdi `app.py` içinde o dosyaları (core, modules, outputs, ui) çağırıp birbirine bağlayacaksın.
Program `streamlit run app.py` denilerek buradan çalışmaya başlayacak.

Çıktı: "Tüm sistemi başlatan ve birbirine bağlayan ana motor kodu."
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

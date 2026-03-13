"""
ui/dashboard.py — Ana Kullanıcı Arayüzü
Sorumlu: Agid Gülsever

Açıklama:
AutoReq sisteminin ana giriş ekranıdır. Kullanıcı metin girişi, analiz tetikleme 
ve işlem durumu takibi süreçlerini yönetir.
"""

import streamlit as st


def render_dashboard():
    """Ana giriş ekranını render eder."""
    st.header("📄 Gereksinim Metni Gir")

    user_text = st.text_area(
        label="Müşteri gereksinimleri",
        placeholder="Örn: Kullanıcı sisteme giriş yapabilmelidir. Sistem hızlı çalışmalıdır...",
        height=300,
        key="requirement_input",
    )

    analyze_btn = st.button("🔍 Analiz Et", type="primary", use_container_width=True)

    # TODO: Üye 4 — Analiz butonuna tıklandığında core.preprocessor'ı çağır
    # TODO: Üye 4 — st.progress() ile işlem durumunu göster
    # TODO: Üye 4 — Sonucu session_state'e kaydet, results.py'ye yönlendir

    return user_text, analyze_btn

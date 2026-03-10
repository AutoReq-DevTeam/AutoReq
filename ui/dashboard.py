"""
ui/dashboard.py — Ana Giriş Ekranı (Vitrin)
Sahibi: Üye 4 (Arayüz ve Entegrasyon)

Senin Görevin:
Müşterinin/Kullanıcının uygulamayı açtığında göreceği o şık, temiz ilk sayfayı yapmak.
Bu sayfada büyük bir metin kutusu olmalı ki adam projesini anlatsın.
Altında kalın harflerle dikkat çeken, tıklanabilir bir "Analiz Et" butonu olmalı.
Ve kullanıcı butona bastığında "Bekleyiniz, veriler işleniyor..." gibi havalı bir yüklenme çubuğu çıkmalı.

Çıktı: "İçine metin girilebilen, şık ve çalışan bir ana ekran."
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

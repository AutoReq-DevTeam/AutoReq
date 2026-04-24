"""
ui/dashboard.py — Ana Kullanıcı Arayüzü
Sorumlu: Agid Gülsever

Açıklama:
AutoReq sisteminin ana giriş ekranıdır. Kullanıcı metin girişi, analiz tetikleme
ve işlem durumu takibi süreçlerini yönetir.
"""

import os

import streamlit as st


def render_dashboard():
    """Ana giriş ekranını render eder.

    Döndürür:
        tuple[str, bool]: (kullanıcının girdiği metin, analiz butonuna basılıp basılmadığı)
    """
    st.title("🚀 AutoReq")
    st.subheader("Otomatik Yazılım Gereksinim Analizörü")
    st.info("Proje geliştirme aşamasındadır. Modüller entegre edildikçe bu ekran güncellenecektir.")

    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    if "analysis_report" not in st.session_state:
        st.session_state.analysis_report = None

    if "total_tokens_used" not in st.session_state:
        st.session_state.total_tokens_used = 0
    if "total_cost_usd" not in st.session_state:
        st.session_state.total_cost_usd = 0.0

    st.sidebar.title("📊 Proje Durumu")
    st.sidebar.success("Sistem aktif")
    st.sidebar.markdown("**Arayüz:** Hazır")
    st.sidebar.markdown("**Testler:** Çalışıyor")

    # API Key durumu göstergesi
    if os.getenv("GEMINI_API_KEY"):
        st.sidebar.markdown("✅ **API Key:** OK")
    else:
        st.sidebar.warning("❌ API Key tanımsız — LLM analizi devre dışı")

    session_tokens = int(st.session_state.total_tokens_used)
    session_cost = float(st.session_state.total_cost_usd)
    st.sidebar.markdown(
        f"**Bu oturumda harcanan:** ~**${session_cost:.2f}** (**{session_tokens}** token)"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📌 Demo", use_container_width=True):
            st.session_state.user_input = (
                "Kullanıcı sisteme kayıt olabilmeli.\n"
                "Şifresini sıfırlayabilmeli.\n"
                "Admin kullanıcıları yönetebilmeli."
            )
            st.toast("Demo metni yüklendi ✅")
            st.rerun()

    with col2:
        analyze_btn = st.button("🚀 Analiz Et", type="primary", use_container_width=True)

    user_text = st.text_area(
        label="Gereksinim metnini gir:",
        placeholder="Örnek: Kullanıcı sisteme giriş yapabilmeli. Şifresini unuttuğunda sıfırlayabilmeli.",
        height=220,
        key="user_input",
    )

    return user_text, analyze_btn
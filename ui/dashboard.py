"""
ui/dashboard.py — Ana Kullanıcı Arayüzü
Sorumlu: Agid Gülsever

Açıklama:
AutoReq sisteminin ana giriş ekranıdır. Kullanıcı metin girişi, analiz tetikleme
ve işlem durumu takibi süreçlerini yönetir.
"""

import os
from pathlib import Path

import streamlit as st


_SAMPLES_DIR = Path(__file__).parent.parent / "data" / "samples"

_SAMPLE_LABELS: dict[str, str] = {
    "ornek_eticaret.txt": "🛒 E-Ticaret",
    "ornek_bankacilik.txt": "🏦 Bankacılık",
    "ornek_egitim.txt": "🎓 Eğitim Platformu",
    "ornek_gereksinim.txt": "📝 Genel Örnek",
}


def _render_sample_loader() -> None:
    """data/samples/ klasöründeki .txt dosyalarını dropdown olarak sunar.

    Seçilen dosyanın içeriğini st.session_state.user_input alanına yükler.
    Dosya bulunamazsa uyarı gösterir.
    """
    sample_files = sorted(_SAMPLES_DIR.glob("*.txt")) if _SAMPLES_DIR.exists() else []

    if not sample_files:
        return

    options = {
        _SAMPLE_LABELS.get(f.name, f"📄 {f.stem}"): f
        for f in sample_files
    }
    label_list = ["— Örnek veri seç —"] + list(options.keys())

    selected_label = st.selectbox(
        "📂 Örnek Veri Yükle",
        label_list,
        index=0,
        key="sample_selector",
        help="data/samples/ klasöründen hazır gereksinim metinlerini yükleyin.",
    )

    if selected_label != "— Örnek veri seç —":
        sample_path = options[selected_label]
        try:
            content = sample_path.read_text(encoding="utf-8")
            if st.button(f"✅ '{selected_label}' dosyasını metin alanına yükle", key="load_sample_btn"):
                st.session_state.user_input = content
                st.toast(f"{selected_label} yüklendi ✅")
                st.rerun()
        except OSError:
            st.warning(f"'{sample_path.name}' dosyası okunamadı.")


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

    _render_sample_loader()

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
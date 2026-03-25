"""
app.py — Ana Uygulama Modülü
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
AutoReq sisteminin merkezi giriş noktasıdır. core, modules, outputs ve ui
modülleri bu dosya üzerinden entegre edilir. Uygulama `streamlit run app.py`
komutu ile başlatılır.
"""

import time
import streamlit as st

from core.models import AnalysisReport
from core.preprocessor import TextPreprocessor
from core.classifier import RequirementClassifier
from core.ner import EntityRecognizer


# Ağır NLP motorlarını belleğe kitler
@st.cache_resource
def load_nlp_pipeline():
    """
    Kullanıcı sayfayı her yenilediğinde baştan yüklenmesini ve uygulamanın donmasını engellemek için
    Stanza modellerini vs. belleğe bir kere yükler.
    """

    # fmt: off
    return {
        "preprocessor": TextPreprocessor(),
        "classifier": RequirementClassifier(),
        "ner": EntityRecognizer(),
    }
    # fmt: on


# Program başladığında modelleri çağırır ve hazır tutar
nlp_engines = load_nlp_pipeline()


def process_text(raw_text: str) -> AnalysisReport:
    """
    Ham metni alır ve tüm analiz sürecini baştan sona çalıştırır.
    """
    # 1. Ön İşleme
    parsed_doc = nlp_engines["preprocessor"].process(raw_text)

    # parsed_doc.requirements listesi üzerinde döngü
    for req in parsed_doc.requirements:
        # 2. Sınıflandırma
        req = nlp_engines["classifier"].classify(req)

        # 3. Varlık Çıkarımı (NER)
        req = nlp_engines["ner"].recognize(req)

    # 4. Rapor Oluşturma
    # fmt: off
    report = AnalysisReport(
        parsed_doc=parsed_doc,
        conflicts=[],
        gaps=[],
        improvements=[]
    )
    # fmt: on

    return report


# --- UI KISMI ---
st.set_page_config(
    page_title="AutoReq – Gereksinim Analizörü",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 AutoReq")
st.subheader("Otomatik Yazılım Gereksinim Analizörü")
st.info("Proje geliştirme aşamasındadır. Modüller entegre edildikçe bu ekran güncellenecektir.")

# Session state
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "analysis_report" not in st.session_state:
    st.session_state.analysis_report = None

# Sidebar
st.sidebar.title("📊 Proje Durumu")
st.sidebar.success("Sistem aktif")
st.sidebar.markdown("**Arayüz:** Hazır")
st.sidebar.markdown("**Testler:** Çalışıyor")

# Butonlar
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
    analyze_clicked = st.button("🚀 Analiz Et", use_container_width=True)

# Metin giriş alanı
st.text_area(
    "Gereksinim metnini gir:",
    key="user_input",
    height=220,
    placeholder="Örnek: Kullanıcı sisteme giriş yapabilmeli. Şifresini unuttuğunda sıfırlayabilmeli.",
)

# Analiz
if analyze_clicked:
    if not st.session_state.user_input.strip():
        st.error("Lütfen metin gir!")
    else:
        st.toast("Analiz başladı 🚀")

        with st.spinner("Analiz ediliyor..."):
            time.sleep(2)
            st.session_state.analysis_report = process_text(st.session_state.user_input)

        st.toast("Analiz tamamlandı ✅")

# Sonuçları göster
if st.session_state.analysis_report is not None:
    report = st.session_state.analysis_report
    requirements = report.parsed_doc.requirements

    tab1, tab2, tab3 = st.tabs(["📄 Özet", "📋 Gereksinimler", "⚙️ Teknik"])

    with tab1:
        st.subheader("Analiz Özeti")
        st.metric("Toplam Gereksinim", len(requirements))

        if requirements:
            st.success("Metin başarıyla işlendi ve gereksinimler ayrıştırıldı.")
        else:
            st.warning("Analiz tamamlandı ancak gereksinim listesi boş döndü.")

    with tab2:
        st.subheader("Ayrıştırılan Gereksinimler")

        if requirements:
            for i, req in enumerate(requirements, start=1):
                st.markdown(f"### 📌 Gereksinim {i}")
                st.info(str(req))
        else:
            st.warning("Henüz ayrıştırılmış gereksinim bulunamadı.")

    with tab3:
        st.subheader("Teknik Detaylar")
        st.write("Çatışmalar:", report.conflicts)
        st.write("Eksikler:", report.gaps)
        st.write("İyileştirmeler:", report.improvements)
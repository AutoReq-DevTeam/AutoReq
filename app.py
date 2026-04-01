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
from ui.dashboard import render_dashboard
from ui.results import render_results


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

user_input, analyze_clicked = render_dashboard()

if analyze_clicked:
    if not st.session_state.user_input.strip():
        st.error("Lütfen metin gir!")
    else:
        st.toast("Analiz başladı 🚀")

        with st.spinner("Analiz ediliyor..."):
            time.sleep(2)
            st.session_state.analysis_report = process_text(st.session_state.user_input)

        st.toast("Analiz tamamlandı ✅")

if st.session_state.get("analysis_report") is not None:
    render_results(st.session_state.analysis_report)
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


# Ağır NLP motorlarını belleğe kitler (Memoization / Caching)
@st.cache_resource
def load_nlp_pipeline():
    """
    Optimizasyon: Streamlit arayüzü her etkileşimde (buton tıklaması vb.) sayfa state'ini sıfırlayıp 
    kodları baştan okur. Stanza ve NLP pipeline'ları ağır yüklü (GB boyutunda) modeller olduğu için,
    @st.cache_resource dekoratörü kullanarak bellekte Singleton Pattern mantığı ile tutuyoruz. 
    Böylece modeller RAM'e sadece 1 kere yüklenir, gereksiz performans kaybı ve bellek şişmesi önlenir.
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
    Bu fonksiyon projenin Orkestrasyon (Orchestrator) merkezidir.
    Tıpkı bir fabrika bandı (Pipeline Pattern) gibi çalışır. Ham maddeyi (metni) alır, 
    sırasıyla preprocessor, classifier ve ner istasyonlarına göndererek analiz zincirini tamamlar. 
    Ön işleme ile Zeka katmanı arasındaki Low Coupling (Zayıf Bağlılık) prensibini güçlendirir.
    """
    # 1. İstasyon: Ön İşleme (Tokenization & Stopwords temizliği)
    parsed_doc = nlp_engines["preprocessor"].process(raw_text)

    # 2. İstasyonlara teker teker gereksinimler gönderilir
    for req in parsed_doc.requirements:
        # Sınıflandırma (FR / NFR)
        req = nlp_engines["classifier"].classify(req)
        # Varlık Çıkarımı (Aktör ve Nesneler)
        req = nlp_engines["ner"].recognize(req)

    # İşlem tamamlandığında 3. ekip (Eren/LLM) için hazırlanan DTO (Data Transfer nesnesi) döndürülür
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
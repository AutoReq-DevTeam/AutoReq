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
from loguru import logger

from core.models import AnalysisReport
from core.preprocessor import TextPreprocessor
from core.classifier import RequirementClassifier
from core.ner import EntityRecognizer
from modules.conflict_detector import ConflictDetector
from modules.gap_analyzer import GapAnalyzer
from modules.improver import RequirementImprover
from modules.llm_client import LLMClientError
from ui.dashboard import render_dashboard
from ui.results import render_results

_log = logger.bind(module="app")


# Ağır NLP motorlarını belleğe kitler (Memoization / Caching)
@st.cache_resource
def load_nlp_pipeline():
    """
    Optimizasyon: Streamlit arayüzü her etkileşimde (buton tıklaması vb.) sayfa state'ini sıfırlayıp 
    kodları baştan okur. Stanza ve NLP pipeline'ları ağır yüklü (GB boyutunda) modeller olduğu için,
    @st.cache_resource dekoratörü kullanarak bellekte Singleton Pattern mantığı ile tutuyoruz. 
    Böylece modeller RAM'e sadece 1 kere yüklenir, gereksiz performans kaybı ve bellek şişmesi önlenir.

    Not: TextPreprocessor ve EntityRecognizer artık paylaşılan bir Stanza pipeline kullanır
    (core/nlp_engine.py). Bu sayede bellek kullanımı ~yarıya iner.
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


def _is_llm_available() -> bool:
    """GEMINI_API_KEY ortam değişkeninin tanımlı olup olmadığını kontrol eder.

    Döndürür:
        bool: API key mevcutsa True, değilse False.
    """
    return bool(os.getenv("GEMINI_API_KEY"))


def process_text(raw_text: str) -> AnalysisReport:
    """
    Bu fonksiyon projenin Orkestrasyon (Orchestrator) merkezidir.
    Tıpkı bir fabrika bandı (Pipeline Pattern) gibi çalışır. Ham maddeyi (metni) alır, 
    sırasıyla preprocessor, classifier ve ner istasyonlarına göndererek analiz zincirini tamamlar.
    Ardından LLM modülleri (ConflictDetector, GapAnalyzer, RequirementImprover) ile çelişki,
    eksiklik ve iyileştirme analizlerini gerçekleştirir. LLM hata toleransı sayesinde API key
    eksikse veya LLM hatası oluşursa pipeline çökmeden devam eder.

    Parametreler:
        raw_text: Kullanıcıdan gelen ham gereksinim metni.

    Döndürür:
        AnalysisReport: NLP ve LLM analizleri tamamlanmış rapor nesnesi.
    """
    # 1. İstasyon: Ön İşleme (Tokenization & Stopwords temizliği)
    parsed_doc = nlp_engines["preprocessor"].process(raw_text)

    # 2. İstasyonlara teker teker gereksinimler gönderilir
    for req in parsed_doc.requirements:
        # Sınıflandırma (FR / NFR)
        req = nlp_engines["classifier"].classify(req)
        # Varlık Çıkarımı (Aktör ve Nesneler)
        req = nlp_engines["ner"].recognize(req)

    # 3. LLM Çelişki Analizi (ConflictDetector)
    conflicts = []
    if _is_llm_available():
        try:
            _log.info("LLM ile çelişki analizi başlatılıyor...")
            conflicts = ConflictDetector().analyze(parsed_doc)
            _log.info("Çelişki analizi tamamlandı | conflicts={}", len(conflicts))
        except (LLMClientError, ValueError) as exc:
            _log.warning("Çelişki analizi başarısız — boş liste ile devam ediliyor | hata={}", exc)
            conflicts = []
    else:
        _log.info("GEMINI_API_KEY tanımlı değil — çelişki analizi atlanıyor.")

    # 4. LLM Eksiklik Analizi (GapAnalyzer)
    gaps = []
    if _is_llm_available():
        try:
            _log.info("LLM ile eksiklik analizi başlatılıyor...")
            gaps = GapAnalyzer().analyze(parsed_doc)
            _log.info("Eksiklik analizi tamamlandı | gaps={}", len(gaps))
        except (LLMClientError, ValueError) as exc:
            _log.warning("Eksiklik analizi başarısız — boş liste ile devam ediliyor | hata={}", exc)
            gaps = []
    else:
        _log.info("GEMINI_API_KEY tanımlı değil — eksiklik analizi atlanıyor.")

    # 5. LLM Gereksinim İyileştirme (RequirementImprover)
    improvements = []
    if _is_llm_available():
        try:
            _log.info("LLM ile gereksinim iyileştirme başlatılıyor...")
            improver = RequirementImprover()
            for req in parsed_doc.requirements:
                result = improver.improve(req)
                # Yalnızca metni gerçekten değişen gereksinimleri ekle (UI gürültüsünü azaltır)
                if result.get("improved") != result.get("original"):
                    improvements.append(result)
            _log.info("Gereksinim iyileştirme tamamlandı | improvements={}", len(improvements))
        except (LLMClientError, ValueError) as exc:
            _log.warning("Gereksinim iyileştirme başarısız — boş liste ile devam ediliyor | hata={}", exc)
            improvements = []
    else:
        _log.info("GEMINI_API_KEY tanımlı değil — gereksinim iyileştirme atlanıyor.")

    # fmt: off
    report = AnalysisReport(
        parsed_doc=parsed_doc,
        conflicts=conflicts,
        gaps=gaps,
        improvements=improvements,
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

        with st.spinner("Stanza ile ön işleme yapılıyor..."):
            st.session_state.analysis_report = process_text(st.session_state.user_input)

        st.toast("Analiz tamamlandı ✅")

if st.session_state.get("analysis_report") is not None:
    render_results(st.session_state.analysis_report)
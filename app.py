"""
app.py — Ana Uygulama Modülü (Güvenli Versiyon)
"""

import os
import streamlit as st
from dotenv import load_dotenv  # Güvenlik için eklendi
from loguru import logger

# .env dosyasını yükle (API anahtarını buradan okuyacak)
load_dotenv()

from core.models import AnalysisReport
from core.preprocessor import TextPreprocessor
from core.classifier import RequirementClassifier
from core.ner import EntityRecognizer
from core.priority_detector import PriorityDetector
from modules.conflict_detector import ConflictDetector
from modules.gap_analyzer import GapAnalyzer
from modules.improver import RequirementImprover
from modules.llm_client import LLMClientError

from ui.dashboard import render_dashboard
from ui.results import render_results

# Çıktı Üreticiler
from outputs.story_generator import StoryGenerator
from outputs.srs_generator import generate_srs

_log = logger.bind(module="app")


# NLP modellerini cache'le
@st.cache_resource
def load_nlp_pipeline():
    return {
        "preprocessor": TextPreprocessor(),
        "classifier": RequirementClassifier(),
        "ner": EntityRecognizer(),
        "priority_detector": PriorityDetector(),
    }


nlp_engines = load_nlp_pipeline()


def _is_llm_available() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


def process_text(raw_text: str) -> AnalysisReport:
    parsed_doc = nlp_engines["preprocessor"].process(raw_text)

    for req in parsed_doc.requirements:
        req = nlp_engines["classifier"].classify(req)
        req = nlp_engines["ner"].recognize(req)
        req = nlp_engines["priority_detector"].detect(req)

    # 🔹 Conflict
    conflicts = []
    if _is_llm_available():
        try:
            conflicts = ConflictDetector().analyze(parsed_doc)
        except Exception:
            conflicts = []

    # 🔹 Gap
    gaps = []
    if _is_llm_available():
        try:
            gaps = GapAnalyzer().analyze(parsed_doc)
        except Exception:
            gaps = []

    # 🔹 Improvement
    improvements = []
    if _is_llm_available():
        try:
            improver = RequirementImprover()
            for req in parsed_doc.requirements:
                result = improver.improve(req)
                if result.get("improved") != result.get("original"):
                    improvements.append(result)
        except Exception:
            improvements = []

    report = AnalysisReport(
        parsed_doc=parsed_doc,
        conflicts=conflicts,
        gaps=gaps,
        improvements=improvements,
    )

    return report


# --- UI ---
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

        with st.spinner("Analiz yapılıyor..."):
            st.session_state.analysis_report = process_text(st.session_state.user_input)

        st.toast("Analiz tamamlandı ✅")

        # --- SRS ve User Story Üretimi ---
        try:
            with st.spinner("User Story ve SRS oluşturuluyor..."):
                generator = StoryGenerator()

                stories = generator.generate(
                    st.session_state.analysis_report,
                    language="en"
                )

                generate_srs(
                    st.session_state.analysis_report,
                    stories
                )

            st.success("SRS PDF başarıyla oluşturuldu 📄")

        except Exception as e:
            st.warning(f"SRS oluşturulamadı: {e}")


if st.session_state.get("analysis_report") is not None:
    render_results(st.session_state.analysis_report)